#! /bin/sh

if [ $# -ne 2 ]; then
    echo "Usage: $(basename $0) input.vcf output.vcf" >&2
    exit 1
fi

annotate_with_snpeff.sh "$1" "$2.tmp" && \
annotate_with_vep.sh "$2.tmp" "$2" && \
rm "$2.tmp"
