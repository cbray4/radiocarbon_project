#import regular expressions, which are used a lot in this script
import re

#this'll let me iterate through all the text files in the raw_output directory
import os

from itertools import chain
#global variable to make sure that the age only reads in the first line
ageAssigned = 0
#used in assignAge() to tell it to take the next line
#(after reading in Older than) and setting that as age
olderCheck = 0


#--------------------
#     FUNCTIONS
#--------------------
def checkBadRead(text):
    #make sure to update this pattern with any other characters that show up
    if re.match('^[19sligejromtnkAHMWOVPQTI.:;•%«»<>%*►■♦§°®^“’‘\'|!f*/#_„,\-—( ]*$', text) and text != "\n":
        #this is bad, throw it out
        return 1
    else:
        #this is good, keep doing stuff
        return 0

def assignLocation(text):
    return text + " "

def assignMatDated(text):
    #matDated also doesn't have anything special. Assign as is
    return text

def assignLabName(text, dataList):
    #this check was added since labNumber is commonly read
    #on the same line as the labName (or age)
    #if a match is found and labNumber hasn't already
    #been assigned something, get that part of the string out
    #and assign labNumber
    possibleLabNum = re.search('[0-9a-zA-Z\-()]+-(\d)+', text)
    if possibleLabNum != None:
        if 'labNumber' in dataList:
            dataList.remove('labNumber')
            assignLabNum(possibleLabNum.group())
        text = text.replace(possibleLabNum.group(), '')
    return text

def assignLabNum(text):
    #labNumber doesn't really have anything special for it, just assign it as is
    return text

#PROBLEM
#If the age section has more than one line
#it does not get written correctly
#consider making a flag so that if this is called
#multiple times it only takes the first line given
def assignAge(text, dataList):
    global ageAssigned, olderCheck

    #this check was added since labNumber is commonly read
    #on the same line as the age (or labName)
    #if a match is found and labNumber hasn't already
    #been assigned something, get that part of the string out
    #and assign labNumber
    checkText = text.replace(' ', '')

    possibleLabNum = re.search('[0-9a-zA-Z\-()]+-(\d)+', checkText)
    if possibleLabNum != None:
        if 'labNumber' in dataList:
            dataList.remove('labNumber')
            assignLabNum(possibleLabNum.group())
        text = text.replace(possibleLabNum.group(), '')

    if olderCheck == 1:
        return text, ""

    if '±' in text:
        ageAssigned = 1
        return text.split('±', 1)
    elif '+' in text:
        ageAssigned = 1
        return text.split('+', 1)
    elif 'i' in text:
        if re.search('\d', text):
            ageAssigned = 1
            return text.split('i', 1)
        else:
            return "N/A", "N/A"
    elif '>' in text or '^' in text or '<' in text:
        ageAssigned = 1
        return text, "0"
    elif text.lower() == "modern" or 'contemporary' in text.lower():
        ageAssigned = 1
        return text, "0"
    elif re.search("(older than)|(at least)|(apparent age)", text.lower()):
        if text.lower() == "older than" or text.lower() == "apparent age":
            olderCheck = 1
            return "", ""
        else:
            return text, ""
    elif 'C14' in text or 'C13' in text:
        return "C14/C13, Fix Later", "DO NOT UPLOAD!"
    elif "yrs" in text or "yr" in text:
        return text, ""
    else:
        return "N/A", "N/A"
    

def assignTypeOfDate(text):
    text = text.replace(' ', '')
    if re.search('(geology)|(archaeology)|(archeology)|(paleontology)', text.lower()):
        return re.search('(geology)|(archaeology)|(archeology)|(paleontology)', text.lower()).group()
    if re.search('(oceanography)|(oceanographic)|(miscellaneous)|(gaspropor)|(geo[-]?che)|(geo[-]?phy)|(ethno)|(ground)|(atmo)', text.lower()):
        return "CANNOT UPLOAD " + text
    if "pollen dated" in text.lower() or "pollen-dated" in text.lower() or "pollen" in text.lower() or "dated" in text.lower():
        return " "
    else:
        return "N/A"

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
    #print(text) #DEBUG

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
        if num2 == None:
            return "numprob"
        if num2.group() == positiveDir:
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
                    if modText == None:
                        modifier = 1
                    else:
                        if modText.group() == negativeDir:
                            modifier = -1
                        else:
                            modifier = 1
            else:
                num3 = re.search('0', '0')
                modifier = 1
        result = str((int(num1.group()) + int(num2.group())/60.0 + int(num3.group())/3600.0) * modifier)
    else:
        result = "numprob"
    return result

