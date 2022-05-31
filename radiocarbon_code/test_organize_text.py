#import regular expressions, which are used a lot in this script
import re

#this'll let me iterate through all the text files in the raw_output directory
import os

#setup information variables (store info to print from txt files)
#all of these are the necessary info for the spreadsheet
location = ""
materialDated = ""
labName = ""
labNumber = ""
age = ""
ageSigma = ""
latitude = ""
longitude = ""
typeOfDate = ""
siteIdentifier = ""

ageAssigned = 0

#For these lists, add file names of items that are set as N/A
#i.e. if Age from 153_text is set as N/A, add 153 to ageList
#remember, the function is .append()
locationDict = {}
materialDatedDict = {}
labNameDict = {}
labNumberDict = {}
ageDict = {}
latLongDict = {}
typeOfDateDict = {}
siteIdentifieDict = {}

#--------------------
#     FUNCTIONS
#--------------------
def checkBadRead(text):
    #make sure to update this pattern with any other characters that show up
    if re.match('^[iI:;•%«■rm^!f* ]*$', text) and text != "\n":
        #this is bad, throw it out
        return 1
    else:
        #this is good, keep doing stuff
        return 0

def assignLocation(text):
    global location
    location = text

def assignMatDated(text):
    #matDated also doesn't have anything special. Assign as is
    global materialDated
    materialDated = text

def assignLabName(text, dataList):
    global labName
    possibleLabNum = re.search('[0-9a-zA-Z\-]+-(\d)+', text)
    if possibleLabNum != None:
        if 'labNumber' in dataList:
            dataList.remove('labNumber')
            assignLabNum(possibleLabNum.group())
        text = text.replace(possibleLabNum.group(), '')
    labName = text

def assignLabNum(text):
    #labNumber doesn't really have anything special for it, just assign it as is
    global labNumber
    labNumber = text

#PROBLEM
#If the age section has more than one line
#it does not get written correctly
#consider making a flag so that if this is called
#multiple times it only takes the first line given
def assignAge(text, dataList):
    global age, ageSigma, ageAssigned
    possibleLabNum = re.search('[0-9a-zA-Z\-]+-(\d)+', text)
    if possibleLabNum != None:
        if 'labNumber' in dataList:
            dataList.remove('labNumber')
            assignLabNum(possibleLabNum.group())
        text = text.replace(possibleLabNum.group(), '')
    if '±' in text and ageAssigned == 0:
        age, ageSigma = text.split('±')
        ageAssigned = 1
    elif '>' in text or '^' in text and ageAssigned == 0:
        age = text
        ageAssigned = 1
    elif ageAssigned == 0:
        age = "N/A"
        ageSigma = "N/A"
    return

def assignTypeOfDate(text):
    global typeOfDate
    if re.search('(geology)|(archaeology)|(paleontology)', text.lower()):
        typeOfDate = text
    else:
        typeOfDate = 'N/A'

