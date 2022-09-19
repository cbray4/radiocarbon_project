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
#Global Variable for when longitude numbers
#show up on the next line
longNextLine = 0

#A list of words that the bad read regex
#mistakes for "bad" lines
validBadReadList = [
    "bone",
    "bones",
    "antler",
    "twigs",
    "treerings",
    "moss"
]

#--------------------
#     FUNCTIONS
#--------------------

#The OCR initially ran on the cards recognizes the hole punches
#as characters sometimes, so the regex in this function checks for 
#lines that follow the pattern. Most typically they come in the form
#of things like "I;:i" but sometimes they'll be read in as random symbols.
#A return value of 1 means that the line is "bad" and should be ignored
#A return value of 0 means that it's good
def checkBadRead(text):
    global validBadReadList
    if re.match('^[1479sligejromwtnkABHMWOVPQTI.:;•%«»<>%*►■♦§°®^“’‘\'|!f*/#_„,\-—( ]*$', text) and text != "\n":
        #sometimes the pattern above matches real words, often important words 
        #we need to search for. validBadReadList contains the most common of these
        #occurences, which we use to double check 
        text = text.rstrip()
        trimText = text.lower()
        trimText = trimText.replace(' ', '')
        if trimText in validBadReadList:
            return 0
        else:
            return 1
    else:
        #this is good, keep doing stuff
        return 0

#The four following functions originally had a lot more code in them
#but as methods changed, a lot of it was moved outside of these functions
#and into the main body of code so that I could access certain variables 
#more easily. They still exist in case I need to change things.
def assignLocation(text):
    return text + " "

def assignMatDated(text):
    return text + " "

def assignLabName(text):
    return text

def assignLabNum(text):
    return text

#Due to the large number of formats for ages, there are many
#checks within this function to ensure that variables are 
#assigned correctly. The typical format is ##±## yr(s)
#Split it at the ± symbol and assign accordingly. 
#Sometimes the symbol is read in as something else, so we
#make sure to check for those as well.
#Most of the other things are where words are used in place
#of symbols, or a card is stated to be "modern"
def assignAge(text):
    global ageAssigned, olderCheck

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
    
#Sorts through all the different types of dates
#and returns the correct CARD compliant type.
def assignTypeOfDate(text):
    text = text.replace(' ', '')
    if re.search('(geo[^r])|(oceanogra)', text.lower()):
        return "geological"
    elif re.search('(archaeology)|(paleontology)', text.lower()):
        return re.search('(archaeology)|(paleontology)', text.lower()).group()
    if re.search('(misc)|(gaspropor)|(ethno)|(atmo)', text.lower()):
        return "CANNOT UPLOAD " + text
    if "pollen dated" in text.lower() or "pollen-dated" in text.lower() or "pollen" in text.lower() or "dated" in text.lower():
        return " "
    else:
        return "N/A"

#Runs through the checking algorithm for lat/long
#isLong = 0 represents lat, isLong = 1 represents long
#this flag changes what cardinal directions to search for (ns or ew)
def latLongFunc(text, isLong):
    #Here's the rundown on what all of this is doing
    #Using regex we search for numbers. Whatever we find first
    #we assign to the variable num1
    #after the first number we have to take into account three cases;
    #1) there is only one number for lat/long
        #this happens when num2 = (ns or ew)
        #if this is the case, set modifier based on cardinal direction
        #and set num2/3 = 0
    #2) there are two numbers for lat/long
        #this happens when num3 = (ns or ew)
    #3) there are three numbers for lat/long
        #when this happens, we have to do one more search for ns or ew
    #since there's these three cases we have to do a lot of wacky if statements
    #NOTE: re.search() returns its own object type called matchObject
    #matchObject.group() returns the text that was matched in the given string
    #so that's why it is used when calculating the lat/long
    #this is also why when setting things to zero I use re.search()

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
    global longNextLine
    #FORMAT: Lat. ##°(##'##")(N/S) x Long. ##°(##'##")(E/W)
    #N = +, S = -
    #E = +, W = -

    #splits the lat/long down the middle where the X is
    #by doing this we can run the same algorithm on 
    #the two separate text areas, making the code take up less space
    #if the x isn't in there due to OCR problems check for
    #the long. Shortened to 'lon' in case OCR misses the g
    if 'x' in text and 'tx' not in text:
        latText, longText = text.split('x',1) 
    elif 'lon' in text:
        latText, longText = text.split('lon',1)
    else:
        return "N/A", "N/A"

    latitude = latLongFunc(latText, 0)
    longitude = latLongFunc(longText, 1)
    
    return latitude, longitude

