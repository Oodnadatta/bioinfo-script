#Created by Anne-Sophie Denommé-Pichon
#2015-12-22

# Usage:
# make -f calling.mk FASTQ1=R1.fastq FASTQ2=R2.fastq BAM=file.bam [THREADS=nbThreads] [MEMORY=memoryToUse]

# TODO: use variables instead of full paths with version numbers

FASTQ1 =
FASTQ2 =
BAM =

THREADS = 24
MEMORY = 16g

# TODO FIXME use gmake subst instead of shell / sed
SAM = $(shell echo "$(BAM)" | sed 's/.bam$$/.sam/')
GVCF = $(shell echo "$(BAM)" | sed 's/.bam$$/.gvcf/')
VCF = $(shell echo "$(BAM)" | sed 's/.bam$$/.vcf/')
SAMPLE = $(shell echo "$(BAM)" | sed 's@\(.*/\)\?\([^/]*\).bam$$@\2@')

GATK = java -Xmx$(MEMORY) -jar ~/tools/GATK/GenomeAnalysisTK.jar

all: $(VCF).filtered.vcf

############################ RESOURCES ############################

#Get reference genome file from 1kG
~/db/human_g1k_v37.fasta:
	wget "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/human_g1k_v37.fasta.gz" -O - \
		| gunzip > $@

~/db/human_g1k_v37.fasta.fai:
	wget "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/human_g1k_v37.fasta.fai" -O $@

~/db/human_g1k_v37.dict: ~/db/human_g1k_v37.fasta
	picard-tools CreateSequenceDictionary R=$< O=$@

~/db/human_g1k_v37.fasta.bwt: ~/db/human_g1k_v37.fasta
	bwa index -a bwtsw $<

#Get indel sites from 1kG
~/db/1000G_phase1.indels.b37.vcf:
	wget "ftp://gsapubftp-anonymous:@ftp.broadinstitute.org/bundle/2.8/b37/1000G_phase1.indels.b37.vcf.gz" -O - \
		| gunzip > $@

#Get capture files
~/db/Agilent/S04380110_Covered.bed:
	$(error 'Capture .bed is missing. To get the capture .bed, download the data from https://earray.chem.agilent.com/suredesign. Just create an account, log in, and select the "Find Designs" tab, then "SureSelect DNA" then under that select "Agilent Catalog", then there should be a list of the different SureSelect related bed files and whatnot.')

~/db/Agilent/S04380110_Covered_noprefix.bed: ~/db/Agilent/S04380110_Covered.bed
	grep -v '^(browser|track)' $< | sed 's/^chr//' > $@

#Get dbSNP database
~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf:
	wget "ftp://ftp.ncbi.nlm.nih.gov/snp/organisms/human_9606_b146_GRCh37p13/VCF/00-All.vcf.gz" -O - \
		| gunzip > $@

# Get VQSR resources
~/db/hapmap_3.3.b37.vcf:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/hapmap_3.3.b37.vcf.gz" -O - \
		| gunzip > $@

~/db/hapmap_3.3.b37.vcf.idx:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/hapmap_3.3.b37.vcf.idx.gz" -O - \
		| gunzip > $@

~/db/1000G_omni2.5.b37.vcf:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_omni2.5.b37.vcf.gz" - O - \
		| gunzip > $@

~/db/1000G_omni2.5.b37.vcf.idx:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_omni2.5.b37.vcf.idx.gz" -O - \
		| gunzip > $@

~/db/1000G_phase1.snps.high_confidence.b37.vcf:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_phase1.snps.high_confidence.b37.vcf.gz" -O - \
		| gunzip > $@

~/db/1000G_phase1.snps.high_confidence.b37.vcf.idx:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/1000G_phase1.snps.high_confidence.b37.vcf.idx.gz" - O - \
		| gunzip > $@

~/db/dbsnp_138.b37.vcf:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/dbsnp_138.b37.vcf.gz" -O - \
		| gunzip > $@

