import csv
import jieba
from collections import defaultdict
from tqdm import tqdm

from src.process_cedict import get_pairs

def get_freqdict(cedict_extracted, freqlist_fp):

	output = defaultdict(int)

	one_on_one_singles = set(cedict_extracted['one_on_one_singles'])

	one_on_one_pairs = dict(cedict_extracted['one_on_one_pairs'])
	one_on_one_pairs_simp = set(one_on_one_pairs.keys())

	multipair_word_pairs = dict(cedict_extracted['multipair_word_pairs'])
	multipair_word_pairs_simp = set(multipair_word_pairs.keys())

	multipair_word = cedict_extracted['multipair_word']
	# not a very big dict

	def wordlist_feeder(word, wordlist, verbose=False):

		entry = ''
		if word in one_on_one_singles:
			entry = word
		elif word in one_on_one_pairs_simp:
			entry = one_on_one_pairs[word]
		elif word in multipair_word_pairs_simp:
			entry = multipair_word_pairs[word]
		elif word in multipair_word:
			entry = f'{multipair_word}*'
		elif verbose:
			print(f'!! {word}')
		
		wordlist.append(entry)
		return entry

	with open(freqlist_fp, 'r', encoding='utf-8', newline='') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')
		for row in tqdm(myreader):

			word, freq = row
			wordlist = list()

			if not wordlist_feeder(word, wordlist):
				for seq in jieba.cut(word):
					wordlist_feeder(seq, wordlist, verbose=True)

			for entry in wordlist:
				output[entry] += int(freq)

	return output

def main():

	from directories import cedict_fp, freqlist_fp, freqdict_target_fp
	from src.write_bulk_to_file import write_bulk_to_file
	
	fps = [freqdict_target_fp,]
	cedict_extracted = get_pairs(cedict_fp)
	datas = [get_freqdict(cedict_extracted, freqlist_fp),]
	write_bulk_to_file(fps, datas)