def latLongFunc(text, isLong):
    #Here's the rundown on what all of this bs is doing
    #Using regex we search for numbers. Whenever we find numbers
    #we assign them to variables latNum/longNum
    #after the first number we have to take into account three cases;
    #1) there is only one number for lat/long
        #this happens when latNum2 = cardinal direction
        #if this is the case, set latMod accordingly
        #and set latNum2/3 = 0
    #2) there are two numbers for lat/long
        #this happens when latNum3 = cardinal direction
    #3) there are three numbers for lat/long
        #when this happens, we have to do one more search
        #for the cardinal direction
    #since there's these three cases we have to do a lot of wacky if statements
    #re.search() returns its own object type called matchObject
    #matchObject.group() returns the text that was matched in the given string
    #so that's why it is used when calculating the lat/long
    #this is also why when setting things to zero I use re.search()
            #maybe I should set these vars to just the .group() strings?
            #that would get rid of the need to re.search() 
            #for things that should = 0. Does it *need* to
            #be that little bit faster though? idk talk to Collin about it 
    #this is only my initial stab at it, so there is probably
    #a couple places where things can be improved but for now this works :)
    if isLong == 0:
        pattern = '[ns]'
        positiveDir = 'n'
        negativeDir = 's'
    else:
        pattern = '[ew]'
        positiveDir = 'e'
        negativeDir = 'w'

    num1 = re.search('\d+', text)
    if num1 != None:
        num2 = re.search('\d+|'+pattern, text[num1.end():])
        if num2.group()== positiveDir:
            modifier = 1
            num2 = re.search('0', '0')
            num3 = re.search('0', '0')
        elif num2.group() == negativeDir:
            modifier = -1
            num2 = re.search('0', '0')
            num3 = re.search('0', '0')
        else:
            num3 = re.search('\d+|'+pattern, text[num2.end()+num1.end():])
            if num3 != None:
                if re.match(pattern, num3.group()):
                    if num3.group() == positiveDir:
                        modifier = 1
                        num3 = re.search('0', '0')
                    else:
                        modifier = -1
                        num3 = re.search('0', '0')
                else:
                    modText = re.search(pattern, text[num3.end():])
                    if modText.group() == negativeDir:
                        modifier = -1
                    else:
                        modifier = 1
            else:
                num3 = re.search('0', '0')
                modifier = 1
        result = str((int(num1.group()) + int(num2.group())/60.0 + int(num3.group())/3600.0) * modifier)
    else:
        result = "N/A"
    return result

def assignLatLong(text):
    global latitude, longitude
    #FORMAT: Lat. ##°(##'##") x Long. ##°(##'##")
    #N = +, S = -
    #E = +, W = -

    #converting to lowercase makes if statements much easier to read
    #by allowing us to avoid checking for uppercase
    newText = str(text).lower()
    #splits the lat/long down the middle where the X is
    #means that we don't have to do weird substring stuff
    if 'x' in newText:
        latText, longText = newText.split('x',1) 
    else:
        latitude = "N/A"
        longitude = "N/A"
        return

    latitude = latLongFunc(latText, 0)
    longitude = latLongFunc(longText, 1)
    
    #Error NOTE Section:
        #use this to detail common errors you run into that we should fix :)
    #some of these have decimal numbers. Figure out how to account for that.

def getPercentage(num1, num2):
    return round(num1/num2 * 100, 2)

#--------------------
#       NOTES
#--------------------
#consider adding more attention to detail in the main code portion
#when assigning things. Does this line have lat/long in it? does it have
#the +- symbol? If so, then it is probably a different variable
#so you should call a different function
#   '[0-9a-z\-]+-(\d)+'
#   ^ regex pattern for lab numbers. 


#--------------------
#     CODE START
#--------------------
#Used to keep track of which piece of info we are on
#convenient chart below for reference
infoCounter = 0
#   0 : location
#   1 : materialDated
#   2 : labName
#   3 : labNumber
#   4 : age, ageSigma
#   5 : latitude, longitude
#   6 : typeOfDate

dataList = [
    'location',
    'materialDated',
    'labName',
    'labNumber',
    'age',
    'latLong',
    'typeOfDate',
    'siteIdentifier',
]

#used to calculate the percentage of files
#that have errors at the end of file reading
fileCounter = 0

#this is a flag used to make sure infoCounter
#does not go up after a line that is read from the
#holes on the sides of the images
badRead = 0

#setup directory variables
sourceDir = "/project/arcc-students/cbray3/radiocarbon_text/raw_output/7-599/"
outputDir = "/project/arcc-students/cbray3/radiocarbon_text/organized_output/7-599/"
directory = os.fsencode(sourceDir)


for file in os.listdir(directory):
    filename = os.fsdecode(file)

    #reset counters/flags here :)
    infoCounter = 0
    ageAssigned = 0
    dataList = [
    'location',
    'materialDated',
    'labName',
    'labNumber',
    'age',
    'latLong',
    'typeOfDate'
    ]

    if filename.endswith(".txt"):
        fileCounter += 1
        #open file and read line by line and check for stuff
        readFile = open(sourceDir+filename, 'r')
        linesOfText = readFile.readlines()

        for line in linesOfText:
            if checkBadRead(line) == 0:
                if line == '\n' and badRead == 0:
                    infoCounter += 1
                    continue
                elif badRead == 1:
                    badRead = 0
                    continue
                line = line.rstrip()

                #Begin checking for specific variables in each line
                if '±' in line or '>' in line:
                    if 'age' in dataList:
                        assignAge(line, dataList)
                        dataList.remove('age')
                elif re.search('(lat)|(long)', line.lower()) and 'latLong' in dataList:
                    assignLatLong(line)
                    dataList.remove('latLong')

