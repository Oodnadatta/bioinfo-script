# Bioinfo script

## Smake
### Motivation
Generate VCF from fastq

### Usage
```bash
$ smake.py [OPTIONS] COMMAND [ARGS]
```

### Commands
Smake scans a directory containing fastqs. Smake creates:
 * a Makefile which can be used to create one (multisample) VCF from fastqs, depending on information given by the user (sample names)
 * a SMakefile which save this information to avoid having to give it again for subsequent uses.

#### scan
The `scan` command is required before using `regenerate` and `list` commands.
In order to add new fastqs to the analysis, `scan` command is required.

<table>
<tr><th>Options</th><th>Description</th></tr>
<tr><th>--full</th><td>Performs a full scan, ignoring existing Makefile. Exclusive with --update and --ask</td></tr>
<tr><th>--update</th><td>Perform a partial scan, updating existing Makefile. Exclusive with --full and --ask</td></tr>
<tr><th>--ask</th><td>Ask whether to perform a full scan or an update. Exclusive with --full and --ask (default)</td></tr>
<tr><th>-o, --output</th><td>Path to the Makefile to generate (default: in the scanned directory)</td></tr>
<tr><th>--help</th><td>Show this help and exit</td></tr>
</table>

Example:
```bash
$ smake.py scan --full FastqDirectory/ -o output.vcf
```

#### regenerate
The `regenerate` command renegerates the Makefile using information kept in the SMakefile.
This command is used if:
 * the Makefile has been manually edited
 * the Makefile has been damaged
 * Smake has been updated

<table>
<tr><th>Options</th><th>Description</th></tr>
<tr><th>--full</th><td>Performs a full scan, ignoring existing Makefile</td></tr>
<tr><th>--update</th><td>Perform a partial scan, updating existing Makefile</td></tr>
<tr><th>--ask</th><td>Ask whether to perform a full scan or an update (default)</td></tr>
<tr><th>--help</th><td>Show this help and exit</td></tr>
</table>

Example:
```bash
$ smake.py regenerate Makefile
```

#### list
The `list` command shows all the targets in the Makefile. These targets can be passed as parameter to gmake.

<table>
<tr><th>Options</th><th>Description</th></tr>
<tr><th>--help</th><td>Show this help and exit</td></tr>
</table>

Example:
```bash
$ smake.py list Makefile
```
### Depedencies
 * smake.py: main program
 * smake: symbolic link to py3wrapper
 * _smake: autocomplete for zsh
 * Makefile.tpl: template for Makefile to generate by smake.py
 * SMakefile.tpl: template for SMakefile to generate a Makefile with annotations concerning samples
 * py3wrapper: in order to use python3 on a python2 machine

## vcfsetop
### Motivation
Performs set manipulations on variants (inclusions and / or exclusions of variants from a VCF in another VCF).

### Usage
```bash
$ vcfsetop.py [OPTIONS] COMMAND [ARGS]
```

### Commands
#### filter
The `filter` command filter variants from a VCF file (stdin if the argument is "-"), to keep only variants from the required samples (if any), from the included samples (otherwise) and not from the excluded samples (anyway).

<table>
<tr><th>Options</th><th>Description</th></tr>
<tr><th>-e, --exclude</th><td>Drop variants from this sample</td></tr>
<tr><th>-i, --included</th><td>Keep variants from this sample</td></tr>
<tr><th>-r, --require</th><td>Keep variants from this sample only</td></tr>
<tr><th>--xgi / --no-xgi</th><td>Expand unknown genotypes for included samples (default: no)</td></tr>
<tr><th>--xge / --no-xge </th><td>Expand unknown genotypes for excluded samples (default: no)</td></tr>
<tr><th>--help</th><td>Show this help and exit</td></tr>
</table>

Example:
```bash
$ vcfsetop filter -r Sample1 -r Sample2 -e Sample3 input.vcf > output.vcf
```
This command keeps common variants in Sample1 and Sample2, and excludes variants in Sample3.
Samples should be in a same VCF file in input.

#### list
The `list` command list sample that can be used to filter variants from a VCF file using the `filter` command.

<table>
<tr><th>--help</th><td>Show this help and exit</td></tr>
</table>

Example:
```bash
$ vcfsetop list input.vcf
```

### Depedencies
 * vcfsetop.py: main program
 * vcfsetop: symbolic link to py3wrapper
 * vcfsetop: autocomplete for zsh
 * py3wrapper: in order to use python3 on a python2 machine
