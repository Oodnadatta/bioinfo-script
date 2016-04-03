#! /usr/bin/env python3

# (C) 2016 Anne-Sophie Denommé-Pichon <as.denomme@outlook.com>
# (C) 2016 Jérémie Roquet <jroquet@arkanosis.net>
# Released under the MIT license

import csv
import jinja2
import os
import os.path
import requests
import shutil
import sys
import urllib.parse

__version__ = "1.0.0"

_templates = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)
_templates.filters['urlencode'] = urllib.parse.quote
_missing_genes_filename = 'missing_genes.html'
_missing = _templates.get_template('{}.tpl'.format(_missing_genes_filename))

def load_tsv(filename):
    '''
    Tab-separated values file format:
    Each column is associated to one index, the name of which is in the first row.
    Remaining rows contain genes for the index (one gene per row).
    '''
    genes = {}
    indexes = None
    with open(filename) as input:
        tsv_reader = csv.reader(input, delimiter='\t')
        for row in tsv_reader:
            if indexes:
                for gene_column, gene in enumerate(row):
                    if gene.strip():
                        genes.setdefault(indexes[gene_column], set()).add(gene.strip())
            else:
                indexes = [ index[:-2].strip() for index in row ]
    return genes

class HBT:
    __root = 'http://hbatlas.org/hbtd'

    @classmethod
    def __pdf_url(cls, gene):
        return '{}/images/wholeBrain/{}.pdf'.format(cls.__root, gene)

    @classmethod
    def download_pdf(cls, gene, filename):
        response = requests.get(cls.__pdf_url(gene), stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as pdf:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, pdf)
                return True
        else:
            print('Warning: unable to download PDF for gene {}'.format(gene), file=sys.stderr)
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {} genes.tsv output_directory'.format(sys.argv[0].split(os.sep)[-1]))
        sys.exit(1)

    missing_genes = set()
    os.makedirs('{}/all_genes'.format(sys.argv[2]))
    for index, genes in load_tsv(sys.argv[1]).items():
        os.makedirs('{}/{}'.format(sys.argv[2], index))
        for gene in genes:
            pdf_file = '{}/all_genes/{}.pdf'.format(sys.argv[2], gene)
            if not os.path.exists(pdf_file):
                if not HBT.download_pdf(gene, pdf_file):
                    missing_genes.add(gene)
            if gene in missing_genes:
                os.symlink('../{}'.format(_missing_genes_filename), '{}/{}/{}.missing'.format(sys.argv[2], index, gene))
            else:
                os.symlink('../all_genes/{}.pdf'.format(gene), '{}/{}/{}.pdf'.format(sys.argv[2], index, gene))
    missing_genes_filename = '{}/{}'.format(sys.argv[2], _missing_genes_filename)
    with open(missing_genes_filename, 'w') as missing_genes_file:
        missing_genes_file.write(_missing.render(genes=sorted(missing_genes)))
    print('{} missing PDFs. See "{}" for more details'.format(len(missing_genes), missing_genes_filename))