def assignLatLong(text):
    #FORMAT: Lat. ##°(##'##") x Long. ##°(##'##")
    #N = +, S = -
    #E = +, W = -

    #converting to lowercase makes if statements much easier to read
    #by allowing us to avoid checking for uppercase
    newText = str(text).lower()
    newText = newText.replace(' ', '')
    #splits the lat/long down the middle where the X is
    #means that we don't have to do weird substring stuff
    if 'x' in newText and 'tx' not in newText:
        latText, longText = newText.split('x',1) 
    elif 'lon' in newText:
        latText, longText = newText.split('lon',1)
    elif 'unlocated' in newText or 'nolat' in newText:
        return "Unlocated", "Unlocated"
    elif 'nolocation' in newText or 'notgiven' in newText:
        return "Unlocated", "Unlocated"
    else:
        return "N/A", "N/A"

    latitude = latLongFunc(latText, 0)
    longitude = latLongFunc(longText, 1)
    
    return latitude, longitude

def getPercentage(num1, num2):
    return round(num1/num2 * 100, 2)

#This function is the template used for writing out errors to the output file
#simply replace relevantDict and varName with the right things and it works correctly
def writeToOutput(relevantDict, varName, fileCounter, file):
    print("\nFiles With " + varName + " Missing: " + str(len(relevantDict)))
    print("Percentage: " + str(getPercentage(len(relevantDict), fileCounter)) + "%")
    printDictionarySorted(relevantDict)

def numOfUniqueKeys(listOfDicts):
    keys = list(set(chain.from_iterable(sub.keys() for sub in listOfDicts)))
    return keys

def createMaterialsList():
    returnThisList = []

    #Open up the valid materials file and start reading in them lines
    matFile = open('valid_materials.txt', 'r')
    fileLines = matFile.readlines()

    #split the lines by : since that's on every single line
    #this will ensure that I get only the material part
    #not the numOfInstances part
    for line in fileLines:
        actualMat = line.split(':', 1)
        returnThisList.append(actualMat[0])

    matFile.close()
    return returnThisList

#Give this function a dictionary and it will print out
#a list of all the files missing things from that dictionary
def printListOfFiles(relevantDict):
    print("\n\n", len(relevantDict), "files in relevantDict are missing items")
    printDictionarySorted(relevantDict)

#
def addToPossibleMaterials(text):
    possibleFile = open("possible_materials.txt", 'w')
    possibleFile.write(text)
    possibleFile.close()

def printDictionarySorted(dict):
    newList = []
    for key in dict:
        newList.append(key)
    newList = sorted(newList)
    for key in newList:
        print(key, "->", dict[key])

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
    #'siteIdentifier',
]

#used to calculate the percentage of files
#that have errors at the end of file reading
fileCounter = 0

#this is a flag used to make sure infoCounter
#does not go up after a line that is read from the
#holes on the sides of the images
badRead = 0

#setup directory variables
sourceDir = "/project/arcc-students/cbray3/radiocarbon_text/raw_output/"
rootOutputDir = "/project/arcc-students/cbray3/radiocarbon_text/organized_output/"

#The necessary information that the database needs
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

#For these dictionaries, add file names of items that are set as N/A
#i.e. if Age from 153_text is set as N/A, add 153 to ageList
#remember, nameDict[file] = whatever is how you add new entries
locationDict = {}
materialDatedDict = {}
labNameDict = {}
labNumberDict = {}
ageDict = {}
latLongDict = {}
typeOfDateDict = {}
siteIdentifieDict = {}
latLongProblemDict = {}
cannotUploadList = {}

materialList = createMaterialsList()

skipFirst = 0

