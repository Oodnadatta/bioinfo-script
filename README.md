# Bioinfo script

## Smake
### Motivation
Generate vcf from fastq

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
$ smake.py scan --full FastqDirectory/
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


#### list
The `list` command shows all the targets in the Makefile. These targets can be passed as parameter to gmake.
