#! /usr/bin/env python3

# (C) 2015-2016 Anne-Sophie Denommé-Pichon <as.denomme@outlook.com>
# (C) 2015-2016 Jérémie Roquet <jroquet@arkanosis.net>
# Released under the MIT license

import click
import collections
import enum
import jinja2
import os
import os.path
import re
import readline
import sys
import yaml

__version__ = "1.0.0"

_id = re.compile(r'[a-zA-Z0-9_-]+')
_sep = re.compile(r'[/._-]')
_ext = re.compile(r'\.(?:fastq|fq|vcf|mk|smk)(?:\.gz)?$')

_templates = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))), trim_blocks=True)
_smakefile = _templates.get_template('SMakefile.tpl')
_makefile = _templates.get_template('Makefile.tpl')

def remove_extension(str):
    return _ext.sub('', str)

def smakefile_name(makefile):
    return remove_extension(makefile) + '.smk'

class ScanMode(enum.Enum):
    full = 1
    update = 2
    ask = 3

class NameBase:
    'This class provides very basic AI to "guess" the name of the next VCF based on the previous ones'

    __transformations = [
        str,
        str,
        str.lower,
    ]

    def __init__(self):
        self.__names = {}
        self.__prediction = None

    def __vectors(self, id):
        original_vectors = _sep.split(remove_extension(id))
        capitalized_vectors = [ vector.capitalize() for vector in original_vectors ]
        lowercase_vectors = [ vector.lower() for vector in original_vectors ]
        return original_vectors, capitalized_vectors, lowercase_vectors

    def __find_index(self, fastq, name):
        for vector, (transform_id, transform) in zip(self.__vectors(fastq), enumerate(NameBase.__transformations)):
            try:
                index = vector.index(transform(name))
                return transform_id, index
            except ValueError:
                pass

    def learn(self, fastq1, fastq2, name):
        self.__names[fastq1] = name
        self.__names[fastq2] = name
        try:
            index1 = self.__find_index(fastq1, name)
            index2 = self.__find_index(fastq2, name)
            if index1 == index2:
                self.__prediction = index1
        except ValueError:
            pass

    def knows(self, fastq1, fastq2):
        return fastq1 in self.__names or fastq2 in self.__names

    def same(self, fastq1, fastq2, name):
        return self.__names.get(fastq1) == self.__names.get(fastq2) == name

    def old(self, fastq1, fastq2):
        if self.__names.get(fastq1) == self.__names.get(fastq2):
            return self.__names.get(fastq1)

    def guess(self, fastq1, fastq2):
        return self.__prediction is not None and \
            NameBase.__transformations[self.__prediction[0]](self.__vectors(fastq1)[self.__prediction[0]][self.__prediction[1]])

class OrderedLoader(yaml.SafeLoader):
    pass
def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return collections.OrderedDict(loader.construct_pairs(node))
OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

def load_yaml(smakefile):
    with open(smakefile) as file:
        return yaml.load(file, OrderedLoader)

def dump_as_yaml(data, smakefile):
    with open(smakefile, 'w') as file:
        file.write(_smakefile.render(
            version=__version__,
            root=data['root'],
            rules=data['rules'],
        ))

def dump_as_makefile(data, makefile):
    with open(makefile, 'w') as file:
        file.write(_makefile.render(
            root=data['root'],
            rules=data['rules'],
        ))

def ask_for_mode():
    while True:
        answer = {
            'u': ScanMode.update,
            'i': ScanMode.full,
            '': ScanMode.update
        }.get(input('SMakefile found, update or ignore. [U/i] ').lower())
        if answer:
            return answer

def ask_for_name(fastqs, default):
    def hook():
        readline.insert_text(default)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    while True:
        answer = input('''Enter a name for the VCF associated with the following FASTQ files (or "." to skip):
 - {fastq1}
 - {fastq2}
> '''.format(fastq1=fastqs[0], fastq2=fastqs[1])) or default
        if answer:
            readline.set_pre_input_hook()
            return answer

