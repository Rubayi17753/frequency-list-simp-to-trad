import csv, copy
import ahocorasick
from tqdm import tqdm
import pandas as pd
from collections import defaultdict, Counter
from itertools import chain

import dirs

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

def process(df, mode='s2t'):

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

	print('Explode glosses')
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

def process_readwrite():

	print('Loading CEDICT')
	df = pd.read_csv(dirs.cedict_fp, sep='\t', header=None, names=['cedict_raw'])
	df, var_dfs = process(df)

	print('Dumping to feather')
	df.to_feather(dirs.cedict_processed_fp)
	return df, var_dfs 