import csv, yaml
from src.process_cedict import get_pairs, query_multipair
from filepaths import cedict_fp, multipair_fp, output_var_fp

def main():

	output, output_var = get_pairs(cedict_fp)
	output = query_multipair(output)

	with open(multipair_fp, 'w', encoding='utf-8', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='\t')
		spamwriter.writerows(output.items())

	with open(output_var_fp, 'w', encoding='utf-8', newline='') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='\t')
		spamwriter.writerows(output_var)