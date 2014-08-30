#!/usr/bin/python
import sys
import os
import os.path
import csv
path=os.path.dirname(__file__)

with open (os.path.join(path, "etiquetastemplate.tex"), "r") as template:
    output=template.read()
users=""
reader=csv.DictReader(sys.stdin)
for row in reader:
    #print("asd{0}".format)
    users+="\\user{{{0} {1}}}{{{2}}}{{{3}}}\n".format(row['Nombre'],row['Apellido'], row['Username'], row['Password'])

print(output.replace("%USERS WILL GO HERE%", users, 1))
