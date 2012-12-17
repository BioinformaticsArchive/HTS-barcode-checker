#!/usr/bin/python2.7
'''
Created on 22 Nov. 2012

Author: Alex Hoogkamer
E-mail: aqhoogkamer@outlook.com / s1047388@student.hsleiden.nl

this script wil filter the blast results on E-value and bit-score.

default minimum coverage: 95%
default minimum identity : 97%

dependencies:
Bio python
Unix OS
'''
from Bio.Blast import NCBIXML
import os
import sys

'''
here the current working directory is saved
and the directories containing the script is
removed. the result is the directory in which
the all necessary files are placed
'''
filename       = sys.stdin.readline()
result_handle  = open(filename, "r")                       # this gets input in an xml format from blast

E_VALUE_THRESH = sys.argv[1]
MIN_IDENT      = sys.argv[2]
MIN_COVER      = sys.argv[3]
result_list    = []

for blast_record in NCBIXML.parse(result_handle):
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            ident = float(hsp.identities/(len(hsp.match)*0.01))# this calculates the % identities and % coverage of the current alignment
            cover = float(len(hsp.match)/(len(hsp.query)*0.01))
                                                               # an alignment needs to meet 3 criteria before we consider it an acceptable result: above the minimum identity, minimum coverage and E-value
            if hsp.expect < E_VALUE_THRESH and ident > MIN_IDENT and cover > MIN_COVER:
                result_list.append(alignment.title)
                result_list.append(';')                        #the ; marks the end of a title and is used to split the list into seperate titles in the output script
                
for line in result_list:
    sys.stdout.write(str(line))