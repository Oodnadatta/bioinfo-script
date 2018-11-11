#! /usr/bin/env python3

import csv
import sys

if len(sys.argv) != 3:
	print('Usage: postpipelinedijon.py inputfilename.tsv outputfilename.tsv', file=sys.stderr)
	sys.exit(1)
with open(sys.argv[1], 'r', newline='') as inputtsvfile:
	tsvreader = csv.reader(inputtsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
	#TODO: support empty files
	header = next(tsvreader)
	#TODO: reprint header to be in tsv and not in csv
	dictionnary = {columnname:columnnumber for columnnumber, columnname in enumerate(header)}
	rows = []
	for row in tsvreader:
		rows.append(row)

with open(sys.argv[2], 'w', newline='') as outputtsvfile:
	tsvwriter = csv.writer(outputtsvfile, delimiter='\t')
	tsvwriter.writerow(header)
	def keep_if(condition):
		todelete = []
		for rownumber, row in enumerate(rows):
			if condition(row):
				tsvwriter.writerow(row)
				todelete.append(rownumber)
		for rownumber in todelete[::-1]:
			del rows[rownumber]
	def is_pathogenic_in_clinvar(row):
		return 'pathogenic' in row[dictionnary['ClinVar']].lower() and 'conflicting_interpretations_of_pathogenicity' not in row[dictionnary['ClinVar']].lower()
	keep_if(is_pathogenic_in_clinvar)
	
	def is_disease_mutation_in_HGMD(row):
		return 'dm' in row[dictionnary['HGMD_Class']].lower()
	keep_if(is_disease_mutation_in_HGMD)
	
	def is_monoallelic(row):
		return 'multiallelic' != row[dictionnary['Multiallelic']].lower()
	keep_if(is_monoallelic)
	