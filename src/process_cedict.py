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
	# ChatGPT-generated
	return any(True for _ in automaton.iter(text))

def get_pairs(cedict_fp):

	multipair_word = defaultdict(list)
	tmonochar_count = defaultdict(int)
	multipair_monochar = list()
	
	keywords = ('variant', 'used in')
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
								tmonochar_count[tword] += 1
								multipair_monochar.append((i, tword, sword, glosses))
							elif True:
							# elif not screen_text(glosses, ahocorasick_automaton):
								for tchar, schar in zip(tchars, schars):
									multipair_word[(tchar, schar)].append((tword, sword))
							else:
								multipair_var.append((i, tword, sword, glosses))
		
		multipair_word2 = defaultdict(list)
		for (tchar, schar), word_pairs in multipair_word.items():
			multipair_word2[schar].append((tchar, len(word_pairs)))
		multipair_word = multipair_word2

			# tchar
			# {tchar: {'count': len(words), 'words': words}}

		# Filter out duplicates etc.

		multipair_word = {schar : tchar_tups for schar, tchar_tups in tqdm(multipair_word.items()) 
							if len(tchar_tups) > 1}
		
		multipair_word_pair = list()
		for tchar_tups in multipair_word.values():
			multipair_word_pair.extend(tchar_tups)
		
		multipair_monochar = [(tword, sword) for i, tword, sword, glosses in multipair_monochar]
		multipair_monochar = list(dict.fromkeys(multipair_monochar))
		
		sword_list = [sword for tword, sword in multipair_monochar]
		for entry in set(sword_list):
			sword_list.remove(entry)	

		multipair_monochar = [(tword, sword) for tword, sword in tqdm(multipair_monochar) 
							if sword in sword_list]
		
		return multipair_word, multipair_word_pair, multipair_monochar


def write_to_file():

	from directories import cedict_fp
	from directories import multipair_word_fp, multipair_word_pair_fp, multipair_monochar_fp
	fps = multipair_word_fp, multipair_word_pair_fp, multipair_monochar_fp
	
	for fp, data in zip(fps, get_pairs(cedict_fp)):
		with open(fp, 'w', encoding='utf-8', newline='') as f:
			print(f'Writing to {fp}')
			spamwriter = csv.writer(f, delimiter='\t')
			spamwriter.writerows(data.items())		
			# yaml.dump(output_word, f, allow_unicode=True)

	



			 
