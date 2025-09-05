import csv, copy
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

	sforms = cedict_data['cedict_s']
	tforms = cedict_data['cedict_t']
	tforms = set(t for s, t in zip(sforms, tforms) if s != t)

	ambigs = defaultdict(list)
	for x, y in (*cedict_data['cedict_pairs_ambig'], *cedict_data['multipair_monochar']):
		ambigs[x].append(y)

	singles = cedict_data['one_on_one_singles']
	singles.extend(cedict_data['cedict_singles'])
	singles = set(singles)

	monopairs = dict(cedict_data['one_on_one_pairs'])
	monopairs.update(dict(cedict_data['cedict_pairs']))
	monopairs.update(dict(cedict_data['multipair_word_pairs']))
	monopairs = {x: y for x, y in monopairs.items() if x not in cedict_pairs_ambig.keys()}
	# monopairs_simp = set(monopairs.keys())
	
	print('CEDICT data prepared')
	
	catalogue = ('singles', 'monopairs', 'ambigs', 'tforms',
			  'multipair_chars', 
			  'multipair_word_pairs',
			  'cedict_pairs_ambig', 'cedict_t')
	return {x: locals().get(x, None) for x in catalogue}

def get_freqdict(cedict_data, freqlist_fp):

	output = defaultdict(int)
	output_ambiguous, output_ambiguous2, output_t = defaultdict(int), defaultdict(int), defaultdict(int)
	orig_freqlist = defaultdict(int)

	def wordlist_feeder(word, wordlist, verbose=False):

		entry = list()

		tchars = cedict_data['monopairs'].get(word, '')
		if tchars:
			word = parse_string_with_unicode(word)
			tchars = parse_string_with_unicode(tchars)
			entry.extend(zip(word, tchars, ''))

		else:
		
			for char in parse_string_with_unicode(word):
				tchar = ''

				if char in cedict_data['singles']:
					tchar = char

				elif not tchar:
					tchar = cedict_data['monopairs'].get(char, '')
					if tchar:
						entry.append((char, tchar, ''))
					else:
						if word in cedict_data['cedict_pairs_ambig']:
							entry.append((f'{char}', '*!!', ' '.join(cedict_data['ambigs'].get(word, [word]))))
				
				if tchar:
					entry.append((char, tchar, ''))

		if False:	# '' in entry
			entry = list()
		else:
			for c in entry:
				wordlist.append(c)
		return entry
	
	with open(freqlist_fp, 'r', encoding='utf-8', newline='') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')

		for row in tqdm(myreader):
		# for row in (('茶几','14716'), ):

			word, freq = row
			freq = int(freq)
			
			for char in parse_string_with_unicode(word):
				orig_freqlist[char] += freq
				
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
											ent = (f'{char}', '*??', f'{' '.join(cedict_data['ambigs'].get(char, char))}')
											wordlist.append(ent)
											output_ambiguous[char] += freq
										elif char in cedict_data['tforms']:
											output_t[char] += freq
										else:
											output_ambiguous2[char] += freq

			for entry in wordlist:
				output[entry] += freq

	c = lambda s, t : t if s != t else ''
	freq2 = lambda s, t : 0 if s == t else orig_freqlist.get(t, 0)
	output = [(s, c(s, t), misc, freq, freq2(s, t)) for (s, t, misc), freq in tqdm(output.items())]	

	return output, output_ambiguous, output_ambiguous2, output_t, orig_freqlist

def query_freqdict(data: dict):
	return {x for x in data if '*' in x[1]}

def main():

	from directories import cedict_fp, freqlist_fp
	from src.write_bulk_to_file import write_bulk_to_file
	
	cedict_data = get_cedict_data(cedict_fp)
	cedict_data = group_cedict_data(cedict_data)

	freqdict, amb, amb2, freqdict_t, orig_freqlist = get_freqdict(cedict_data, freqlist_fp)
	freqdict_query = query_freqdict(freqdict)

	fps_names = ('freqdict', 'freqdict_query', 'freqdict_t', 'amb', 'amb2', 'orig_freqlist',)
	fps = [f'output/freqlist/{x}.tsv' for x in fps_names]
	datas = [freqdict, freqdict_query, freqdict_t, amb, amb2, orig_freqlist,]

	write_bulk_to_file(fps, datas)

