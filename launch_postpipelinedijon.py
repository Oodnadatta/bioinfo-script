#! /usr/bin/env python3

import glob
import sys

import postpipelinedijon

empty_file_exception = False

for inputtsvfilename in glob.glob(r'C:\Users\asden\Desktop\Exomes Dijon\*.report.tsv'):
	try:
		postpipelinedijon.filter_variants(inputtsvfilename, inputtsvfilename.replace('report.tsv', 'report.filtered.tsv'))
	except postpipelinedijon.EmptyFileException as ex:
		empty_file_exception = True

if empty_file_exception:
	sys.exit(1)
