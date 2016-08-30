#!/usr/bin/python
from sys import argv,exit
import re
import os.path
import csv
from subprocess import call

if len(argv)!=3:
    print ("Creates a pdf with the labels\nUsage: {exe} users.csv output.tex".format(exe=argv[0]))
    exit(1)

with open (os.path.join(os.path.dirname(__file__), "templatelabels.tex"), "r") as tf:
    raw=tf.read()
[(head, tail)] = re.compile("(.*)%USERS_WILL_GO_HERE%(.*)", re.DOTALL).findall(raw)

with open(argv[2], "w") as out:
    out.write(head)
    reader=csv.DictReader(open(argv[1], "r"))
    for row in reader:
        out.write("\\user{{{0} {1}}}{{{2}}}{{{3}}}{{{4}}}\n\n".format(row['Nombre'], row['Apellido'], row['Nivel'], row['Username'], row['Password']))
    out.write(tail)

call(["pdflatex", argv[2]])
