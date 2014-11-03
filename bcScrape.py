from lxml import html
import requests
import json

outData = []

with open ('./bcURLList.txt','r') as urlFile:
	lineNum=1
	for line in urlFile:
		entry = dict()
		#Add a comma after the previous data point if
		#we are not dealing with the first line
		#if lineNum != 1:
		#	outData+=','
		lineNum += 1
		#Get the raw HTML of the album's website
		albumURL = line.rstrip()
		print albumURL
		page = requests.get(albumURL)
		tree = html.fromstring(page.text)

		#Grab the meta elements that describe the album and a link to its 
		#album art thumbnail
		descElem = tree.xpath('//meta[@name="Description"]')[0]
		albumArtElem = tree.xpath('//link[@rel="shortcut icon"]')[0]

		#Isolate the content of the description and the href of the album art
		fullDesc = descElem.get("content").splitlines()[1]
		albumArtLink = albumArtElem.get("href")

		#Split up the full description into title, artist, and release date
		descPortions = fullDesc.split(",")
		title =  descPortions[0].split(" by ")[0]
		artist = descPortions[0].split(" by ")[1]
		releaseDate =  descPortions[1].split("released ")[1]

		#Finally, build the addition for the ChipChart Array Element
		albumArtOut = "<a href='" + albumURL + "'><img title='" + title + "' src='" + albumArtLink + "'></a>"
		
		entry["albumArt"] = albumArtOut
		entry["artist"] = artist
		entry["releaseDate"] = releaseDate
		#newDataLine = "['"+albumArtOut+"','"+artist+"','"+releaseDate+"']"
		outData.append(entry)

#print json.dumps(outData)
#Save and overwrite the previous .js array object
with open('./chartList.json','w') as outFile:
	json.dump(outData, outFile)

