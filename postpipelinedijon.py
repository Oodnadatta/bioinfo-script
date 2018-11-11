#! /usr/bin/env python3

import csv
import sys

if len(sys.argv) != 2:
	print('Usage: postpipelinedijon.py filename', file=sys.stderr)
	sys.exit(1)
with open(sys.argv[1], 'r') as tsvfile:
	tsvreader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
	#TODO : gérer les fichiers vides
	header = next(tsvreader)
	print(header)
	dictionnary = {columnname:columnnumber for columnnumber, columnname in enumerate(header)}
	print (dictionnary)
	#for row in tsvreader:
	#	print(row)
		
