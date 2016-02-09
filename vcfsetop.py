#! /usr/bin/env python3

# (C) 2016 Anne-Sophie Denommé-Pichon <as.denomme@outlook.com>
# (C) 2016 Jérémie Roquet <jroquet@arkanosis.net>
# Released under the MIT license

import click
import itertools
import os.path
import re
import sys

__version__ = "1.0.0"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--xgi/--no-xgi', default=False, help='Expand unknown genotypes for included samples (default: no).')
@click.option('--xge/--no-xge', default=False, help='Expand unknown genotypes for excluded samples (default: no).')
@click.option('--exclude', '-e', multiple=True, help='Drop variants from this sample.')
@click.option('--include', '-i', multiple=True, help='Keep variants from this sample.')
@click.option('--require', '-r', multiple=True, help='Keep variants from this sample only.')
@click.argument('vcf')
def filter(xgi, xge, exclude, include, require, vcf):
    'Filter variants from a VCF file (stdin if the argument is "-"), to keep only variants from the required samples (if any), from the included samples (otherwise) and not from the excluded samples (anyway).'

    def parse_columns(line):
        columns = { sample: column for column, sample in enumerate(line.split()) if column > 8 }
        def map_columns(samples):
            res = set()
            for sample in samples:
                if sample in columns:
                    res.add(columns[sample])
                else:
                    print('Sample "{}" not available in VCF "{}"'.format(sample, vcf), file=sys.stderr)
                    sys.exit(1)
            return res
        return map_columns(exclude), map_columns(include), map_columns(require)

    CHROM = 0
    POS = 1
    ALT = 4

    def process(input):
        for line in input:
            line = line.rstrip()
            if line.startswith('#'):
                print(line)
                if not line.startswith('##'):
                    excluded, included, required = parse_columns(line)
            else:
                columns = line.split()
                alt = columns[ALT].split(',')

                def get_alleles(sample, expand_unknown_genotype):
                    genotype = re.split('/|', columns[sample].split(':')[0])
                    if expand_unknown_genotype and '.' in genotype:
                        return set(alt)
                    return set([alt[int(allele) - 1] for allele in genotype if allele not in '.0'])

                alleles = set()
                for sample in required or included:
                    alleles |= get_alleles(sample, xgi)
                for sample in required:
                    alleles &= get_alleles(sample, xgi)
                for sample in excluded:
                    alleles -= get_alleles(sample, xge)

                if alleles:
                    columns[ALT] = ','.join(sorted(alleles))
                    print('\t'.join(columns))

    for excluded in exclude:
        if excluded in include or excluded in require:
            print('Sample "{}" can\'t be included and excluded at the same time'.format(excluded), file=sys.stderr)
            sys.exit(1)
    for required in require:
        if required in include:
            print('Sample "{}" can\'t be included and required at the same time'.format(required), file=sys.stderr)
            sys.exit(1)
    if vcf == '-':
        process(sys.stdin)
    else:
        if not os.path.exists(vcf):
            print('No such file:', vcf, file=sys.stderr)
            sys.exit(1)
        with open(vcf) as input:
            process(input)

@cli.command()
@click.argument('vcf')
def list(vcf):
    'List samples that can be used to filter variants from a VCF file using the "filter" command.'
    if not os.path.exists(vcf):
        print('No such file:', vcf, file=sys.stderr)
        sys.exit(1)
    with open(vcf) as input:
        for line in input:
            if line.startswith('#') and not line.startswith('##'):
                for sample in line.split()[9:]:
                    print(sample)
                break

if __name__ == '__main__':
    cli()
