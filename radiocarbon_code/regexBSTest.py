import re

text = "super lame laboratory ivic-768"
matchObject = re.search('[0-9a-z\-]+-(\d)+', text)
print(matchObject.group())

newText = "I"

if re.match('^[iI:;• ]*$', newText):
    #this is bad, throw it out
    print("oh noes bro that's a bad read.")
else:
    #this is good, keep doing stuff
    print("keep going dude this line is a-ok")