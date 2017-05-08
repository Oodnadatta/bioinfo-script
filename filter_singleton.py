#! /usr/bin/env python3

import sys

def find_genotype(variant, column):
	"Récupère le génotype dans le vcf (1/1 par exemple)"
	return variant.split('\t')[column].split(':')[0].split('/')

if __name__ == '__main__':
	
	homozygous = '-homozygous' in sys.argv
	if homozygous:
		sys.argv.remove('-homozygous')
	compound_heterozygous = '-compound-heterozygous' in sys.argv
	if compound_heterozygous:
		sys.argv.remove('-compound-heterozygous')
	xlinked = '-xlinked' in sys.argv
	if xlinked:
		sys.argv.remove('-xlinked')
	
	dico = {}
	
	for line in sys.stdin:
		line = line.rstrip()
		if line.startswith('#'):
			print(line) # write the header
							
		else:
			child_genotype = find_genotype(line, 9)
			if child_genotype[0] != '0': # pour homozygotes
				if 'X' in line.split('\t', 1)[0]:
					if xlinked:
						print(line)
					
				else:
					if homozygous:
						print(line)
					
			else: # pour les hétérozygotes composites
				if child_genotype[1] != '0':
					if compound_heterozygous:
						split_string = 'EFF=' in line and 'EFF=' or 'ANN='
						annotation = line.split('\t')[7].split(split_string)[1].split(';')[0]
						for effect in annotation.split(','):
							gene_name = effect.split('|')[3]
							if gene_name:
								if gene_name not in dico:
									dico[gene_name] = set()
								dico[gene_name].add(line)

	# annotation = ensemble des annotation des snpEFF uniquement
	#	exemple :
	#	frameshift_variant(HIGH||ccc/cTcc|p.Pro54_Pro55fs/c.161_162insT|540|SAMD11|protein_coding|CODING|ENST00000455979|1|1|WARNING_TRANSCRIPT_NO_START_CODON),frameshift_variant(HIGH||ccc/cTcc|p.Pro228_Pro229fs/c.683_684insT|681|SAMD11|protein_coding|CODING|ENST00000342066|7|1),upstream_gene_variant(MODIFIER||909|||SAMD11|processed_transcript|CODING|ENST00000478729||1),upstream_gene_variant(MODIFIER||1639|||SAMD11|retained_intron|CODING|ENST00000474461||1),upstream_gene_variant(MODIFIER||2666|||SAMD11|retained_intron|CODING|ENST00000466827||1),upstream_gene_variant(MODIFIER||2729|||SAMD11|retained_intron|CODING|ENST00000464948||1),downstream_gene_variant(MODIFIER||3644||108|SAMD11|protein_coding|CODING|ENST00000437963||1),downstream_gene_variant(MODIFIER||4767||749|NOC2L|protein_coding|CODING|ENST00000327044||1),downstream_gene_variant(MODIFIER||4767|||NOC2L|retained_intron|CODING|ENST00000483767||1),downstream_gene_variant(MODIFIER||4768|||NOC2L|retained_intron|CODING|ENST00000477976||1),downstream_gene_variant(MODIFIER||146||178|SAMD11|protein_coding|CODING|ENST00000420190||1),intron_variant(MODIFIER|||c.427+25_427+26insT|588|SAMD11|protein_coding|CODING|ENST00000341065|5|1|WARNING_TRANSCRIPT_NO_START_CODON)

	# dico = dico
	# gene_name = clé
	# dico[gene_name] = valeur associée à gene_name = un set

	dedoublon = set() #dedoublon : les variants que l'on va garder
	for gene_name in dico:
		if len(dico[gene_name]) > 1:
			dedoublon.update(dico[gene_name]) #ajoute à dédoublon tous les variants qui n'étaient pas déjà dans dédoublon

	#Des variants peuvent chevaucher plusieurs gènes. Ces variants ne doivent apparaître qu'une seule fois dans le fichier vcf de sortie.
	#Dédoublon sert à éviter cette redondance car dédoublon est un set.
	
	for variant in dedoublon:
		print(variant)

	# variant = élément de dico[gene_name], ce dernier est un set. L'élement d'un set (de string) se trouve entre '' quand il est affiché avec print.
