import csv, copy
import ahocorasick
from tqdm import tqdm
from collections import defaultdict

from src.parse_string_unic import parse_string_with_unicode

def build_automaton(keywords):
	# ChatGPT-generated
	automaton = ahocorasick.Automaton()
	for idx, word in enumerate(keywords):
		automaton.add_word(word, (idx, word))
	automaton.make_automaton()
	return automaton

def screen_text(text: str, automaton) -> bool:
	# ChatGPT-generated, edited
	text = text.strip()
	return any(True for _ in automaton.iter(text))

def get_pairs(cedict_fp):

	multipair_word = defaultdict(list)
	data_monochar, data_words = list(), list()
	tmonochar_count = defaultdict(int)
	multipair_var, multipair_var2 = list(), list()
	
	keywords = ('variant of', '/used in')
	ahocorasick_automaton = build_automaton(keywords)

	with open(cedict_fp, 'r', encoding='utf-8') as f:

		for i, row in tqdm(enumerate(f)):
			if not row.startswith('#'):
				row = row.replace('[', '\t[', 1).replace(']', ']\t', 1)

				if len(row) < 3:
					print('\t'.join((str(i), '!!', *row)))
				
				else:
					tword_sword, pinyin, glosses, *_ = row.strip().split('\t')
					tword_sword = tword_sword.strip()

					if tword_sword.count(' ') != 1:
						print(' '.join((str(i), '!!', *row)))

					else:
						tword, sword = tword_sword.split(' ')
						tchars = parse_string_with_unicode(tword)
						schars = parse_string_with_unicode(sword)

						if len(tchars) != len(schars):
							print('\t'.join((str(i), '>>' *row)))

						else:	
							if len(tword) == 1:
								if screen_text(glosses, ahocorasick_automaton):
									multipair_var.append((i, sword, tword, glosses))						
								else:
									tmonochar_count[tword] += 1
									data_monochar.append((i, sword, tword, glosses))

							else:
								if screen_text(glosses, ahocorasick_automaton):
									multipair_var2.append((i, sword, tword, glosses))
								else:
									data_words.append((i, sword, tword, glosses))				
									for s, t in zip(schars, tchars):
										multipair_word[(s, t)].append((sword, tword, s, t))
								
		
		multipair_word2 = defaultdict(list)
		for (s, t), word_pairs in multipair_word.items():
			multipair_word2[s].append((t, len(word_pairs), word_pairs))
		multipair_word = multipair_word2

		# tchar
		# {tchar: {'count': len(words), 'words': words}}

		# Filter out duplicates etc.

		data_words = [(s, t) for i, s, t, glosses in data_words]
		data_words = list(dict.fromkeys(data_words))
		
		schars = [sword for sword, tword in multipair_monochar]
		multipair_schars = list(schars)	# list() creates copy of list

		for entry in tqdm(set(schars)):
			multipair_schars.remove(entry)
		one_on_one = [(s, t) for s, t in multipair_monochar if s not in multipair_schars]
		one_on_one_pairs = ([(s, t) for s, t in one_on_one if s != t])
		one_on_one_singles = [s for s, t in one_on_one if s == t]

		data_monochar = [(s, t) for i, s, t, glosses in data_monochar]
		data_monochar = list(dict.fromkeys(data_monochar))
		multipair_monochar = [(sword, tword) for sword, tword in tqdm(data_monochar) 
							if sword in multipair_schars]

		multipair_word = {schar : tchar_tups for schar, tchar_tups 
							in tqdm(multipair_word.items()) if schar in multipair_schars}
							# len(tchar_tups) > 1
		
		multipair_word_pairs = list()
		for tchar_tups in multipair_word.values():
			for x in tchar_tups:
				word_pair = x[2]
				multipair_word_pairs.extend(word_pair)

		multipair_word_pairs_simp = [s for s, t, *_ in multipair_word_pairs]

		for entry in tqdm(set(multipair_word_pairs_simp)):
			multipair_word_pairs_simp.remove(entry)
		multipair_word_pairs = [(s, t) for s, t, *_ in multipair_word_pairs if s not in multipair_word_pairs_simp]
		multipair_word_pairs_ambig = [(s, t) for s, t, *_ in multipair_word_pairs if s in multipair_word_pairs_simp]

		one_on_one_words = [x for x in data_words if x not in multipair_word_pairs]
		one_on_one_words_pairs = ([(s, t) for s, t in one_on_one if s != t])
		one_on_one_words_singles = [s for s, t in one_on_one if s == t]

		output = (multipair_word, multipair_word_pairs, multipair_word_pairs_ambig, 
				multipair_monochar, multipair_var, multipair_var2, 
				one_on_one_pairs, one_on_one_singles,
				one_on_one_words_pairs, one_on_one_words_singles,)

		return {f'{x}': x  for x in output}
	
def main():

	from directories import cedict_fp
	from src.write_bulk_to_file import write_bulk_to_file

	fps = {f'data/output/{x}.tsv' for x in get_pairs(cedict_fp).keys()}
	datas = get_pairs(cedict_fp).values()
	write_bulk_to_file(fps, datas)



			 
