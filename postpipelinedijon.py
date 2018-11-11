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
	# keep_if(is_pathogenic_in_clinvar)
	
	def is_disease_mutation_in_HGMD(row):
		return 'dm' in row[dictionnary['HGMD_Class']].lower()
	# keep_if(is_disease_mutation_in_HGMD)
	
	def is_monoallelic(row):
		return 'multiallelic' != row[dictionnary['Multiallelic']].lower()
	
	def has_allele_balance_over(threshold):
		def has_allele_balance_over_threshold(row):
			return float(row[dictionnary['dijex2934']].split('=')[-1]) >= threshold
		return has_allele_balance_over_threshold
	
	def is_in_OMIM(row):
		return '.' != row[dictionnary['OMIM']]
	
	def is_dominant(row):
		return 'no' == row[dictionnary['Recessive']].lower()
	
	def has_count_in_gnomad_under(threshold):
		def has_count_in_gnomad_under_threshold(row):
			return (
				('.' == row[dictionnary['AC_gnomADex']] or
				float(row[dictionnary['AC_gnomADex']]) <= threshold) and
				('.' == row[dictionnary['AC_gnomADge']] or
				float(row[dictionnary['AC_gnomADge']]) <= threshold))
		return has_count_in_gnomad_under_threshold
	
	def has_not_only_recessive_inheritance_in_OMIM(row):
		for inheritance in row[dictionnary['OMIM_inheritance']].split('|'):
			if inheritance != 'AR':
				return True
		return False
	
	def has_count_in_batch_under(threshold):
		def has_count_in_batch_under_threshold(row):
			return float(row[dictionnary['BatchSampleCount']]) <= threshold
		return has_count_in_batch_under_threshold
	
	def has_count_in_control_under(threshold):
		def has_count_in_control_under_threshold(row):
			return float(row[dictionnary['ControlSampleCount']]) <= threshold
		return has_count_in_control_under_threshold
	
	def is_candidate_for_dominant_inheritance(row):
		return (
			is_monoallelic(row) and
			has_allele_balance_over(0.20)(row) and
			is_in_OMIM(row) and
			is_dominant(row) and
			has_count_in_gnomad_under(5)(row) and
			has_not_only_recessive_inheritance_in_OMIM(row) and
			has_count_in_batch_under(3)(row) and
			has_count_in_control_under(2)(row))
	
	keep_if(is_candidate_for_dominant_inheritance)
	
		