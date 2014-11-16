"""Chipchart Database Construction Script

This script converts lists of album data, or URLs pointing at album data into a JSON database that
is utilized by the ChipChart album chart list system.  The formatting of the JSON produced by this 
script is geared to the format required by Datatables' AJAX database population methods.

Usage:
When running the script, all it needs is to be passed the directory that will house the album art
jpegs, and the database files to build the json from.

JSON format pulled from:  http://www.datatables.net/examples/ajax/custom_data_property.html
"""
from lxml import html
import requests
import json
import sys
import urllib
import os
import datetime
from datetime import date
import calendar
import re

usageString = "Usage: buildChartDB.py <directory containing data>"

#Dictionary for Date Lookups for the Bandcamp Scans
revMonthD = {v: k for k,v in enumerate(calendar.month_name)}

#The final output file being prepared
outData = []

#The list of files to utilize in building the output json
inputFiles = []

#Test to make sure we've got enough arguments
if len(sys.argv) != 2:
	print "Incorrect Number of Arguments."
	print usageString
	exit(0)

#Check that top level directory passed exists
if (os.path.isdir(sys.argv[1]) != 1):
	print "Argument for Top Level must be a directory."
	print usageString
	exit(0)

#Check that Database directory exists.  Gotta have databases to have data.
if (os.path.isdir(sys.argv[1] + os.sep + "Database") != 1):
	print "Databases directory must exist."
	print usageString
	exit(0)
	
#Check that albumArt output directory exists, create it if it
#does not.
if (os.path.isdir(sys.argv[1] + os.sep + "images" + os.sep + "AlbumArt") != 1):
	print "Album Art Directory must exist."
	print usageString
	exit(0)

#Functionality to add -- get output file and all input files from the command line
for file in os.listdir(sys.argv[1] + os.sep + "Database" + os.sep + "Unprocessed"):
	#Yeah, this is bad design VF.  Its a stem to eventually expand into identification of our
	#different database sources to farm out to the appropriate methods.
	print file
	if(file.endswith(".json") != 1):
		print "Found non-final database"
		inputFiles.append(file)

#Begin opening the input files.  For now, just the first file.
with open (sys.argv[1] + os.sep + "Database" + os.sep + "Unprocessed" + os.sep + inputFiles[0],'r') as urlFile:
	for line in urlFile:
		entry = []
		#Get the raw HTML of the album's website
		albumURL = line.rstrip()
		#print "Querying " + albumURL
		try:
			page = requests.get(albumURL)
			tree = html.fromstring(page.text)

			#Grab the meta elements that describe the album and a link to its 
			#album art thumbnail
			descElem = tree.xpath('//meta[@name="Description"]')[0]
			albumArtElem = tree.xpath('//link[@rel="shortcut icon"]')[0]

			#Isolate the content of the description and the href of the album art
			fullDesc = descElem.get("content").splitlines()[1]
			#A thought here would be to download the image, and save it to a images folder in the Chipchart.
			albumArtLink = albumArtElem.get("href")
			
			#Useful bit of functionality.  Check to see if image already exists in our database.  If
			#not, download image.
			
			#Choose the filename based on Bandcamp's own filename system.
			fnStart = albumArtLink.rfind("/")
			#print fnStart
			#print albumArtLink[fnStart+1:]
			albumArtFileName = os.sep + "images" + os.sep + "AlbumArt" + os.sep + albumArtLink[fnStart+1:]
			if (os.path.isfile(sys.argv[1] + albumArtFileName) != 1):
				urllib.urlretrieve(albumArtLink, sys.argv[1] + albumArtFileName)

				#Split up the full description into title, artist, and release date
				descPortions = fullDesc.split(",")
				title =  descPortions[0].split(" by ")[0]
				artist = descPortions[0].split(" by ")[1]
				releaseDate =  descPortions[1].split("released ")[1]
				
				#Datatables uses javascript's built-in Date.parse() for parsing dates for sorting.
				#As such, we'll split up the string, convert Bandcamp's month string into digits,
				#and rebuild the string.
				
				#print releaseDate
				releaseDateChunks = re.split(u'\s|\u200b',releaseDate)
				#print releaseDateChunks
				#print type(int(releaseDateChunks[0]))
				#print type(revMonthD[releaseDateChunks[1]])
				#print type(int(releaseDateChunks[2]))
				dReleaseDate = date(int(releaseDateChunks[2]), revMonthD[releaseDateChunks[1]], int(releaseDateChunks[0]))
				#print dReleaseDate
				
				modReleaseDate = dReleaseDate.strftime("%d/%m/%y")
				#print modReleaseDate

				#Finally, build the addition for the ChipChart Array Element
				albumArtOut = "<a href='" + albumURL + "'><img title='" + title + "' src='./images/AlbumArt/" + albumArtLink[fnStart+1:] + "'></a>"
		
				entry.append(albumArtOut)
				entry.append(artist)
				entry.append(modReleaseDate)
				outData.append(entry)
		except:
			print "Some invalid data at:"
			print albumURL
			print "Continuing processing."
			
#Put together the final dictionary to play nicely with the formatting DataTables is expecting
outJSON = dict();
outJSON["chartData"] = outData

#Save and overwrite the previous .js array object
with open(sys.argv[1] +os.sep + "Database" + os.sep + "Processed" + os.sep + "chartList.json",'w') as outFile:
	json.dump(outJSON, outFile)