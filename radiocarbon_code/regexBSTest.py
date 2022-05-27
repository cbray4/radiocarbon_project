import re

text = "This 12'24 is a 34 test string, have fun!"
latNum1 = re.search('\d+', text)
print(str(latNum1.end()) + " " + latNum1.group())

text = text[latNum1.end():]
print(text)
latNum2 = re.search('\d+|[xX]', text)
print(str(latNum2.end()) + " " + latNum2.group())

newText = "I"

if re.match('^[iI:;• ]*$', newText):
    #this is bad, throw it out
    print("oh noes bro that's a bad read.")
else:
    #this is good, keep doing stuff
    print("keep going dude this line is a-ok")