~/db/dbsnp_138.b37.vcf.idx:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/dbsnp_138.b37.vcf.idx.gz" -O - \
		| gunzip > $@

~/db/Mills_and_1000G_gold_standard.indels.b37.vcf:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.gz" -O - \
		| gunzip > $@

~/db/Mills_and_1000G_gold_standard.indels.b37.vcf.idx:
	wget "ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.idx.gz" -O - \
		| gunzip > $@

############################ ALIGNMENT ############################

# TODO add cutadapt if necessary (cf. FASTQC)

#Align with BWA
  #-M Mark shorter split hits as secondary (for Picard compatibility)
  #-R Complete read group header line
$(SAM): ~/db/human_g1k_v37.fasta $(FASTQ1) $(FASTQ2)
	bwa mem -t $(THREADS) -M -R "@RG\tID:exome\tSM:$(SAMPLE)\tPL:illumina\tLB:agilent_v5" $^ > $@

$(BAM): $(SAM)
	samtools view -hb $< > $@

$(BAM).sorted.bam: $(BAM)
	samtools sort -o -@ $(THREADS) $< _ > $@

#Flag BAM duplicates with Picard
$(BAM).duplicates.bam: $(BAM).sorted.bam
	picard-tools MarkDuplicates REMOVE_DUPLICATES=false METRICS_FILE="$(BAM).dup.log" I=$< O=$@
$(BAM).dup.log: $(BAM).duplicates.bam
	touch $@

$(BAM).duplicates.bai: $(BAM).duplicates.bam
	samtools index $<

#Realign indels
$(BAM).target.list: $(BAM).duplicates.bam ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/1000G_phase1.indels.b37.vcf
	$(GATK) \
		-nt $(THREADS) \
		-T RealignerTargetCreator \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-known ~/db/1000G_phase1.indels.b37.vcf \
		-I $< \
		-o $@

$(BAM).realigned.bam: $(BAM).duplicates.bam $(BAM).target.list ~/db/human_g1k_v37.fasta ~/db/1000G_phase1.indels.b37.vcf
	$(GATK) \
		-T IndelRealigner \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
			-known ~/db/1000G_phase1.indels.b37.vcf \
		-targetIntervals $(BAM).target.list \
		-o $@

#Recalibrate bases
$(BAM).bases: $(BAM).realigned.bam ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf
	$(GATK) \
		-nct $(THREADS) \
		-T BaseRecalibrator \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
		-knownSites ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf \
		-o $@

$(BAM).recalibrated.bam: $(BAM).realigned.bam $(BAM).bases ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nct $(THREADS) \
		-T PrintReads \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
		-BQSR "$(BAM).bases" \
		-o $@

############################  CALLING  ############################

#Split the Capture .bed  file into 24 files
#For now, not used in the calling. I have to implement this.
#nb_line_bed=$(wc -l ~/db/Agilent/S04380110_Covered_noprefix.bed | awk '{print $1}')
#nb_line_split=$(((nb_line_bed+THREADS-1)/THREADS))
#for i in $(seq THREADS)
#	do
#		test -f ~/db/Agilent/S04380110_Covered_noprefix_$i.bed || \
#		sed -n "$((nb_line_split*(i-1))),$((nb_line_split*i-1)) p" ~/db/Agilent/S04380110_Covered_noprefix.bed > ~/db/Agilent/S04380110_Covered_noprefix_$i.bed
#	done

#Call variants with GATK HaplotypeCaller in gVCF
$(GVCF): $(BAM).recalibrated.bam ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf
	$(GATK) \
		-nct $(THREADS) \
		-T HaplotypeCaller \
			-ERC GVCF \
			--variant_index_type LINEAR \
			--variant_index_parameter 128000 \
			-L:capture,BED ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-stand_call_conf 30.0 \
		-stand_emit_conf 10.0 \
		-S SILENT \
		-I $< \
		--dbsnp:vcfinput,VCF ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf \
		-o $@

