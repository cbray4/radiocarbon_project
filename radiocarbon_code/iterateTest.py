import os
rootdir = '/project/arcc-students/cbray3/radiocarbon_card_copies/ocr/'
outputDir = '/project/arcc-students/cbray3/radiocarbon_text/raw_output/'

for subdir, dirs, files in os.walk(rootdir):
    print("subdir="+subdir)
    print("dirs="+str(dirs))
    currentDir = os.path.basename(os.path.normpath(subdir))
    print(currentDir)
    actualOutput = outputDir + currentDir
    print(actualOutput)
    if currentDir == 'ocr':
        print("Skip this dir!")
    elif os.path.exists(actualOutput):
        print("this directory exists!")
    else:
        print(actualOutput+" does not exist!")
    for file in files:
        print(os.path.join(subdir, file))