#Used to display error percentages in the output
def getPercentage(num1, num2):
    return round(num1/num2 * 100, 2)

#This function is the template used for writing out all errors to the output file
#simply replace relevantDict and varName with what you want to be displayed
def writeToOutput(relevantDict, varName, fileCounter):
    print("\nFiles With " + varName + " Missing: " + str(len(relevantDict)))
    print("Percentage: " + str(getPercentage(len(relevantDict), fileCounter)) + "%")
    printDictionarySorted(relevantDict)

#Gets the actual amount of files that have errors
#instead of just adding the error numbers up
def numOfUniqueKeys(listOfDicts):
    keys = list(set(chain.from_iterable(sub.keys() for sub in listOfDicts)))
    return keys

#Reads through valid_materials.txt and appends the items to a list
#valid_materials contains a (hopefully) comprehensive list of materials
#that show up on the cards, so if a line has a material that is in this list
#then it is good to add onto the organized text files.
def createMaterialsList():
    returnThisList = []

    #Open up the valid materials file and start reading in thoses lines
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
#Usually used for debugging since writeToOutput is meant to 
#be more "permanent"
def printListOfFiles(relevantDict):
    print("\n\n", len(relevantDict), "files in relevantDict are missing items")
    printDictionarySorted(relevantDict)

#The order that the files are read does not follow
#any readily apparent pattern, so this sorts it in
#ascending order, lowest file number to highest
def printDictionarySorted(dict):
    newList = []
    for key in dict:
        newList.append(key)
    newList = sorted(newList)
    for key in newList:
        print(key, "->", dict[key])

#--------------------
#     CODE START
#--------------------

dataList = [
    'location',
    'materialDated',
    'labName',
    'labNumber',
    'age',
    'latLong',
    'typeOfDate',
    'siteName',
    'references'
]

#used to calculate the percentage of files
#that have errors at the end of file reading
fileCounter = 0

#this is a flag used to make sure infoCounter
#does not go up after a line that is read from the
#holes on the sides of the images
badRead = 0

#Originally used to prevent extra lines from being
#read in before I was getting the references
#since a lot of random lines were getting put into the location.
itemCounter = 0

#These two variables decide the directories that the script will read to
#and output to. Change these when testing new OCR or if you're on a different machine
sourceDir = "/project/arcc-students/cbray3/radiocarbon_text/raw_output/"
rootOutputDir = "/project/arcc-students/cbray3/radiocarbon_text/organized_output/"

#These are the data that will be uploaded to the CARD database
#All of these except for Location have key identifiers/patterns
#that make it "simple" to search for them in the text files.
location = ""
materialDated = ""
labName = ""
labNumber = ""
age = ""
ageSigma = ""
latitude = ""
longitude = ""
typeOfDate = ""
siteName = ""
references = ""

#These dictionaries are used to keep track of errors.
#Most commonly errors where a piece of data simply isn't found
#
locationDict = {}
materialDatedDict = {}
labNameDict = {}
labNumberDict = {}
ageDict = {}
latLongDict = {}
typeOfDateDict = {}
siteNameDict = {}
referencesDict = {}
#This dictionary is specifically for latLong lines
#where the OCR screwed up and put letters or symbols
#instead of numbers
latLongProblemDict = {}
#List of items that aren't compatible with the CARD database
#This means: Incompatible type of date or things with Lat/Long missing
cannotUploadList = {}

materialList = createMaterialsList()

#Was originally going to be used for certain edge cases
#such as lat/long being split up, or getting location
#removed from the dataList, but otherwise isn't used
lastDataRemoved = ""

#A list of common materials found on lines with a lab name
materialInLabNameList = [
    'organic material',
    'organic residue',
    'water',
    'carbonaceous residue',
    'charcoal and wood',
    'groundwater'
]

#it is easier to write a list then a long if statement
#with a lot of "or"s in it.
validAgeSearchList = [
    '±',
    '+',
    #'i',
    '>',
    '<',
    '^',
    '%',
    'yr', 
    'yrs',
    'c14',
    'c13',
    'modern',
    'contemporary',
    'older than',
    'at least',
    'apparent age'
]

#sometimes the 'yr' in above will match with actual words
#these are most of the instances that I spotted
invalidAgeSearchList = [
    'myrtle',
    'syria',
    'ayrshire',
    'pyramid',
    'lyropecten',
    'anadyr',
    'ingsmyr',
    'myren',
    'myra',
    'akureyri',
    'styria',
    'veyrins',
    'kyriat',
]

