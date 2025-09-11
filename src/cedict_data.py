import pandas as pd
from collections import defaultdict

from directories import cedict_fp
from src.process_cedict import preprocess

def process_ambig(df):

	df = df[(df['len_s'] > 1)]
	df['glosses'] = df['glosses'].apply(lambda x: ', '.join(x))
	df['word_s'] = df['word_s'].astype(str)
	df = df.groupby(['word_s',]).agg(
		words_t=('word_t', list),
		# pinyin=('pinyin', lambda x: list(dict.fromkeys(chain.from_iterable(x)))),
		# glosses=('glosses', lambda x: list(dict.fromkeys(x))),
		).reset_index()

	def mapping(word_s, words_t):
		result = defaultdict(list)

		for word_t in words_t:
			for s, t in zip(word_s, word_t):
				result[s].append(t)
		result = {s: tuple(dict.fromkeys(tt)) for s, tt in result.items()}
		return result
	df['mapping'] = df.apply(lambda row: mapping(row.word_s, row.words_t), axis=1)

	return df

df = pd.read_csv(cedict_fp, sep='\t', header=None, names=['cedict_raw'])
df, var_dfs = preprocess(df)

print('Filtering data')
df_one_one = df[(df['count_s'] == 1)]
df_ambig = df[(df['count_s'] > 1)]
df_ambig = process_ambig(df_ambig)

one_one = df_one_one.set_index('word_s')['word_t'].to_dict()
ambig = df_ambig.set_index('word_s')['mapping'].to_dict()