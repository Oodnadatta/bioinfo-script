#! /bin/sh

if [ $# -ne 3 ]; then
    echo "Usage: $(basename $0) input.vcf output.vcf filter" >&2
    exit 1
fi

input="$(readlink -f $1)"
output="$(readlink -f $2)"
filter="$3"

cd ~/tools/ensembl-tools-release-83/scripts/variant_effect_predictor && ./filter_vep.pl  \
    --format vcf \
    -f "$filter" \
    -i "$input" \
    -o "$output"
