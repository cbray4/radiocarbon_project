#import regular expressions, which are used a lot in this script
import re

#this'll let me iterate through all the text files in the raw_output directory
import os
from unittest import result

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
#Other Variables
infoCounter = 0
#   0 : location
#   1 : materialDated
#   2 : labName
#   3 : labNumber
#   4 : age, ageSigma
#   5 : latitude, longitude
#   6 : typeOfDate

#--------------------
#     FUNCTIONS
#--------------------
def checkBadRead(text):
    if re.match('^[iI:;•% ]*$', text) and text != "\n":
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

def assignLabName(text):
    global labName
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
def assignAge(text):
    global age, ageSigma
    if '±' in text:
        age, ageSigma = text.split('±')
    else:
        age = "N/A"
        ageSigma = "N/A"
    return

def assignTypeOfDate(text):
    global typeOfDate
    typeOfDate = text

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
        pattern = '[nsx]'
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
                    if num3.group() == positiveDir or num3.group() == 'x':
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
        latText, longText = newText.split('x') 
    else:
        latitude = "N/A"
        longitude = "N/A"
        return

    latitude = latLongFunc(latText, 0)
    longitude = latLongFunc(longText, 1)
    
    #Error NOTE Section:
        #use this to detail common errors you run into that we should fix :)
    #some of these have decimal numbers. Figure out how to account for that.

def assignTypeOfDate(text):
    global typeOfDate
    typeOfDate = text

#--------------------
#       NOTES
#--------------------
#consider adding more attention to detail in the main code portion
#when assigning things. Does this line have lat/long in it? does it have
#the +- symbol? If so, then it is probably a different variable
#so you should call a different function

#--------------------
#     CODE START
#--------------------
#this is a flag used to make sure infoCounter
#does not go up after a line that is read from the
#holes on the sides of the images
badRead = 0
#setup directory variables
sourceDir = "/project/arcc-students/cbray3/radiocarbon_text/raw_output/26000-26999/"
outputDir = "/project/arcc-students/cbray3/radiocarbon_text/organized_output/26000-26999/"
directory = os.fsencode(sourceDir)


for file in os.listdir(directory):
    filename = os.fsdecode(file)
    print("Reading New File, " + filename)#DEBUG
    infoCounter = 0
    if filename.endswith(".txt"):
        #open file and read line by line and check for stuff
        readFile = open(sourceDir+filename, 'r')
        linesOfText = readFile.readlines()

        for line in linesOfText:
            if checkBadRead(line) == 0:
                print(repr(line))
                if line == '\n' and badRead == 0:
                    print("infoCounter has been increased.")
                    infoCounter += 1
                    continue
                elif badRead == 1:
                    badRead = 0
                    continue
                line = line.rstrip()

#NOTE AREA
#so one problem I've run into is that if the order is messed up at all
#then the rest of the info gets ruined. So solve that.
#main idea is to check for the ones that are most likely to break
#(Age/LatLong) and have specific checks for their unique symbols
#Once they've been put in set a flag or increase infoCounter,
#something along those lines.
                if infoCounter == 0:
                    assignLocation(line)
                elif infoCounter == 1:
                    assignMatDated(line)
                elif infoCounter == 2:
                    assignLabName(line)
                elif infoCounter == 3:
                    assignLabNum(line)
                elif infoCounter == 4:
                    assignAge(line)
                elif infoCounter == 5:
                    assignLatLong(line)
                elif infoCounter == 6:
                    assignTypeOfDate(line)
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
        print("Finished Writing To File\n\n")

#End Of Directory Reading