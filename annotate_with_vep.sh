#! /bin/sh

if [ $# -ne 2 ]; then
    echo "Usage: $(basename $0) input.vcf output.vcf" >&2
    exit 1
fi

input="$(readlink -f $1)"
output="$(readlink -f $2)"

cd ~/tools/ensembl-tools-release-83/scripts/variant_effect_predictor && ./variant_effect_predictor.pl  \
    --fork 24 \
    --buffer_size 100000 \
    --cache --dir ~/db/VEP --offline \
    --db_version 83 \
    --species homo_sapiens \
    --assembly GRCh37 \
    --symbol \
    --variant_class \
    --sift b \
    --polyphen b \
    --gmaf \
    --maf_1kg \
    --maf_esp \
    --maf_exac \
    --format vcf \
    --vcf \
    --no_stats \
    -i "$input" \
    -o "$output"
