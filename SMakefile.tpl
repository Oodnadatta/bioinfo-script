smake_version: {{ version }}
root: {{ root }}
rules:
{% for vcf, fastqs in rules.items() %}
  {{ vcf }}:
    fastq1: {{ fastqs['fastq1'] }}
    fastq2: {{ fastqs['fastq2'] }}
{% endfor %}
