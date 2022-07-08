#this function looks at last_organized_output.txt before it has been
#overwritten, and compares it to organized_output.txt, which now
#contains new output because it has been called before this script
#in the Slurm script.
#It will compare these two files line by line to see if any lines have been
#deleted or inserted. Useful for checking if anything is changing based on 
#changes in organize_text.py
def compareOldNewOutput(outputDir):
    #first, write to old file
    oldFile = open(outputDir+'WIP_last_organized_output.txt', 'r')
    newFile = open(outputDir+'WIP_organized_output.txt', 'r')

    oldLines = oldFile.readlines()
    newLines = newFile.readlines()

    deletedLines = []
    addedLines = []

    for line in oldLines:
        if line not in newLines:
            deletedLines.append(line)
    for line in newLines:
        if line not in oldLines:
            addedLines.append(line)

    print("\nDeleted Lines:")
    print("".join(deletedLines))
    print("\n\nAdded Lines:")
    print("".join(addedLines))

    oldFile.close()
    newFile.close()

#Before making any changes to the output file
#write it out to last_organized_output.txt, which
#will allow us to compare what has changed.
def overwriteOldOutput(outputDir): 
    oldFile = open(outputDir+'WIP_last_organized_output.txt', 'w')
    newFile = open(outputDir+'WIP_organized_output.txt', 'r')

    for line in newFile:
        oldFile.write(line)

    oldFile.close()
    newFile.close()

#Consider not reading the lines that simply reference the amount of files?
#I'm really only looking for files that are added/deleted. 

directory = "/project/arcc-students/cbray3/radiocarbon_text/organized_output/"

compareOldNewOutput(directory)
overwriteOldOutput(directory)