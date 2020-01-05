#! /usr/bin/env python3

# Anne-Sophie Denommé-Pichon
# 2020-01-04
# Script to get SNPs genotype by pedigree from LabKey export in xlsx

import openpyxl

if __name__ == '__main__':
    input_wb = openpyxl.load_workbook(r"C:\Users\asden\Desktop\Genotypage sample_2020-01-04_21-36-01.xlsx") #FIXME : make name of file generic
    ws = input_wb['data']

    # Create an object (json like) to store the values extracted from the xlsx.
    #{
    #    'PED7699.1': {
    #        '18069': {
    #            '2010-01-02': {
    #                'SNP10_rs9530': 'A/G',
    #                'SNP11_rs20583': 'C/T'
    #            }
    #        }
    #    }
    #}

    values = {}
    snps = set()

    for row in ws.rows:
        if row[0].value.startswith('PED7699'): #FIXME : make name of PED generic
            snps.add(row[3].value)
            ped = values.setdefault(row[0].value, {})
            gad = ped.setdefault(str(row[14].value), {}) #FIXME : remove float type to GAD
            date = gad.setdefault(row[16].value, {})
            ## Genotype
            date[row[3].value] = row[9].value
    snps_names = sorted(snps)
 
    # Create an xslx file to sumarize genotypes by PED number.
    output_wb = openpyxl.Workbook()
    ws = output_wb.active

    ## SNPs
    for index, snp in enumerate(snps_names):
        ws.cell(column=1, row=index + 4, value=snp)
    ## PED
    patient_column = 2
    for ped, gads in values.items(): #FIXME : sort by .2 .1 .3
        ws.cell(column=patient_column, row=1, value=ped)
        ## GAD
        for gad, dates in gads.items():
            ws.cell(column=patient_column, row=2, value=gad)
            ## Date
            for date, genotypes in dates.items():
                ws.cell(column=patient_column, row=3, value=date)
                ## Genotype
                for index, snp in enumerate(snps_names):
                    ws.cell(column=patient_column, row=index + 4, value=genotypes[snp])
                patient_column = patient_column + 1

    ws.column_dimensions['A'].width = 15.7
    for column in range(ord('B'), ord('Z')):
        ws.column_dimensions[chr(column)].width = 10
    
    output_wb.save(r"C:\Users\asden\Desktop\PED7699.xlsx")
