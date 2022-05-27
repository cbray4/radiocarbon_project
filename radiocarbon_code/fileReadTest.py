import os

sourceDir = "/project/arcc-students/cbray3/radiocarbon_text/raw_output/7-599/"

directory = os.fsencode(sourceDir)


for file in os.listdir(directory):
	filename = os.fsdecode(file)
	if filename.endswith(".txt"):
		#open file and read line by line and check for shit
		readFile = open(sourceDir+filename, 'r')
		linesOfText = readFile.readlines()
		counter = 2
		print(repr(filename))
		for line in linesOfText:
			if counter == 0:
				break
			line = line.rstrip()
			print(repr(line))
		counter -= 1
