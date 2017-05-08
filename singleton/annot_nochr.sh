#! /bin/sh

/commun/data/packages/jdk/jdk1.8.0_60/bin/java -Xmx16g -jar $HOME/src/snpEff/snpEff.jar GRCh37.75 -i vcf -o vcf -sequenceOntology -lof -noStats $1 > $1.1.tmp
sed -i 's/^chr//' $1.1.tmp
/commun/data/packages/vep/ensembl-tools-release-76/scripts/variant_effect_predictor/variant_effect_predictor.pl \
    --cache --dir /commun/data/pubdb/ensembl/vep/cache --write_cache  \
    --species homo_sapiens \
    --assembly GRCh37 \
    --db_version 76 \
    --fasta /commun/data/pubdb/broadinstitute.org/bundle/1.5/b37/index-bwa-0.7.10/human_g1k_v37.fasta \
    --offline \
    --symbol \
    --format vcf \
    --force_overwrite \
    --sift=b \
    --polyphen=b \
    --refseq \
    --gmaf \
    --maf_1kg \
    --maf_esp \
    --everything \
    --pubmed \
    --xref_refseq \
    --quiet --vcf --no_stats \
    -i $1.1.tmp \
    -o $1.2.tmp
/commun/data/packages/jdk/jdk1.8.0_60/bin/java -Xmx16g -jar $HOME/src/snpEff/SnpSift.jar dbnsfp -v -db $HOME/src/dbNsfp/2.9.1_hg19_20160330.vcf.gz $1.2.tmp > $1.3.tmp
/commun/data/packages/jdk/jdk1.8.0_60/bin/java -Xmx16g -jar $HOME/src/snpEff/SnpSift.jar annotate -id $HOME/src/dbSNP/human_9606_b147_GRCh37p13_all_20160601.vcf.gz $1.3.tmp > $1.4.tmp
/commun/data/packages/jdk/jdk1.8.0_60/bin/java -Xmx16g -jar $HOME/src/snpEff/SnpSift.jar annotate -id $HOME/src/clinvar/GRCh37_20160831.vcf.gz $1.4.tmp > $2
