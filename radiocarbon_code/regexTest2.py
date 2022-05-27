import re

text = '''Lat. 57’ 00' N x Long. 3’ 25' W'''
newText = str(text).lower()
latText, longText = newText.split('x')

latNum1 = re.search('\d+', latText)
latNum2 = re.search('\d+|[nNsS]', latText[latNum1.end():])
if str(latNum2.group()).lower() == 'n':
    latModifier = 1
    latNum2 = re.search('0', '0')
    latNum3 = re.search('0', '0')
elif latNum2.group() == 's' or latNum2.group() == 'S':
    latModifier = -1
    latNum2 = re.search('0', '0')
    latNum3 = re.search('0', '0')
else:
    latNum3 = re.search('\d+|[nNsSxX]', latText[latNum2.end()+latNum1.end():])
    if latNum3 != None:
        if re.match('[nNsSxX]', latNum3.group()):
            if latNum3.group() == 'n' or latNum3.group() == 'N' or latNum3.group() == 'x' or latNum3.group() == 'X':
                latModifier = 1
                latNum3 = re.search('0', '0')
            else:
                latModifier = -1
                latNum3 = re.search('0', '0')
        else:
            modText = re.search('[nNsSxX]', latText[latNum3.end():]).group
            if str(modText).lower() == 's':
                latModifier = -1
            else:
                latModifier = 1
    else:
        latNum3 = re.search('0', '0')
        latModifier = 1

latitude = str((int(latNum1.group()) + int(latNum2.group())/60.0 + int(latNum3.group())/3600.0) * latModifier)

longNum1 = re.search('\d+', longText)
longNum2 = re.search('\d+|[eEwW]', longText[longNum1.end():])
if str(longNum2.group()).lower() == 'e':
    longModifier = 1
    longNum2 = re.search('0', '0')
    longNum3 = re.search('0', '0')
elif str(longNum2.group()).lower() == 'w':
    longModifier = -1
    longNum2 = re.search('0', '0')
    longNum3 = re.search('0', '0')
else:
    longNum3 = re.search('\d+|[eEwW]', longText[longNum2.end()+longNum1.end():])
    if longNum3 != None:
        if re.match('[eEwW]', longNum3.group()):
            if str(longNum3.group()).lower() == 'e':
                longModifier = 1
                longNum3 = re.search('0', '0')
            else:
                longModifier = -1
                longNum3 = re.search('0', '0')
        else:
            modText = re.search('[eEwW]', longText[longNum3.end():])
            if str(modText).lower() == 'w':
                longModifier = -1
            else:
                longModifier = 1
    else:
        longNum3 = re.search('0', '0')
        longModifier = 1

longitude = str((int(longNum1.group()) + int(longNum2.group())/60.0 + int(longNum3.group())/3600.0) * longModifier)