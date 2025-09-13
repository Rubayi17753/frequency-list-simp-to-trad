import pandas as pd
from collections import defaultdict

import dirs
from src.process_cedict import process, process_readwrite

def agg_ambig(df):

	df['glosses'] = df['glosses'].apply(lambda x: ', '.join(x))
	df['word_s'] = df['word_s'].astype(str)
	df = df.groupby(['word_s',]).agg(
		words_t=('word_t', list),
		# pinyin=('pinyin', lambda x: list(dict.fromkeys(chain.from_iterable(x)))),
		# glosses=('glosses', lambda x: list(dict.fromkeys(x))),
		).reset_index()
	return df

def get_ambig_words(df):

	df = df[(df['len_s'] > 1)]
	df = agg_ambig(df)

	def mapping(word_s, words_t):
		result = defaultdict(list)

		for word_t in words_t:
			for s, t in zip(word_s, word_t):
				result[s].append(t)
		result = {s: tuple(dict.fromkeys(tt)) for s, tt in result.items()}
		return result
	df['mapping'] = df.apply(lambda row: mapping(row.word_s, row.words_t), axis=1)

	return df

def get_ambig_chars(df):

	df = df[(df['len_s'] == 1)]
	df = agg_ambig(df)
	return df

try:
	df = pd.read_feather(dirs.cedict_processed_fp)
except FileNotFoundError:
	df, var_dfs = process_readwrite()

print('Filtering data')
df_one_one = df[(df['count_s'] == 1)]
df_ambig = df[(df['count_s'] > 1)]
df_ambig_words = get_ambig_words(df_ambig)
df_ambig_chars = get_ambig_chars(df_ambig)

one_one = df_one_one.set_index('word_s')['word_t'].to_dict()
ambig_words = df_ambig_words.set_index('word_s')['mapping'].to_dict()
ambig_chars = df_ambig_chars.set_index('word_s')['words_t'].to_dict()