#somtimes these are put into the location variable
#we don't want these in the location variable
locationExclusionList = [
    "pollen-dated",
    "gas proportional",
    "gas geiger",
]

#this ensures that the directory reading
#for loop works correctly
skipFirst = 0

#I'll be honest I got this directory walking code from Stack Exchange
#https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
#Fairly certain this is the post I got it from.
#Since the card text is separated into separate subfolders based on number
#I have to be able to go through each of those, this for loop does that automatically
#subDir is basically each folder underneath sourceDir, the for loop iterates through
#these after each loop, automating the process instead of going through a list
#I do not think there is any specific pattern that it walks through the folders in
#files is all the files underneath each subDir, that's how we get the raw text files to read in
#dirs is not used, it's there to make sure the iteration works (I think)
for subDir, dirs, files in os.walk(sourceDir):
    if skipFirst == 1:
        #This grabs the subfolder name, for example
        #raw_output/7-599/ turns into just 7-599
        #attach that to our base output directory
        #and you are now under the right subfolder
        wantedDir = os.path.basename(os.path.normpath(subDir))
        outputDir = rootOutputDir + wantedDir + "/"
        #This only comes into play the first time you run this script
        #if outputDir does not exist, make the subfolder please
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        #Now that we are in a subfolder in our sourceDir
        #and outputDir, we can start going through the files
        for file in files:
            #reset counters/flags/variables here :)
            itemCounter = 0
            ageAssigned = 0
            olderCheck = 0
            longNextLine = 0
            lastDataRemoved = ""
            locationCounter = 0
            referenceCounter = 0
            skipPop = 0
            dataList = [
            'location',
            'materialDated',
            'labName',
            'labNumber',
            'age',
            'latLong',
            'typeOfDate',
            'siteName',
            'references'
            ]

            #Gotta make sure to reset these or else
            #you get data from previous cards being
            #put into cards read afterwards
            location = ""
            materialDated = ""
            labName = ""
            labNumber = ""
            age = ""
            ageSigma = ""
            latitude = ""
            longitude = ""
            typeOfDate = ""
            siteName = ""
            references = ""

            if file.endswith(".txt"):
                fileCounter += 1
                #open file and read in all the lines
                #the algorithm checks line by line, so 
                #we use a for loop to iterate through those
                readFile = open(subDir+"/"+file, 'r')
                linesInFile = readFile.readlines()

                #if the script is stopping for some unknown reason
                #use this statement to see which file it stops at
                #print("beginning read of " + str(file)) #DEBUG

                for line in linesInFile:
                    if checkBadRead(line) == 0:
                        if line == '\n' and badRead == 0:
                            #print("itemCounter increased.") #DEBUG
                            itemCounter += 1

                            #The script should stop either when the dataList has all 
                            #of its items removed, or too many lines have been read in
                            if len(dataList) == 0 or itemCounter == 12:
                                break
                            continue
                        #If we have a bad read, we just skip past that line
                        #typically because it is going to be a '\n' character
                        elif badRead == 1:
                            badRead = 0
                            continue
                        #We have to remove the pesky newline character
                        #off the ends of the lines, or else a lot of this
                        #algorithm just doesn't work (mainly string comparisons)
                        line = line.rstrip()
                        #print(repr(line)) #DEBUG

                        #There are certain lines that are just useless or we want to skip entirely
                        #These are where we check for them. For now we check for age lines
                        #that have "A.D." or "B.C.", we also check for "liquid scintilation"
                        #which kept getting put into the location. We don't want that
                        if re.search('(A *\. *D *\.)|(B *\. *C *\.)|(liquid scin)', line):
                            continue
                        #If I remember correctly these are extra info for certain fields that aren't
                        #necessary, so we just skip em'
                        elif 'corrected' in line.lower() or 'solid carbon' in line.lower():
                            skipPop = 1
                            continue
                        
                        
                        #Now is where we begin the search for data
                        #Each piece of data has symbols and formats we can
                        #search for using regular expressions or string matching
                        #so we just do a lot of that. If it doesn't match any of that
                        #it is most likely a location

                        #trimLine is used when we want to get rid of spaces
                        #a lot of the time the OCR goofs and adds spaces 
                        #in between letters where we don't want them, so
                        #we use trimLine to reduce the amount of errors that causes
                        trimLine = line.replace(' ', '')
                        trimLine = trimLine.lower()
                        lowerLine = line.lower()

                        #An explanation of these checks SHOULD be in the readme on github
                        if trimLine.lower() in materialList:
                            if 'materialDated' in dataList:
                                materialDated = assignMatDated(line)
                                dataList.remove('materialDated')
                                lastDataRemoved = 'materialDated'
                                skipPop = 1
                                continue
                        if re.search('(lab[^a]?)|(univ)|(u\.s\.)|(geol.sur)|(unit[^ed])|(packardinstrument)|(inst)|(div\.)', trimLine):
                            if 'labName' in dataList:
                                #Check for any materials that have been read in  
                                #the same line as the lab name
                                if 'materialDated' in dataList:
                                    if any(item in lowerLine for item in materialInLabNameList):
                                        tempRegexPattern = '(' + ')|('.join(materialInLabNameList) + ')'
                                        matInName = re.search(tempRegexPattern, lowerLine)
                                        materialDated = assignMatDated(matInName.group().capitalize())
                                        line = line.replace(matInName.group().capitalize(), '')
                                        dataList.remove('materialDated')

                                #Check for any lab numbers that have been read in 
                                #the same line as the lab name
                                possibleLabNum = re.search('[0-9a-zA-Z\-]{1,4}-(\d){1,4}', line)
                                if possibleLabNum != None:
                                    if 'labNumber' in dataList:
                                        dataList.remove('labNumber')
                                        labNumber = assignLabNum(possibleLabNum.group())
                                    line = line.replace(possibleLabNum.group(), '')

                                labName = assignLabName(line)
                                dataList.remove('labName')
                                lastDataRemoved = 'labName'
                                skipPop = 1
                                continue
                        if any(item in lowerLine for item in validAgeSearchList) and all(item not in lowerLine for item in invalidAgeSearchList):
                            if 'age' in dataList:
                                #this check was added since labNumber is commonly read
                                #on the same line as the age (or labName)
                                #if a match is found and labNumber hasn't already
                                #been assigned something, get that part of the string out
                                #and assign labNumber
                                possibleLabNum = re.search('[0-9a-zA-Z\-]{1,4}-(\d){1,4}', line)
                                if possibleLabNum != None:
                                    if 'labNumber' in dataList:
                                        dataList.remove('labNumber')
                                        labNumber = assignLabNum(possibleLabNum.group())
                                    line = line.replace(possibleLabNum.group(), '')

                                if ageAssigned == 1:
                                    continue
                                if '%' in line:
                                    age = "modern"
                                    ageSigma = "0"
                                    dataList.remove("age")
                                    continue
                                if "C14" in line or "C13" in line:
                                    cannotUploadList[file] = "C14/C13 Format, Fix Later"
                                    continue
                                if '<' in line or '^' in line or '>' in line:
                                    if not re.search('\d+', line):
                                        pass
                                    else:
                                        age, ageSigma = assignAge(line)
                                        if age == "N/A":
                                            ageDict[file] = line
                                        elif olderCheck == 1:
                                            continue
                                        else:
                                            skipPop = 1
                                            dataList.remove('age')
                                            lastDataRemoved = 'age'
                                        continue
                                else: 
                                    age, ageSigma = assignAge(line)
                                    if age == "N/A":
                                        ageDict[file] = line
                                    elif olderCheck == 1:
                                        continue
                                    else:
                                        skipPop = 1
                                        dataList.remove('age')
                                        lastDataRemoved = 'age'
                                    continue
                        if re.search('([0-9a-zA-Z\-]{1,4}-(\d){1,4})', trimLine):
                            if 'labNumber' in dataList:
                                labNumber = assignLabNum(line)
                                dataList.remove('labNumber')
                                lastDataRemoved = 'labNumber'
                                skipPop = 1
                                continue
                        if re.search('(lat[^i])|(long)|(unlocated)|(nolat)|(nolocation)|(notgiven)|(unknown)', trimLine):
                            if 'latLong' in dataList:
                                if re.search('(unlocated)|(nolat)|(nolocation)|(notgiven)|(unknown)', trimLine):
                                    latitude = "Unlocated"
                                    longitude = "Unlocated"
                                elif re.search('(lat)-+', trimLine):
                                    latitude = "Unlocated"
                                    longitude = "Unlocated"
                                elif 'lo' not in trimLine:
                                    latitude = latLongFunc(trimLine, 0)
                                    skipPop = 1
                                    continue
                                elif 'la' not in trimLine:
                                    longitude = latLongFunc(trimLine, 1)
                                    skipPop = 1
                                else:
                                    latitude, longitude = assignLatLong(trimLine)
                                if latitude == "N/A" or longitude == "N/A":
                                    latLongDict[file] = line
                                if latitude == "numprob" or longitude == "numprob":
                                    latLongProblemDict[file] = line
                                else:
                                    skipPop = 1
                                    dataList.remove('latLong')
                                    lastDataRemoved = 'latLong'
                                continue
                        if re.search('(geo[^r])|(archaeology)|(paleontology)|(oceano)|(misc)|(gaspropor)|(ethno)|(atmo)', trimLine):
                            if 'typeOfDate' in dataList:
                                typeOfDate = assignTypeOfDate(line)
                                if typeOfDate == "N/A":
                                    typeOfDateDict[file] = line
                                else:
                                    skipPop = 1
                                    dataList.remove('typeOfDate')
                                    lastDataRemoved = 'typeOfDate'
                            continue
                        if (":" in line or ";" in line) and len(dataList) <= 3:
                            if 'siteName' in dataList:
                                if ":" in line:
                                    siteName, uselessForNow = line.split(':', 1)
                                if ";" in line:
                                    siteName, uselessForNow = line.split(';', 1)
                                if siteName.lower() in materialList:
                                    siteName = "Material In Place Of Identifier"
                                dataList.remove('siteName')
                                dataList.remove('location')
                                continue
                        if re.search('(volume)|(pg)|(p\.)|(radiocarbon)|(journal)|(press)', trimLine):
                            if "references" in dataList:
                                if re.search('inc', trimLine):
                                    continue
                                references += line + "; "
                                referenceCounter += 1
                                if referenceCounter >= 2:
                                    dataList.remove("references")
                                    lastDataRemoved = "references"
                                continue

                        #If the last dataList entry is removed we 
                        #should stop reading through the file
                        if not dataList:
                            break
                        else:
                            currentData = dataList[0]

                        #more likely than not location is going to be at the top of the dataList
                        #so anything that doesn't match with the above is going into location
                        if currentData == 'location':
                            if locationCounter < 4 and len(line) <= 30 and all(item not in lowerLine for item in locationExclusionList):
                                location += assignLocation(line)
                                locationCounter += 1
                        elif currentData == 'materialDated':
                            materialDatedDict[file] = line + " currentData Error"
                        elif currentData == 'labName':
                            labNameDict[file] = line + " currentData Error"
                        elif currentData == 'labNumber':
                            labNumberDict[file] = line + " currentData Error"
                        elif currentData == 'age':
                            ageDict[file] = line + " currentData Error"
                            if age == "N/A" or ageSigma == "N/A":
                                ageDict[file] = line + " currentData Error"
                        elif currentData == 'latLong':
                            latLongDict[file] = line + " currentData Error"
                        elif currentData == 'typeOfDate':
                            #typeOfDate = assignTypeOfDate(line)
                            typeOfDateDict[file] = line + " currentData Error"
                            if typeOfDate == "N/A":
                                typeOfDateDict[file] = line + " currentData Error"
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
            if siteName == "":
                siteNameDict[file] = ""
            if references == "":
                referencesDict[file] = ""

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
            orgOutputFile.write("\n\nSite Name: " + siteName)
            orgOutputFile.write("\n\nReferences: " + references)
            orgOutputFile.close()
            readFile.close()
    else:
        skipFirst = 1
        continue
    #End Of Directory Reading

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
print("Site Name Errors:", len(siteNameDict))
print("References Errors: ", len(referencesDict))

#Begin printing out the content of each error list
#be sure to update this whenever you add functionality
#to each list
#Print out the amount of files missing said data
#and the percentage.
print("\n***BEGIN ERROR LISTS***")
writeToOutput(materialDatedDict, "Material Dated", fileCounter)
writeToOutput(ageDict, "Age", fileCounter)
writeToOutput(latLongDict, "Lat/Long", fileCounter)
writeToOutput(typeOfDateDict, "Type Of Date", fileCounter)
writeToOutput(siteNameDict, "Site Name", fileCounter)
writeToOutput(referencesDict, "References", fileCounter)

print("\n\n" + str(len(cannotUploadList))+" FILES CANNOT BE UPLOADED DUE TO DATABASE CONFLICTS :(")
printDictionarySorted(cannotUploadList)

print("\n\n" + str(len(latLongProblemDict)) + " FILES HAVE PROBLEMS WITH LAT/LONG NUMBERS :(")
printDictionarySorted(latLongProblemDict)

#DEBUG PRINTING SECTION
