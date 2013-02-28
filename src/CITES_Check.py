#!/usr/bin/env python

# descrip


# import the argparse module to handle the input commands
import argparse

# get the commandline arguments that specify the input fastafile and the output file
parser = argparse.ArgumentParser(description = ('Identify a set of sequences and check if there are CITES species present'))

parser.add_argument('-i', '--input_file', metavar='fasta file', dest='i', type=str, 
			help='enter the fasta file')
parser.add_argument('-o', '--output_file', metavar='output file', dest='o', type=str, 
			help='enter the output file')
parser.add_argument('-ba', '--BLAST_algorithm', metavar='algorithm', dest='ba', type=str, 
			help='Enter the algorithm BLAST wil use (default=blastn)', default='blastn')
parser.add_argument('-bd', '--BLAST_database', metavar='database', dest='bd', type=str,
			help = 'Enter the database BLAST wil use (default=nt)', default = 'nt')
parser.add_argument('-hs', '--hitlist_size', dest='hs', type=int,
			help = 'Enter the size of the hitlist BLAST wil return (default=1)', default = 1)
parser.add_argument('-mb', '--megablast', dest='mb', action='store_true', 
			help = 'Use megablast, can only be used in combination with blastn')
parser.add_argument('-mi', '--min_identity', dest='mi', type=int, 
			help = 'Enter the minimal identity for BLAST results', default = 97)
parser.add_argument('-mc', '--min_coverage', dest='mc', type=int, 
			help = 'Enter the minimal coverage for BLAST results', default = 100)
parser.add_argument('-me', '--max_evalue', dest='me', type=float, 
			help = 'Enter the minimal E-value for BLAST results', default = 0.05)
parser.add_argument('-bl', '--blacklist', metavar='blacklist file', dest='bl', type=str,
			help = 'File containing the blacklisted genbank id\'s', default='')
parser.add_argument('-cd', '--CITES_db', metavar='CITES database file', dest='cd', type=str,
			help = 'Path to the local copy of the CITES database')
parser.add_argument('-fd', '--force_download', dest='fd', action='store_true',
			help = 'Force the update of the local CITES database')
parser.add_argument('-ad', '--avoid_download', dest='ad', action='store_true',
			help = 'Avoid updating the local CITES database')

args = parser.parse_args()

def blast_bulk ():

	# The blast modules are imported from biopython
	from Bio.Blast import NCBIWWW, NCBIXML
	from Bio import SeqIO
	
	# parse the fasta file and get a list of sequences
	seq_list = [seq for seq in SeqIO.parse(args.i, 'fasta')]

	blast_list = []

	# for each sequence obtain the blast result
	for seq in seq_list:
		result_handle = NCBIWWW.qblast(args.ba, args.bd, seq.format('fasta'), megablast=args.me, hitlist_size=args.hs)
		blast_list.append(NCBIXML.read(result_handle))
	
	return blast_list


def get_blacklist ():
	
	# return a list containing the blacklisted genbank id's
	# the blacklist follows the following format:
	# genbank_id, description
	try:
		return [line for line in open(args.bl,'r')]
	except:
		return []


def get_CITES ():
	
	# import the subporcess module to run the 
	# Retieve_CITES script from the shell
	from subprocess import call
	
	if args.fd == True:
		path = call(['./Retrieve_CITES.py', '-db', args.cd, '-f'])
	else:
		path = call(['./Retrieve_CITES.py', '-db', args.cd])



def get_CITES_dic ():
	
	# open the local CITES database, return a dictionary
	# containing the CITES information with the taxid's as keys

	CITES_dic = {}
	
	for line in open(args.cd, 'r'):
		line = line.rstrip().split(',')
		if line[0] != 'Date':
			CITES_dic[line[0]] = line[1:]

	return CITES_dic


def parse_blast (blast_list, CITES_dic, blacklist, mode):
	
	# parse_through the blast results and remove
	# results that do not meet the e-value, coverage,
	# identity and blacklist critera

	from Bio.Blast import NCBIWWW, NCBIXML

	for blast_result in blast_list:
		for alignment in blast_result.alignments:
			for hsp in alignment.hsps:
	            		
				# calculate the %identity
		            	identity = float(hsp.identities/(len(hsp.match)*0.01))

				# grab the genbank number
				gb_num = alignment.title.split('|')[1]
				
				# an alignment needs to meet 3 criteria before 
				# it is an acceptable result: above the minimum 
				# identity, minimum coverage and E-value
			
				# create containing the relevant blast results
				# pass this list to the filter_hits function to
				# filter and write the blast results
				filter_hits([('\"' + blast_result.query + '\"'), ('\"' + alignment.title + '\"'), gb_num, str(identity),
						str(blast_result.query_length), str(hsp.expect), str(hsp.bits)], CITES_dic, blacklist, mode)


def obtain_tax (code):
	
	# a module from Biopython is imported to connect to the Entrez database
	from Bio import Entrez
	from Bio import SeqIO

	taxon = [[],[]]

	try:
		# based on the genbank id the taxon id is retrieved from genbank
		Entrez.email = "quick@test.com"
		handle = Entrez.efetch(db="nucleotide", id= code, rettype="gb",retmode="text")
		record = SeqIO.read(handle, "gb")

		# parse through the features and grap the taxon_id
		sub = record.features
		taxon[0] = sub[0].qualifiers['db_xref'][0].split(':')[1]
		taxon[1] = record.annotations['organism']

	except:
		pass

	return taxon


def filter_hits (blast, CITES_dic, blacklist, mode):
	
	# filter the blast hits, based on the minimum
	# identity, minimum coverage, e-value and the user blacklist
	if float(blast[3]) >= args.mi and int(blast[4]) >= args.mc and float(blast[5]) <= args.me:
		if blast[2] not in blacklist:
			taxon = obtain_tax(blast[2])
			results = blast+taxon

			# check if the taxon id of the blast hit
			# is present in the CITES_dic
			if taxon[0] in CITES_dic:			
				results+CITES_dic[taxon[0]]
			
			# write the results
			write_results(','.join(results), mode)
			
			

def write_results (result, mode):
	
	# write the results to the output file
	out_file = open(args.o, mode)
	out_file.write(result + '\n')
	out_file.close()


def main ():

	# Check if there is a more recent CITES list online
	if args.ad != True:
		get_CITES()

	# create a dictionary containing the local CITES set	
	CITES_dic = get_CITES_dic()

	# create a list with the blacklisted genbank ids
	blacklist = get_blacklist()

	# create a blank result file and write the header
	header = 'query,hit,accession,identity,hit length,e-value,bit-score,taxon id,genbank record species,CITES species,CITES info,NCBI Taxonomy name,appendix'
	write_results(header, 'w')

	# blast the fasta file
	blast_list = blast_bulk()

	# parse through the results and write the blast hits + CITES info
	parse_blast(blast_list, CITES_dic, blacklist, 'a')
	

if __name__ == "__main__":
    main()