for subDir, dirs, files in os.walk(sourceDir):
    if skipFirst == 1:
        wantedDir = os.path.basename(os.path.normpath(subDir))
        outputDir = rootOutputDir + wantedDir + "/"
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        for file in files:
        #reset counters/flags here :)
            infoCounter = 0
            ageAssigned = 0
            olderCheck = 0
            skipPop = 0
            dataList = [
            'location',
            'materialDated',
            'labName',
            'labNumber',
            'age',
            'latLong',
            'typeOfDate'
            ]

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

            if file.endswith(".txt"):
                fileCounter += 1
                #open file and read line by line and check for stuff
                readFile = open(subDir+"/"+file, 'r')
                linesInFile = readFile.readlines()

                #print("beginning read of " + str(file)) #DEBUG

                for line in linesInFile:
                    if checkBadRead(line) == 0:
                        if line == '\n' and badRead == 0:
                            #print("infoCounter increased.") #DEBUG
                            if infoCounter == 7 or not dataList:
                                break
                            if skipPop == 0:
                                infoCounter += 1
                                dataList.pop(0)
                            else:
                                skipPop = 0
                            continue
                        elif badRead == 1:
                            badRead = 0
                            continue
                        line = line.rstrip()

                        #print(repr(line)) #DEBUG

                        if re.search('A *. *D *.', line):
                            continue

                        #Begin checking for specific variables in each line
                        #Double check how this is interacting with the infoCounter
                        #seriously I'm not entirely sure and I think that's
                        #the main problem at the moment.
                        if '±' in line or '>' in line or '<' in line or 'yr' in line or 'yrs' in line:
                            if 'age' in dataList:
                                age, ageSigma = assignAge(line, dataList)
                                if age == "N/A":
                                    ageDict[file] = line
                                else:
                                    skipPop = 1
                                    if infoCounter != 4:
                                        dataList.remove('age')
                                continue
                        elif re.search('[0-9a-zA-Z\-]+-(\d)+', line):
                            labNumber = assignLabNum(line)
                            if 'labNumber' in dataList:
                                dataList.remove('labNumber')
                            skipPop = 1
                            continue
                        elif re.search('(lat[^i])|(long)', line.lower()) and 'latLong' in dataList:
                            trimLine = line.replace(' ', '')
                            if 'long' not in trimLine.lower():
                                latitude = latLongFunc(trimLine, 0)
                                continue
                            elif 'lat' not in trimLine.lower():
                                longitude = latLongFunc(trimLine, 1)
                            else:
                                latitude, longitude = assignLatLong(trimLine)
                            if latitude == "N/A" or longitude == "N/A":
                                latLongDict[file] = line
                            if latitude == "numprob" or longitude == "numprob":
                                latLongProblemDict[file] = line
                            else:
                                skipPop = 1
                                dataList.remove('latLong')
                            continue
                        elif re.search('(geology)|(archaeology)|(paleontology)', line.lower()):
                            if 'typeOfDate' in dataList:
                                typeOfDate = assignTypeOfDate(line)
                                if typeOfDate == "N/A":
                                    typeOfDateDict[file] = line
                                else:
                                    if infoCounter != 6:
                                        skipPop = 1
                                    dataList.remove('typeOfDate')
                            continue
                        elif 'lab' in line.lower() or 'univ' in line.lower():
                            if 'labName' in dataList:
                                labName = assignLabName(line, dataList)
                                dataList.remove('labName')
                                skipPop = 1
                                continue
                        elif re.search('B *. *C *.', line) or re.search('liquid scin', line.lower()):
                            continue
                        elif 'corrected' in line.lower():
                            infoCounter -= 1
                            continue

        #NOTE AREA
        #so one problem I've run into is that if the order is messed up at all
        #then the rest of the info gets ruined. So solve that.
        #main idea is to check for the ones that are most likely to break
        #(Age/LatLong) and have specific checks for their unique symbols
        #Once they've been put in set a flag or increase infoCounter,
        #something along those lines.
                        if infoCounter == 0 and 'location' in dataList:
                            matLine = line.replace(' ', '').lower()
                            if matLine in materialList:
                                #print("material dated read in as location")
                                materialDated += assignMatDated(line) + " "
                            else:
                                location += assignLocation(line)
                        elif infoCounter == 1 and 'materialDated' in dataList:
                            matLine = line.replace(' ', '').lower()
                            if matLine in materialList:
                                materialDated += assignMatDated(line) + " "
                            else:
                                #print("location read in as material dated")
                                location += assignLocation(line)
                        elif infoCounter == 2 and 'labName' in dataList:
                            labName = assignLabName(line, dataList)
                        elif infoCounter == 3 and 'labNumber' in dataList:
                            labNumber = assignLabNum(line)
                        elif infoCounter == 4 and 'age' in dataList:
                            if ageAssigned == 1:
                                continue
                            age, ageSigma = assignAge(line, dataList)
                            if age == "N/A":
                                ageDict[file] = line
                            elif olderCheck == 1:
                                continue
                            elif "C14" in age:
                                cannotUploadList[file] = "C14/C13 Format, Fix Later"
                            #else:
                                #dataList.remove('age')
                        elif infoCounter == 5 and 'latLong' in dataList:
                            latitude, longitude = assignLatLong(line)
                            #If Lat and Long are separated onto two different lines
                            #some stuff needs to happen 
                            if latitude == "N/A" or longitude == "N/A":
                                latLongDict[file] = line
                            if latitude == "numprob" or longitude == "numprob":
                                latLongProblemDict[file] = line
                            #else:
                                #dataList.remove('latLong')
                        elif infoCounter == 6 and 'typeOfDate' in dataList:
                            typeOfDate = assignTypeOfDate(line)
                            if typeOfDate == "N/A":
                                typeOfDateDict[file] = line
                    else:
                        badRead = 1
                        continue
                #End Of File Read

            #print("end of reading file " + str(file)) #DEBUG

            if location == "":
                locationDict[file] = ""
            if materialDated == "":
                materialDatedDict[file] = ""
            if labName == "":
                labNameDict[file] = ""
            if labNumber == "":
                labNumberDict[file] = ""
            if age == "" and ageSigma == "":
                ageDict[file] = ""
            if latitude == "" or longitude == "":
                latLongDict[file] = ""
            if typeOfDate == "":
                typeOfDateDict[file] = ""
            if latitude == "Unlocated":
                cannotUploadList[file] = "Unlocated"
            if "CANNOT UPLOAD" in typeOfDate:
                cannotUploadList[file] = "Unsupported Date Type, " + typeOfDate

            #Call function to double check variables to make sure they aren't incorrect

            orgOutputFile = open(outputDir+file[:len(file)-4]+"_organized.txt", 'w')
            #Begin Writing To Text Files
            orgOutputFile.write("Location: " + location)
            orgOutputFile.write("\n\nMaterial Dated: " + materialDated)
            orgOutputFile.write("\n\nLab Name: " + labName)
            orgOutputFile.write("\nLab Number: " + labNumber)
            orgOutputFile.write("\n\nAge: " + str(age))
            orgOutputFile.write("\nAge Sigma: " + str(ageSigma))
            orgOutputFile.write("\n\nLatitude: " + latitude)
            orgOutputFile.write("\nLongitude: " + longitude)
            orgOutputFile.write("\n\nType Of Date: " + typeOfDate)
            orgOutputFile.close()
            readFile.close()
    else:
        skipFirst = 1
        continue
    #End Of Directory Reading