# Generate VCF from gVCF
$(VCF): $(GVCF) ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nt $(THREADS) \
		-T GenotypeGVCFs \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-V $< \
		-o $@

# Compute VQSR model for SNPs
$(VCF).SNP.recal: $(VCF) ~/db/human_g1k_v37.fasta ~/db/hapmap_3.3.b37.vcf ~/db/1000G_omni2.5.b37.vcf ~/db/1000G_phase1.snps.high_confidence.b37.vcf.idx ~/db/dbsnp_138.b37.vcf
	$(GATK) \
		-nt $(THREADS) \
		-T VariantRecalibrator \
		-mode SNP \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		-resource:hapmap,known=false,training=true,truth=true,prior=15.0 ~/db/hapmap_3.3.b37.vcf \
		-resource:omni,known=false,training=true,truth=true,prior=12.0 ~/db/1000G_omni2.5.b37.vcf \
		-resource:1000G,known=false,training=true,truth=false,prior=10.0 ~/db/1000G_phase1.snps.high_confidence.b37.vcf \
		-resource:dbsnp,known=true,training=false,truth=false,prior=2.0 ~/db/dbsnp_138.b37.vcf \
			-an FS \
			-an MQ \
			-an MQRankSum \
			-an QD \
			-an ReadPosRankSum \
			-an SOR \
		-recalFile $@ \
		-tranchesFile "$(VCF).SNP.tranches"
$(VCF).SNP.tranches: $(VCF).SNP.recal
	touch $@

# TODO FIXME if nbSamples > 10 and unrelated, add -an InbreedingCoeff

# Apply VQSR model for SNPs
$(VCF).snp_recalibrated.vcf: $(VCF) $(VCF).SNP.recal $(VCF).SNP.tranches ~/db/human_g1k_v37.fasta
	$(GATK) \
		-T ApplyRecalibration \
		-mode SNP \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		--ts_filter_level 99.5 \
		-recalFile "$(VCF).SNP.recal" \
		-tranchesFile "$(VCF).SNP.tranches" \
		-o $@

# Compute VQSR model for indels
$(VCF).indels.recal: $(VCF) ~/db/human_g1k_v37.fasta ~/db/Mills_and_1000G_gold_standard.indels.b37.vcf ~/db/dbsnp_138.b37.vcf
	$(GATK) \
		-nt $(THREADS) \
		-T VariantRecalibrator \
		-mode INDEL \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		-resource:mills,known=false,training=true,truth=true,prior=12.0 ~/db/Mills_and_1000G_gold_standard.indels.b37.vcf \
		-resource:dbsnp,known=true,training=false,truth=false,prior=2.0 ~/db/dbsnp_138.b37.vcf \
			-an FS \
			-an MQRankSum \
			-an QD \
			-an ReadPosRankSum \
			-an SOR \
		--maxGaussians 4 \
		-recalFile $@ \
		-tranchesFile "$(VCF).indels.tranches"
$(VCF).indels.tranches: $(VCF).indels.recal
	touch $@

# Apply VQSR model for SNPs
$(VCF).all_recalibrated.vcf: $(VCF).snp_recalibrated.vcf $(VCF).indels.recal $(VCF).indels.tranches ~/db/human_g1k_v37.fasta
	$(GATK) \
		-T ApplyRecalibration \
		-mode INDEL \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		--ts_filter_level 99.0 \
		-recalFile "$(VCF).indels.recal" \
		-tranchesFile "$(VCF).indels.tranches" \
		-o $@

# Filter variants on VQSR results
$(VCF).filtered.vcf: $(VCF).all_recalibrated.vcf ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nt $(THREADS) \
		-T SelectVariants \
	                -env \
		-R ~/db/human_g1k_v37.fasta \
		-V $< \
		-o $@
