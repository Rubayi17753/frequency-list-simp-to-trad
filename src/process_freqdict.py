import csv
import jieba
from collections import defaultdict
from tqdm import tqdm

from src.process_cedict import get_pairs

def get_freqdict(cedict_extracted, freqlist_fp):

	output = defaultdict(int)

	(multipair_word, multipair_word_pairs, multipair_word_pairs_ambig, 
	multipair_monochar, multipair_var, multipair_var2, 
	one_on_one_pairs, one_on_one_singles) = cedict_extracted

	one_on_one_singles = set(one_on_one_singles)

	one_on_one_pairs = dict(one_on_one_pairs)
	one_on_one_pairs_simp = set(one_on_one_pairs.keys())

	multipair_word_pairs = dict(multipair_word_pairs)
	multipair_word_pairs_simp = set(multipair_word_pairs.keys())

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

def write_bulk_to_file(data):

	from directories import cedict_fp, freqdict_target_fp
		
	with open(freqdict_target_fp, 'w', encoding='utf-8', newline='') as f:
		print(f'Writing to {freqdict_target_fp}')
		spamwriter = csv.writer(f, delimiter='\t')
		if type(data) == dict:
			spamwriter.writerows(data.items())
		else:
			spamwriter.writerows(data)
		# yaml.dump(output_word, f, allow_unicode=True)


def main():

	from directories import cedict_fp, freqlist_fp, freqdict_target_fp
	
	fps = freqdict_target_fp
	cedict_extracted = get_pairs(cedict_fp)
	datas = get_freqdict(cedict_extracted, freqlist_fp)
	write_bulk_to_file(fps, datas)

