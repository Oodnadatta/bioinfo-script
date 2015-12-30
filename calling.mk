#Created by Anne-Sophie Denommé-Pichon
#2015-12-22

FASTQ1 =
FASTQ2 =

THREADS = 24
MEMORY = 16g

GATK = java -Xmx$(MEMORY) -jar ~/tools/GATK/GenomeAnalysisTK.jar

.SECONDARY:
.PHONY: all

all:
	$(info Usage: make -f calling.mk FASTQ1=R1.fastq FASTQ2=R2.fastq output.vcf [THREADS=nbThreads] [MEMORY=memoryToUse])

############################ RESOURCES ############################

# TODO: use variables instead of full paths with version numbers

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
%.raw.sam: ~/db/human_g1k_v37.fasta $(FASTQ1) $(FASTQ2)
	bwa mem -t $(THREADS) -M -R "@RG\tID:exome\tSM:$(basename $(notdir $@))\tPL:illumina\tLB:agilent_v5" $^ > $@

%.raw.bam: %.raw.sam
	samtools view -hb $< > $@

%.sorted.bam: %.raw.bam
	samtools sort -o -@ $(THREADS) $< _ > $@

#Flag BAM duplicates with Picard
%.duplicates.bam: %.sorted.bam
	picard-tools MarkDuplicates REMOVE_DUPLICATES=false METRICS_FILE="$*.dup.log" I=$< O=$@
%.dup.log: %.duplicates.bam
	touch $@

%.duplicates.bai: %.duplicates.bam
	samtools index $<

#Realign indels
%.target.list: %.duplicates.bam %.duplicates.bai ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/1000G_phase1.indels.b37.vcf
	$(GATK) \
		-nt $(THREADS) \
		-T RealignerTargetCreator \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-known ~/db/1000G_phase1.indels.b37.vcf \
		-I $< \
		-o $@

%.realigned.bam: %.duplicates.bam %.target.list ~/db/human_g1k_v37.fasta ~/db/1000G_phase1.indels.b37.vcf
	$(GATK) \
		-T IndelRealigner \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
			-known ~/db/1000G_phase1.indels.b37.vcf \
		-targetIntervals $*.target.list \
		-filterMBQ \
		-o $@

#Recalibrate bases
%.bases: %.realigned.bam ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf
	$(GATK) \
		-nct $(THREADS) \
		-T BaseRecalibrator \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
		-knownSites ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf \
		-o $@

%.recalibrated.bam: %.realigned.bam %.bases ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nct $(THREADS) \
		-T PrintReads \
		-R ~/db/human_g1k_v37.fasta \
		-I $< \
		-BQSR "$*.bases" \
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
%.raw.gvcf: %.recalibrated.bam ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta ~/db/dbSNP/GRCh37p13_dbsnp146_00-All.vcf
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
%.raw.vcf: %.raw.gvcf ~/db/Agilent/S04380110_Covered_noprefix.bed ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nt $(THREADS) \
		-T GenotypeGVCFs \
			-L ~/db/Agilent/S04380110_Covered_noprefix.bed \
		-R ~/db/human_g1k_v37.fasta \
		-V $< \
		-o $@

# Compute VQSR model for SNPs
%.raw.vcf.SNP.recal: %.raw.vcf ~/db/human_g1k_v37.fasta ~/db/hapmap_3.3.b37.vcf ~/db/1000G_omni2.5.b37.vcf ~/db/1000G_phase1.snps.high_confidence.b37.vcf.idx ~/db/dbsnp_138.b37.vcf
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
		-tranchesFile "$*.raw.vcf.SNP.tranches"
%.raw.vcf.SNP.tranches: %.raw.vcf.SNP.recal
	touch $@

# TODO FIXME if nbSamples > 10 and unrelated, add -an InbreedingCoeff

# Apply VQSR model for SNPs
%.snp_recalibrated.vcf: %.raw.vcf %.raw.vcf.SNP.recal %.raw.vcf.SNP.tranches ~/db/human_g1k_v37.fasta
	$(GATK) \
		-T ApplyRecalibration \
		-mode SNP \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		--ts_filter_level 99.5 \
		-recalFile "$*.raw.vcf.SNP.recal" \
		-tranchesFile "$*.raw.vcf.SNP.tranches" \
		-o $@

# Compute VQSR model for indels
%.raw.vcf.indels.recal: %.raw.vcf ~/db/human_g1k_v37.fasta ~/db/Mills_and_1000G_gold_standard.indels.b37.vcf ~/db/dbsnp_138.b37.vcf
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
		-tranchesFile "$*.raw.vcf.indels.tranches"
%.raw.vcf.indels.tranches: %.raw.vcf.indels.recal
	touch $@

# Apply VQSR model for SNPs
%.all_recalibrated.vcf: %.snp_recalibrated.vcf %.raw.vcf.indels.recal %.raw.vcf.indels.tranches ~/db/human_g1k_v37.fasta
	$(GATK) \
		-T ApplyRecalibration \
		-mode INDEL \
		-R ~/db/human_g1k_v37.fasta \
		-input $< \
		--ts_filter_level 99.0 \
		-recalFile "$*.vcf.indels.recal" \
		-tranchesFile "$*.vcf.indels.tranches" \
		-o $@

# Filter variants on VQSR results
%.vcf: %.all_recalibrated.vcf ~/db/human_g1k_v37.fasta
	$(GATK) \
		-nt $(THREADS) \
		-T SelectVariants \
	                -env \
		-R ~/db/human_g1k_v37.fasta \
		-V $< \
		-o $@