def ask_for_override(name, fastqs):
    while True:
        answer = {
            'y': True,
            'n': False,
            '': False
        }.get(input('''The name "{name}" is already associated with the following FASTQ files:
 - {fastq1}
 - {fastq2}
Override? [y/N] '''.format(name=name, fastq1=fastqs['fastq1'], fastq2=fastqs['fastq2'])).lower())
        if answer is not None:
            return answer

@click.group()
def cli():
    pass

@cli.command()
@click.option('--full', 'mode', flag_value=ScanMode.full, help='Perform a full scan, ignoring existing Makefile.')
@click.option('--update', 'mode', flag_value=ScanMode.update, help='Perform a partial scan, updating existing Makefile.')
@click.option('--ask', 'mode', flag_value=ScanMode.ask, default=True, help='Ask whether to perform a full scan or an update (default).')
@click.argument('directory')
@click.option('--output', '-o', 'makefile', default='.', help='Path to the Makefile to generate (default: in the scanned directory)')
def scan(mode, directory, makefile):
    'Scan a DIRECTORY for FASTQ files and produce the MAKEFILE and its associated SMakefile.'
    directory = directory.rstrip(os.sep)
    if not os.path.exists(directory):
        print('No such directory:', directory, file=sys.stderr)
        sys.exit(1)
    if makefile == '.':
        makefile = os.path.join(directory, 'Makefile')
    smakefile = smakefile_name(makefile)
    output = {
        'root': directory,
        'rules': collections.OrderedDict()
    }
    if os.path.exists(smakefile):
        if mode == ScanMode.ask:
            mode = ask_for_mode()
        output['rules'].update(load_yaml(smakefile).get('rules', {}))
    names = NameBase()
    for name, fastqs in output['rules'].items():
        names.learn(fastqs['fastq1'], fastqs['fastq2'], name)
    for path, directories, filenames in os.walk(directory):
        path = path[len(directory) + 1:]
        directories.sort()
        fastqs = []
        filenames.sort()
        for filename in filenames:
            if filename.endswith('.fastq') or \
               filename.endswith('.fastq.gz'):
                fastqs.append(os.path.join(path, filename))
        if len(fastqs) == 2:
            if mode == ScanMode.full or \
               not names.knows(fastqs[0], fastqs[1]):
                while True:
                    old_name = names.old(fastqs[0], fastqs[1])
                    name = remove_extension(ask_for_name(fastqs, old_name or names.guess(fastqs[0], fastqs[1])))
                    if name == '.':
                        print('Skipping.')
                        break
                    elif not _id.match(name):
                        print('Invalid name, only "_", "-" and alphanumerical characters allowed.')
                    elif name not in output['rules'] or \
                       names.same(fastqs[0], fastqs[1], name) or \
                       ask_for_override(name, output['rules'][name]):
                       break
                if old_name:
                    del output['rules'][old_name]
                if name != '.':
                    output['rules'][name] = {
                        'fastq1': fastqs[0],
                        'fastq2': fastqs[1]
                    }
                    names.learn(fastqs[0], fastqs[1], name)
        elif fastqs:
            print('Warning: found {} FASTQ files in directory "{}, skipping"'.format(len(fastqs), path), file=sys.stderr)
    dump_as_yaml(output, smakefile)
    dump_as_makefile(output, makefile)

@cli.command()
@click.argument('makefile')
def list(makefile):
    'List the targets of the MAKEFILE\'s associated SMakefile.'
    smakefile = smakefile_name(makefile)
    if not os.path.exists(smakefile):
        print('SMakefile not found for', makefile, file=sys.stderr)
        sys.exit(1)
    for name, _ in load_yaml(smakefile)['rules'].items():
        print(name)

@cli.command()
@click.argument('makefile')
def regenerate(makefile):
    'Regenerate the MAKEFILE from its SMakefile.'
    smakefile = smakefile_name(makefile)
    if not os.path.exists(smakefile):
        print('SMakefile not found for', makefile, file=sys.stderr)
        sys.exit(1)
    if smakefile == makefile:
        print('Makefile and SMakefile have the same name', file=sys.stderr)
        sys.exit(1)
    dump_as_makefile(load_yaml(smakefile), makefile)

if __name__ == '__main__':
    cli()
