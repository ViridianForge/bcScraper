"""Chipchart Database Construction Script

This script converts lists of album data, or URLs pointing at album data into a JSON database that
is utilized by the ChipChart album chart list system.  The formatting of the JSON produced by this 
script is geared to the format required by Datatables' AJAX database population methods.

JSON format pulled from:  http://www.datatables.net/examples/ajax/custom_data_property.html
"""
from lxml import html
import requests
import json
import sys

usageString = "Usage: buildChartDB.py <outputfile> <inputfile_1> ... <inputfile_n>"

#Storage for dump to json
outData = []

#The list of files to utilize in building the output json
inputFiles = []

#Test to make sure we've got enough arguments
if len(sys.argv) < 3:
	print "Not enough arguments."
	print usageString
	return

#The location to print the json built from the input data sources
try:
	outputFile = sys.argv[1]
except IndexError:
	print "No Output File Specified."
	print usageString
	return

#Functionality to add -- get output file and all input files from the command line
for arg in sys.argv[2:]:
	#Yeah, this is bad design VF.  Its a stem to eventually expand into identification of our
	#different database sources to farm out to the appropriate methods.
	inputFiles.append(arg)

#Begin opening the input files.  For now, just the first file.
with open (inputFiles[0],'r') as urlFile:
	for line in urlFile:
		entry = []
		#Get the raw HTML of the album's website
		albumURL = line.rstrip()
		print "Querying " + albumURL
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

			#Split up the full description into title, artist, and release date
			descPortions = fullDesc.split(",")
			title =  descPortions[0].split(" by ")[0]
			artist = descPortions[0].split(" by ")[1]
			releaseDate =  descPortions[1].split("released ")[1]

			#Finally, build the addition for the ChipChart Array Element
			albumArtOut = "<a href='" + albumURL + "'><img title='" + title + "' src='" + albumArtLink + "'></a>"
		
			entry.append(albumArtOut)
			entry.append(artist)
			entry.append(releaseDate)
			outData.append(entry)
		except:
			print "Some invalid data at:"
			print albumURL
			print "Continuing processing."
			
#Put together the final dictionary to play nicely with the formatting DataTables is expecting
outJSON = dict();
outJSON["chartData"] = outData

#Save and overwrite the previous .js array object
with open('./chartList.json','w') as outFile:
	json.dump(outJSON, outFile)