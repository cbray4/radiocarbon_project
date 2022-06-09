#this package is what reads the text from the OCRd pdfs
from pdfminer.high_level import extract_text

#this will let me interact with directories
#mainly so I can loop through all of the pdfs in a directory
import os

#this is regular expressions
import re

def readFile(file, sourceDir, outputDir):
	filename = os.fsdecode(file)
	if filename.endswith(".pdf"):
		#Extract text from file, then print a title to distinguish each file
		#finally print the actual extracted text
		text = extract_text(str(os.path.join(sourceDir, file)))
		#get rid of double spaces to make it easier to read
		text = re.sub(' +', ' ', text)

		#NOTE TO SELF: "w" means that if the file exists it will simply write over the whole thing
		#new output method: output each OCR into separate files
		outputFile = open(outputDir+"/"+filename[:len(filename)-4] + "_text.txt", 'w')
		outputFile.write(text)
		outputFile.close()

		#this prints everything into the console/into one file
		#print("FILENAME: " + filename + "\n")
		#print(text + "\n")	

#put the directories into strings so I can change them later if need be
sourceDir = '/project/arcc-students/cbray3/radiocarbon_card_copies/ocr/' 		#where the pdfs are stored
rootOutputDir = '/project/arcc-students/cbray3/radiocarbon_text/raw_output/'	#where the output should go

#get the directory for the pdfs as a var the os library can work with

#this counter keeps track of how many files it has gone through
#mostly so there can be any form of output
fileCounter = 0

skipFirst = 0

for subDir, dirs, files in os.walk(sourceDir):
	if skipFirst == 1:
		wantedDir = os.path.basename(os.path.normpath(subDir))
		outputDir = rootOutputDir + wantedDir	
		if not os.path.exists(outputDir):
			os.makedirs(outputDir)
		for file in files:
			readFile(file, subDir, outputDir)
			fileCounter += 1
	else:
		skipFirst = 1
		continue
	#End of file iterating
#End of directory iterating
print("Read through " + str(fileCounter) + " files.")
print("Files were read from " + sourceDir + ".")


#NOTES
#when looping through the files, I need the serial number
#luckily all the files have already been labled
#serialNo = filename[:len(filename)-4]
#basically just put this at the top of the output file