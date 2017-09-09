#!/usr/bin/python
from sys import argv,exit
import re
import os.path
import csv
from subprocess import call
import os,errno

if len(argv)!=4:
    print ("Creates a pdf with the labels\nUsage: {exe} ContestName users.csv output.tex".format(exe=argv[0]))
    exit(1)
ContestName=argv[1]
UsersCsv=argv[2]
OutputName=argv[3]

with open (os.path.join(os.path.dirname(__file__), "templatelabels.tex"), "r") as tf:
    raw=tf.read()
raw = raw.replace("%CONTEST_NAME%", ContestName)
[(head, tail)] = re.compile("(.*)%USERS_WILL_GO_HERE%(.*)", re.DOTALL).findall(raw)

with open(OutputName, "w") as out:
    out.write(head)
    reader=csv.DictReader(open(UsersCsv, "r"))
    for row in reader:
        out.write("\\user{{{0} {1}}}{{{2}}}{{{3}}}{{{4}}}\n\n".format(row['Nombre'], row['Apellido'], row['Nivel'], row['Username'], row['Password']))
    out.write(tail)

call(["latexmk", "-pdf", OutputName])

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
basename = os.path.splitext(OutputName)[0]
for ext in ['log','fdb_latexmk', 'fls']:
    silentremove(basename+"."+ext)
