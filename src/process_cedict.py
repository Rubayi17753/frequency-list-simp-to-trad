import csv, copy
import ahocorasick
from tqdm import tqdm
import pandas as pd
from collections import defaultdict, Counter
from itertools import chain

from directories import cedict_fp

def build_automaton(keywords):
	# ChatGPT-generated
	automaton = ahocorasick.Automaton()
	for idx, word in enumerate(keywords):
		automaton.add_word(word, (idx, word))
	automaton.make_automaton()
	return automaton

keywords = ('old variant of', 'Japanese variant of','variant of', 'surname')
automaton = build_automaton(keywords)
def screen_text(text: str) -> bool:
	# ChatGPT-generated, edited
	text = text.strip()
	return any(True for _ in automaton.iter(text))

def preprocess(df, mode='s2t'):

	df = df[~df['cedict_raw'].str.startswith('#')].copy()
	df['cedict_raw'] = df['cedict_raw'].str.replace(' [', '`[', n=1, regex=False)
	df['cedict_raw'] = df['cedict_raw'].str.replace('] /', ']`/', n=1, regex=False)
	
	print('Splitting fields')
	df[['word_pairs', 'pinyin', 'glosses']] = df['cedict_raw'].str.split('`', expand=True)
	df[['word_t', 'word_s']] = df['word_pairs'].str.split(' ', expand=True)
	df['pinyin'] = df['pinyin'].apply(lambda x: x.strip('[').strip(']'))
	df['glosses'] = df['glosses'].str.strip('/')
	df['glosses'] = df['glosses'].str.split('/', expand=False)
	del df['cedict_raw']

	print('Explode')
	df = df.explode('glosses').copy()

	print('Removing old variants')
	# mask = df['glosses'].apply(screen_text)

	var_dfs = list()
	for keyword in keywords:
		mask = df['glosses'].apply(lambda x: x.startswith(keyword))
		var_df  = df[mask]
		df = df[~mask].copy()
		var_dfs.append(var_df)

	print('Agreggate entries')
	df = df.groupby(['word_t', 'word_s']).agg(
        pinyin=('pinyin', list),
        glosses=('glosses', list),
        ).reset_index()
	
	df['count_t'] = df.groupby('word_t')['word_t'].transform('count')
	df['count_s'] = df.groupby('word_s')['word_s'].transform('count')

	print('Calculating lengths')
	df['len_t'] = df['word_t'].apply(len)
	df['len_s'] = df['word_s'].apply(len)

	return df, var_dfs

def create_charlist(df):

	df['chars_t'] = df['word_t'].apply(list)
	df['chars_s'] = df['word_s'].apply(list)
	df = df.explode(['chars_t', 'chars_s'])
	df = df.rename(columns={
    'chars_t': 'char_t',
    'chars_s': 'char_s'
	})

	df = df.groupby(['char_t', 'char_s']).agg(
        count_t=('char_t', 'count'),
        count_s=('char_s', 'count'),
        ).reset_index()
	
	return df

def main():

	df = pd.read_csv(cedict_fp, sep='\t', header=None, names=['cedict_raw'])
	df, var_dfs = preprocess(df)

	def write():
		fp = 'output/cedict/data_main.tsv'
		print(f'Writing to {fp}')
		df.to_csv(fp, sep='\t', index=False)

	def write_var():
		for keyword, var_df in zip(keywords, var_dfs):
			fp = f'output/cedict/var_{keyword}.tsv'
			print(f'Writing to {fp}')
			var_df.to_csv(fp, sep='\t', index=False)

	def preview():
		print(df)
		for _ in var_dfs:
			print(_)
		for fil in query1(df):
			print(fil)

	def query1():
		fil1 = df[(df['count_s'] > 1) & (df['count_t'] == 1)]
		fil2 = df[(df['count_s'] == 1) & (df['count_t'] > 1)]
		fil3 = df[(df['count_s'] > 1) & (df['count_t'] > 1)]
		return fil1, fil2, fil3

	def query2():

		print('Running query2')
		char_df = create_charlist(df)
		char_df2 = df[(df['len_s'] == 1)]

		char_df2 = char_df2.rename(columns={
		'word_t': 'char_t',
		'word_s': 'char_s'
		})	

		char_df = char_df[['char_t', 'char_s']]
		char_df2 = char_df2[['char_t', 'char_s']]
		char_diff = char_df[~char_df.apply(tuple, axis=1).isin(char_df2.apply(tuple, axis=1))]
		
		print(' '.join(char_diff['char_s'].tolist()))
		print(' '.join(char_diff['char_t'].tolist()))

	def verify():
		print(df[(df['len_t'] != df['len_s'])])

	def fetch_data():

		df_one_one = df[(df['count_s'] == 1)]
		df_one_one_chars = df_one_one[(df_one_one['len_s'] == 1)]
		df_one_one_words = df_one_one[(df_one_one['len_s'] > 1)]

		df_ambig = df[(df['count_s'] > 1)]

		df_ambig_chars = df_ambig[(df_ambig['len_s'] == 1)]
		df_ambig_chars = df_ambig_chars.groupby(['word_s',]).agg(
			words_t=('word_t', list),
			pinyin=('pinyin', lambda x: list(chain.from_iterable(x))),
			glosses=('glosses', lambda x: list(chain.from_iterable(x))),
			).reset_index()
		
		df_ambig_words = df_ambig[(df_ambig['len_s'] > 1)]
		df_ambig_words['glosses'] = df_ambig_words['glosses'].apply(lambda x: ', '.join(x))
		df_ambig_words['word_s'] = df_ambig_words['word_s'].astype(str)
		df_ambig_words = df_ambig_words.groupby(['word_s',]).agg(
			words_t=('word_t', list),
			pinyin=('pinyin', lambda x: list(dict.fromkeys(chain.from_iterable(x)))),
			glosses=('glosses', lambda x: list(dict.fromkeys(x))),
			).reset_index()

		def generate_mapping():

			def mapping(word_s, words_t):
				result = defaultdict(list)

				for word_t in words_t:
					for s, t in zip(word_s, word_t):
						result[s].append(t)
				result = {s: tuple(dict.fromkeys(tt)) for s, tt in result.items()}
				return result

			# wrong: df_ambig_words['mapping'] = df_ambig_words[('word_s', 'words_t')].apply(mapping)
			df_ambig_words['mapping'] = df_ambig_words.apply(lambda row: mapping(row.word_s, row.words_t), axis=1)

		def generate_ambigs_t():

			def ambigs_t(words_t):
				word1, word2, *_ = words_t
				return [f'{char1}{char2}' for char1, char2 in zip(word1, word2) if char1 != char2]
	
			df_ambig_words['ambigs_t'] = df_ambig_words['words_t'].apply(ambigs_t)
			df_ambig_words['ambigs_t'] = df_ambig_words['ambigs_t'].copy().apply(lambda x: ' '.join((str(i) for i in x)))
			df_ambig_words = df_ambig_words.sort_values(by=['ambigs_t'])

			df_ambig_words['len_glosses'] = df_ambig_words['glosses'].apply(len)
			df_ambig_words['preferred_t'] = ''

			cols = df_ambig_words.columns.tolist()
			cols = cols[-1:] + cols[:-1]
			df_ambig_words = df_ambig_words[cols]

		generate_mapping()
		# df_ambig_words = df_ambig_words[(df_ambig_words['len_glosses'] == 1)]
		df_ambig_words.to_csv('output/cedict/ambig_words.tsv', sep='\t', index=False)

	fetch_data()
	exit()
