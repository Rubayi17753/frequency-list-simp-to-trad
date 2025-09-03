import csv
import jieba
from collections import defaultdict
from tqdm import tqdm

from directories import cedict_fp, freqlist_fp
from src.process_cedict import get_pairs

def read_cedict(cedict_fp):
	...

def main():

	output = defaultdict(int)
	cedict_data = read_cedict(cedict_fp)

	with open(freqlist_fp, 'r', encoding='utf-8', newline='') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')
		for row in tqdm(myreader):

			word, freq = row
			simp_seqs = list()

			if word in cedict_data:
				simp_seqs.append(word)
			else:
				simp_seqs.append(*[x for x in jieba.cut(word)])

			multipairs_words, multipairs_monochar = get_pairs()


						

					


