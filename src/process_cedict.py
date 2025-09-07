import csv, copy
import ahocorasick
from tqdm import tqdm
import pandas as pd
from collections import defaultdict, Counter

from directories import cedict_fp

def build_automaton(keywords):
	# ChatGPT-generated
	automaton = ahocorasick.Automaton()
	for idx, word in enumerate(keywords):
		automaton.add_word(word, (idx, word))
	automaton.make_automaton()
	return automaton

keywords = ('old variant of', 'surname')
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
        pinyin=('pinyin', lambda x: ', '.join(x)),
        glosses=('glosses', lambda x: '/'.join(x)),
        ).reset_index()
	
	df['count_t'] = df.groupby('word_t')['word_t'].transform('count')
	df['count_s'] = df.groupby('word_s')['word_s'].transform('count')

	def unic():
		print('Parsing by Unicode')

		print('Calculating lengths')
		df['len_t'] = df['word_t'].apply(len)
		df['len_s'] = df['word_s'].apply(len)
		return df
	unic()

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
		char_df = create_charlist(df)
		char_df2 = df[(df['len_s'] == 1)]
		char_df2 = char_df2.rename(columns={
		'chars_t': 'char_t',
		'chars_s': 'char_s'
		})		

		char_df = char_df[['char_t', 'char_s']]
		char_df2 = char_df2[['char_t', 'char_s']]

		print(char_df)
		print(char_df2)
	
	def verify():
		print(df[(df['len_t'] != df['len_s'])])

	def fetch_data():
		df_one_one = df[(df['count_s'] == 1)]
		df_one_one_chars = df_one_one[(df_one_one['len_s'] == 1)]
		df_one_one_words = df_one_one[(df_one_one['len_s'] > 1)]
		df_ambig = df[(df['count_s'] > 1)]
		df_ambig_chars = df_ambig[(df_ambig['len_s'] == 1)]
		df_ambig_words = df_ambig[(df_ambig['len_s'] > 1)]

		df_ambig_words.to_csv('output/cedict/ambig_words.tsv', sep='\t', index=False)

	query2()
	exit()
