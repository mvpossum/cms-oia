#!/usr/bin/python
from sys import argv,exit
import re
import os.path
import csv
from subprocess import call
import random

def genpass():
    #~ if len(argv)==4:
        #~ return argv[3]
    with open('wordlist.txt', 'r') as wordfile:
        words=[s.strip() for s in wordfile.read().split('\n') if s.strip()]
    pw_length = 3
    return '.'.join([words[random.randrange(len(words))] for _ in range(pw_length)])
    
if len(argv)!=3 and len(argv)!=4:
    print ("Adds usernames and passwords data\nUsage: {exe} form.csv output.csv [password]".format(exe=argv[0]))
    exit(1)
        
with open(argv[2], "w") as out:
    fieldnames = ['Nombre', 'Apellido', 'Username', 'Password']
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    reader=csv.DictReader(open(argv[1], "r"))
    for i,row in enumerate(reader):
        writer.writerow({'Nombre': row['Nombre'], 'Apellido': row['Apellido'], 'Username': row['Nivel']+row['Codigo']+str(i+1),'Password':  genpass() })
    