#NOTE AREA
#so one problem I've run into is that if the order is messed up at all
#then the rest of the info gets ruined. So solve that.
#main idea is to check for the ones that are most likely to break
#(Age/LatLong) and have specific checks for their unique symbols
#Once they've been put in set a flag or increase infoCounter,
#something along those lines.
                if infoCounter == 0 and 'location' in dataList:
                    assignLocation(line)
                    dataList.remove('location')
                elif infoCounter == 1 and 'materialDated' in dataList:
                    assignMatDated(line)
                    dataList.remove('materialDated')
                elif infoCounter == 2 and 'labName' in dataList:
                    assignLabName(line, dataList)
                    dataList.remove('labName')
                elif infoCounter == 3 and 'labNumber' in dataList:
                    assignLabNum(line)
                    dataList.remove('labNumber')
                elif infoCounter == 4 and 'age' in dataList:
                    assignAge(line, dataList)
                    if age == "N/A":
                        ageDict[filename] = line
                    else:
                        dataList.remove('age')
                elif infoCounter == 5 and 'latLong' in dataList:
                    assignLatLong(line)
                    if latitude == "N/A" or longitude == "N/A":
                        latLongDict[filename] = line
                    else:
                        dataList.remove('latLong')
                elif infoCounter == 6 and 'typeOfDate' in dataList:
                    assignTypeOfDate(line)
                    if typeOfDate == "N/A":
                        typeOfDateDict[filename] = line
                else:
                    break
            else:
                badRead = 1
                continue
        #End Of File Read

        #Begin Writing To Text Files
        orgOutputFile = open(outputDir+filename[:len(filename)-4]+"_organized.txt", 'w')
        orgOutputFile.write("Location: " + location)
        orgOutputFile.write("\n\nMaterial Dated: " + materialDated)
        orgOutputFile.write("\n\nLab Name: " + labName)
        orgOutputFile.write("\nLab Number: " + labNumber)
        orgOutputFile.write("\n\nAge: " + age)
        orgOutputFile.write("\nAge Sigma: " + ageSigma)
        orgOutputFile.write("\n\nLatitude: " + latitude)
        orgOutputFile.write("\nLongitude: " + longitude)
        orgOutputFile.write("\n\nType Of Date: " + typeOfDate)

#End Of Directory Reading

if len(ageDict) > len(latLongDict):
    largestFileError = len(ageDict)
else:
    largestFileError = len(latLongDict)
#print out the numbers/percentage of files that had errors in them
print("Percentage of files with errors: " + str(round(largestFileError/fileCounter * 100, 2)) + "%")
print("largestFileErrors = " + str(largestFileError))
print("fileCounter = " + str(fileCounter))

#Begin printing out the content of each error list
#be sure to update this whenever you add functionality
#to each list
#Print out the amount of files missing said data
#and the percentage.
print("\n***BEGIN ERROR LISTS***\n")
print("Files With Age Missing: " + str(len(ageDict)))
print("Percentage: " + str(getPercentage(len(ageDict), fileCounter)) + "%")
for file in ageDict:
    print(file, "->", ageDict[file])
print("\nFiles With Lat/Long Missing: " + str(len(latLongDict)))
print("Percentage: " + str(getPercentage(len(latLongDict), fileCounter)) + "%")
for file in latLongDict:
    print(file, "->", latLongDict[file])
print("\nFiles With Type Of Date Missing: " + str(len(typeOfDateDict)))
print("Percentage: " + str(getPercentage(len(typeOfDateDict), fileCounter)) + "%")
for file in typeOfDateDict:
    print(file, "->", typeOfDateDict[file])