#NOTE CHANGE THIS TO ITERATE THROUGH THE WHOLE LIST
#THAT MEANS YOU NEED TO MAKE A LIST CONTAINING ALL THE DICTS
#THIS WOULD MAKE ITERATING THROUGH ALL OF THESE OTHER THINGS
#A LOT EASIER TOO. DO THAT ON MONDAY :)




listOfDicts = [
    locationDict,
    materialDatedDict,
    labNameDict,
    labNumberDict,
    ageDict,
    latLongDict,
    typeOfDateDict
]

listOfImportantDicts = [
    materialDatedDict,
    labNumberDict,
    ageDict,
    latLongDict,
    typeOfDateDict
]

maxError = 0
for item in listOfDicts:
    if len(item) > maxError:
        maxError = len(item)

uniqueCardErrors = numOfUniqueKeys(listOfDicts)
uniqueErrorsImportant = numOfUniqueKeys(listOfImportantDicts)

#print out the numbers/percentage of files that had errors in them
print("Percentage of files with errors: " + str(round(len(uniqueCardErrors)/fileCounter * 100, 2)) + "%")
print("Number Of Cards With Errors = " + str(len(uniqueCardErrors)))
print("Number Of Cards Missing Important Data =", len(uniqueErrorsImportant))
print("Data With Most Errors = " + str(maxError))
print("fileCounter = " + str(fileCounter))

#print numbers for each list at the top so it's easy to see changes
print("\nLocation Errors:", len(locationDict))
print("Material Dated Errors:", len(materialDatedDict))
print("Lab Name Errors:", len(labNameDict))
print("Lab Number Errors:", len(labNumberDict))
print("Age Errors:", len(ageDict))
print("Lat/Long Errors:", len(latLongDict))
print("Type Of Date Errors:", len(typeOfDateDict))

#Begin printing out the content of each error list
#be sure to update this whenever you add functionality
#to each list
#Print out the amount of files missing said data
#and the percentage.
print("\n***BEGIN ERROR LISTS***")
writeToOutput(ageDict, "Age", fileCounter, file)
writeToOutput(latLongDict, "Lat/Long", fileCounter, file)
writeToOutput(typeOfDateDict, "Type Of Date", fileCounter, file)

print("\n\n" + str(len(cannotUploadList))+" FILES CANNOT BE UPLOADED DUE TO DATABASE CONFLICTS :(")
printDictionarySorted(cannotUploadList)

print("\n\n" + str(len(latLongProblemDict)) + " FILES HAVE PROBLEMS WITH LAT/LONG NUMBERS :(")
printDictionarySorted(latLongProblemDict)

#DEBUG PRINTING SECTION
printListOfFiles(materialDatedDict)