#! /usr/bin/env python3
# By Anne-Sophie Denommé-Pichon
# 2019-09-02
# AGLPv3

with open('dijen528.raw.vcf') as file:
	for line in file:
		if not line.startswith('#'):
			cells = line.split('\t')
			depth = cells[9].split(':')[1].split(',')
			
			chrom = cells[0]
			pos = cells[1]
			wild_depth = int(depth[0])
			var_depth = int(depth[1])
			try:
				allelic_balance = var_depth / (wild_depth + var_depth)
				print(f'{chrom}\t{pos}\t{allelic_balance:.3f}')
			except ZeroDivisionError:
				pass
