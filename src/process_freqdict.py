import csv
import jieba
import pdb
from collections import defaultdict
from tqdm import tqdm

from src.parse_string_unic import parse_string_with_unicode
from src.process_cedict import get_cedict_data

def group_cedict_data(cedict_data):

	multipair_word_pairs = dict(cedict_data['multipair_word_pairs'])
	cedict_pairs_ambig = dict(cedict_data['cedict_pairs_ambig'])
	multipair_chars = dict(cedict_data['multipair_monochar'])

	singles = cedict_data['one_on_one_singles']
	singles.extend(cedict_data['cedict_singles'])
	singles = set(singles)

	monopairs = dict(cedict_data['one_on_one_pairs'])
	monopairs.update(dict(cedict_data['cedict_pairs']))
	monopairs.update(dict(cedict_data['multipair_word_pairs']))
	monopairs = {x: y for x, y in monopairs.items() if x not in cedict_pairs_ambig.keys()}
	# monopairs_simp = set(monopairs.keys())

	print('CEDICT data prepared')
	
	catalogue = ('singles', 'monopairs', 
			  'multipair_chars', 
			  'multipair_word_pairs', 'cedict_pairs_ambig')
	return {x: locals().get(x, None) for x in catalogue}

def get_freqdict(cedict_data, freqlist_fp):

	output = defaultdict(int)
	output_ambiguous, output_ambiguous2 = defaultdict(list), defaultdict(list)

	def wordlist_feeder(word, wordlist, verbose=False):

		entry = list()

		tchars = cedict_data['multipair_word_pairs'].get(word, '')

		if word in cedict_data['cedict_pairs_ambig']:
			for char in parse_string_with_unicode(word):
				tchar = cedict_data['monopairs'].get(char, '')
				if tchar:
					entry.append((char, tchar))
				else:
					entry.append((f'{char}*', f'! {word}'))

		elif tchars:
			word = parse_string_with_unicode(word)
			tchars = parse_string_with_unicode(tchars)
			entry.extend(zip(word, tchars))

		else:
			for char in parse_string_with_unicode(word):

				tchar = ''
				tchars = ''

				if char in cedict_data['singles']:
					tchar = char
				elif not tchar:
					tchar = cedict_data['monopairs'].get(char, '')
				else:
					tchar = '!!'

				if tchar:
					entry.append(((char, tchar)))

		if '!!' in entry:
			entry = list()
		else:
			for c in entry:
				wordlist.append(c)

		return entry
	
	with open(freqlist_fp, 'r', encoding='utf-8', newline='') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')
		for row in tqdm(myreader):

			word, freq = row
			wordlist = list()

			if not wordlist_feeder(word, wordlist):
				for seq in jieba.cut(word):
					if not wordlist_feeder(seq, wordlist):
						for subseq in jieba.cut(word):
							if not wordlist_feeder(subseq, wordlist):
								for char in parse_string_with_unicode(subseq):
									entry = wordlist_feeder((char,), wordlist)
									if not entry:
										if char in cedict_data['multipair_chars']:
											ent = (f'{char}*', '?')
											wordlist.append(ent)
											output_ambiguous[char].append(word)
										else:
											output_ambiguous2[char].append(word)

			for entry in wordlist:
				output[entry] += int(freq)

	return output, output_ambiguous, output_ambiguous2

def main():

	from directories import cedict_fp, freqlist_fp
	from src.write_bulk_to_file import write_bulk_to_file
	
	cedict_data = get_cedict_data(cedict_fp)
	cedict_data = group_cedict_data(cedict_data)

	freqdict, amb, amb2 = get_freqdict(cedict_data, freqlist_fp)

	fps_names = ('freqdict', 'amb', 'amb2')
	fps = [f'output/freqlist/{x}.tsv' for x in fps_names]
	datas = [freqdict, amb, amb2,]

	write_bulk_to_file(fps, datas)

