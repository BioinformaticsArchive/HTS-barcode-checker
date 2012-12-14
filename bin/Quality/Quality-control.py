#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil filter the blast results on E-value and bit-score.

coverage 95%
identity 97%

dependencies:
Bio python
'''
from Bio.Blast import NCBIXML
import os
import sys

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all nececary files
'''
result_handle = open(sys.argv[1], "r") # this gets input in an xml format from blast

E_VALUE_THRESH = 0.04
MIN_IDENT = 97
MIN_COVER = 95
result_list = []

for blast_record in NCBIXML.parse(result_handle):
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01))# this calculates the % identeties and % coverage of the current alignment
            cover = float(len(hsp.match)/(len(hsp.query)*0.01))
            # an alignment needs to meet 3 criteria before we consider it an acceptable result: above the minimum identitie, minimu coverage and E-value
            if hsp.expect < E_VALUE_THRESH and ident > MIN_IDENT and cover > MIN_COVER:
                result_list.append(alignment.title)
                #result_list.append(alignment.hit_id)
                #result_list.append(alignment.hit_def)
                result_list.append(';')#the ; marks the end of a title and is used to split the list into seperate titles in the output script
                

#os.system("rm my_blast_filterd.txt")
#save_file = open("my_blast_filterd.txt", "a")
for line in result_list:
    #save_file.write(line + '\n')
    sys.stdout.write(str(line))
#save_file.close
#result_handle.close()