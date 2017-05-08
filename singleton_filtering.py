#! /usr/bin/env python3

import sys

def find_genotype(variant, column):
	"Récupère le génotype dans le vcf (1/1 par exemple)"
return variant.split('\t')[column].split(':')[0].split('/')
