#! /bin/sh

if [ $# -ne 2 ]; then
    echo "Usage: $(basename $0) input.vcf output.vcf" >&2
    exit 1
fi

input="$(readlink -f $1)"
output="$(readlink -f $2)"

java -jar -Xmx16g ~/tools/snpEff/snpEff.jar \
     eff GRCh37.75 \
     -t \
     -i vcf \
     -o vcf \
     -nodownload \
     -sequenceOntology \
     -lof \
     -noStats \
     "$input" \
     > "$output"
