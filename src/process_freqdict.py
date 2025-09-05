import csv
import jieba
import pdb
from collections import defaultdict
from tqdm import tqdm

from src.parse_string_unic import parse_string_with_unicode
from src.process_cedict import get_cedict_data

def group_cedict_data(cedict_data):

	singles = cedict_data['one_on_one_singles']
	singles.extend(cedict_data['cedict_singles'])
	singles_simp = set(singles)

	monopairs = dict(cedict_data['one_on_one_pairs'])
	monopairs.update(dict(cedict_data['cedict_pairs']))
	monopairs.update(dict(cedict_data['multipair_word_pairs']))
	monopairs_simp = set(monopairs.keys())

	multipair_chars = dict(cedict_data['multipair_monochar'])
	# not a very big dict

	print('CEDICT data prepared')
	
	catalogue = ('singles', 'monopairs', 'multipair_chars', 'singles_simp', 'monopairs_simp')
	return {x: locals().get(x, None) for x in catalogue}

def get_freqdict(cedict_data, freqlist_fp):

	output = defaultdict(int)
	output_ambiguous = defaultdict(list)

	def wordlist_feeder1(word, wordlist, verbose=False):

		entry = list()
		for char in parse_string_with_unicode(word):
			if char in cedict_data['singles_simp']:
				entry = char
			elif char in cedict_data['monopairs_simp']:
				entry = cedict_data['monopairs'][char]
			else:
				entry = '!!'	
		
		if '!!' in entry:
			entry = list()
		else:
			for char in entry:
				wordlist.append(entry)

		return entry
	
	with open(freqlist_fp, 'r', encoding='utf-8', newline='') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')
		for row in tqdm(myreader):

			word, freq = row
			wordlist = list()

			if not wordlist_feeder1(word, wordlist):
				for seq in jieba.cut(word):
					if not wordlist_feeder1(seq, wordlist):
						for subseq in jieba.cut(word):
							if not wordlist_feeder1(seq, wordlist):
								for char in parse_string_with_unicode(subseq):
									entry = wordlist_feeder1(char, wordlist)
									if not entry:
										ent = f'{char}*'
										wordlist.append(ent)
										output_ambiguous[char].append(word)

			for entry in wordlist:
				output[entry] += int(freq)

	return output, output_ambiguous

def main():

	from directories import cedict_fp, freqlist_fp
	from src.write_bulk_to_file import write_bulk_to_file
	
	cedict_data = get_cedict_data(cedict_fp)
	cedict_data = group_cedict_data(cedict_data)

	freqdict, freqdict_amb = get_freqdict(cedict_data, freqlist_fp)

	fps_names = ('freqdict', 'freqdict_amb')
	fps = [f'output/freqlist/{x}.tsv' for x in fps_names]
	datas = [freqdict, freqdict_amb,]

	write_bulk_to_file(fps, datas)

