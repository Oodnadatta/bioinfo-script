#! /usr/bin/env python3

import csv
import sys

class EmptyFileException(Exception):
	pass

def filter_variants(inputtsvfilename, outputtsvfilename):
	with open(inputtsvfilename, 'r', newline='') as inputtsvfile:
		tsvreader = csv.reader(inputtsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
		try:
			header = next(tsvreader)
		except StopIteration as ex:
			print('File "' + inputtsvfilename + '" is empty.', file=sys.stderr)
			raise EmptyFileException() from ex
		#TODO: reprint header to be in tsv and not in csv
		dictionnary = {columnname:columnnumber for columnnumber, columnname in enumerate(header)}
		rows = []
		for row in tsvreader:
			rows.append(row)

	with open(outputtsvfilename, 'w', newline='') as outputtsvfile:
		tsvwriter = csv.writer(outputtsvfile, delimiter='\t')
		tsvwriter.writerow(header)
		def keep_if(condition, title):
			tsvwriter.writerow(['#' + title])
			todelete = []
			for rownumber, row in enumerate(rows):
				if condition(row):
					tsvwriter.writerow(row)
					todelete.append(rownumber)
			for rownumber in todelete[::-1]:
				del rows[rownumber]
		def is_pathogenic_in_clinvar(row):
			return 'pathogenic' in row[dictionnary['ClinVar']].lower() and 'conflicting_interpretations_of_pathogenicity' not in row[dictionnary['ClinVar']].lower()
		
		def is_disease_mutation_in_HGMD(row):
			return 'dm' in row[dictionnary['HGMD_Class']].lower()
		
		def is_monoallelic(row):
			return 'multiallelic' != row[dictionnary['Multiallelic']].lower()
		
		def has_allele_balance_over(threshold):
			def has_allele_balance_over_threshold(row):
				return float(row[4].strip('"').split('=')[-1]) >= threshold
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
				has_count_in_gnomad_under(10)(row) and
				has_not_only_recessive_inheritance_in_OMIM(row) and
				has_count_in_batch_under(2)(row) and
				has_count_in_control_under(1)(row))
		
		def has_not_only_dominant_inheritance_in_OMIM(row):
			for inheritance in row[dictionnary['OMIM_inheritance']].split('|'):
				if inheritance != 'AD':
					return True
			return False
		
		def is_candidate_for_recessive_inheritance(row):
			return (
				is_monoallelic(row) and
				has_allele_balance_over(0.20)(row) and
				is_in_OMIM(row) and
				not is_dominant(row) and
				has_not_only_dominant_inheritance_in_OMIM(row) and
				has_count_in_batch_under(3)(row) and
				has_count_in_control_under(2)(row))
		
		def is_truncating(row):
			return 'true' == row[dictionnary['Truncating']].lower()		
		
		def has_not_only_dominant_inheritance_in_OMIM(row):
			for inheritance in row[dictionnary['OMIM_inheritance']].split('|'):
				if inheritance != 'AD':
					return True
			return False
		
		def has_PLI_over(threshold):
			def has_PLI_over_threshold(row):
				for intolerance in row[dictionnary['PLI']].split(','):
					if intolerance != '.' and float(intolerance) >= threshold:
						return True
				return False
			return has_PLI_over_threshold
		
		def is_intolerated_truncated_and_not_in_OMIM(row):
			return (
				is_monoallelic(row) and
				has_allele_balance_over(0.20)(row) and
				has_PLI_over(0.9)(row) and
				is_truncating(row) and	
				not is_in_OMIM(row) and
				has_count_in_batch_under(3)(row) and
				has_count_in_control_under(2)(row))
		
		def has_CNV(row):
			return '.' != row[dictionnary['CNVs']]
		
		keep_if(is_pathogenic_in_clinvar, 'Pathogenic or likely pathogenic in ClinVar')
		keep_if(is_disease_mutation_in_HGMD, '"Disease mutation" (or suspected as) in HGMD')
		keep_if(is_candidate_for_recessive_inheritance, 'Recessive')
		keep_if(is_candidate_for_dominant_inheritance, 'Dominant')
		keep_if(is_intolerated_truncated_and_not_in_OMIM, 'Intolerant truncated the gene of which is not in OMIM')
		keep_if(has_CNV, 'CNV in the same gene')
		
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print('Usage: postpipelinedijon.py inputfilename.tsv outputfilename.tsv', file=sys.stderr)
		sys.exit(1)
	try:
		filter_variants(sys.argv[1], sys.argv[2])
	except EmptyFileException as ex:
		sys.exit(1)
