JAVA=/commun/data/packages/jdk/jdk1.8.0_60/bin/java -Xmx16g
JVARKIT=/commun/data/packages/jvarkit-git
SNPSIFT=/commun/data/users/asdp/src/snpEff/SnpSift.jar

HETEROZYGOUS_FREQUENCY=0.0001
RECESSIVE_FREQUENCY=0.01
XLINKED_FREQUENCY=0.005

.PHONY: all

.SECONDARY:

all: \
	TSVC_variants.predict.depth.clinvar.heterozygous.vcf \
	TSVC_variants.predict.depth.clinvar.homozygous.vcf \
	TSVC_variants.predict.depth.clinvar.compound_heterozygous.vcf \
	TSVC_variants.predict.depth.clinvar.xlinked.vcf \
	TSVC_variants.predict.depth.${HETEROZYGOUS_FREQUENCY}.cadd.heterozygous.vcf \
	TSVC_variants.predict.depth.${RECESSIVE_FREQUENCY}.cadd.homozygous.vcf \
	TSVC_variants.predict.depth.${RECESSIVE_FREQUENCY}.cadd.compound_heterozygous.vcf \
	TSVC_variants.predict.depth.${XLINKED_FREQUENCY}.cadd.xlinked.vcf

%.annot.vcf: %.vcf
	./annot_nochr.sh $< $@

%.predict.vcf: %.annot.vcf
	< $< ${JAVA} -jar ${JVARKIT}/vcffilterso.jar -A SO:0001818 -A SO:0001590 -A SO:0001572 -A SO:0001629 -A SO:0001569 -A SO:0001630 > $@

%.depth.vcf: %.vcf
	< $< ${JAVA} -jar ${JVARKIT}/vcffilterjs.jar -e 'variant.getGenotype("OM12").getDP() > 5' > $@

%.clinvar.vcf: %.vcf
	< $< ${JAVA} -jar ${SNPSIFT} filter "( CLNSIG = '4' ) || ( CLNSIG = '5' )" - > $@

%.cadd.vcf: %.vcf
	< $< ${JAVA} -jar ${SNPSIFT} filter "( dbNSFP_CADD_phred[ANY] >= 10 )" - > $@

%.heterozygous.vcf: %.vcf
	< $< ./filter_singleton.py -heterozygous > $@

%.homozygous.vcf: %.vcf
	< $< ./filter_singleton.py -homozygous > $@

%.compound_heterozygous.vcf: %.vcf
	< $< ./filter_singleton.py -compound-heterozygous > $@

%.xlinked.vcf: %.vcf
	< $< ./filter_singleton.py -xlinked > $@

%.${HETEROZYGOUS_FREQUENCY}.vcf: %.vcf
	< $< ${JAVA} -jar ${SNPSIFT} filter "( dbNSFP_ExAC_AF[ANY] < ${HETEROZYGOUS_FREQUENCY} )" - > $@

%.${RECESSIVE_FREQUENCY}.vcf: %.vcf
	< $< ${JAVA} -jar ${SNPSIFT} filter "( dbNSFP_ExAC_AF[ANY] < ${RECESSIVE_FREQUENCY} )" - > $@

%.${XLINKED_FREQUENCY}.vcf: %.vcf
	< $< ${JAVA} -jar ${SNPSIFT} filter "( dbNSFP_ExAC_AF[ANY] < ${XLINKED_FREQUENCY} )" - > $@
