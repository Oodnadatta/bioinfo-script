#! /usr/bin/env python3

import csv
import sys

if len(sys.argv) != 2:
	print('Usage: postpipelinedijon.py filename', file=sys.stderr)
	sys.exit(1)
with open(sys.argv[1], 'r') as tsvfile:
	tsvreader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
	#TODO: support empty files
	header = next(tsvreader)
	print(header)
	#TODO: reprint header to be in tsv and not in csv
	dictionnary = {columnname:columnnumber for columnnumber, columnname in enumerate(header)}
	rows = []
	for row in tsvreader:
		rows.append(row)


		