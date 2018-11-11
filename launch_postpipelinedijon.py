#! /usr/bin/env python3

import glob
import sys

import postpipelinedijon

for inputtsvfilename in glob.glob(r'C:\Users\asden\Desktop\Exomes Dijon\*.report.tsv'):
	postpipelinedijon.filter_variants(inputtsvfilename, inputtsvfilename.replace('report.tsv', 'report.filtered.tsv'))
