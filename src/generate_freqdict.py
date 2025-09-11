import pandas as pd
import csv, copy
import jieba
import pdb
from collections import defaultdict
from itertools import chain
from tqdm import tqdm

from src.process_cedict import preprocess
from directories import cedict_fp

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

def pipeline(segm_s, word_s, one_one, ambig):
	
	def pipeline_char(s):

		for data, label in zip((one_one, ambig), ('', 1)):
			match = data.get(s, None)

			if match:
				if label:		# i.e. if char in ambig
					return '?', match
				else:			# i.e. if char in one_one
					return match, ''
			
	entries = list()
	match = None
	
	for data, label in zip((one_one, ambig), ('', 1)):		
		match = data.get(segm_s, None)

		if match:

			if label:	
				# if word in ambig
				entries.extend([(s, *pipeline_char(s)) 
				for s, t in zip(list(segm_s), list(match))])

			else:
				# if word in one_one	
				entries.extend([(s, t, label) 
				for s, t in zip(list(segm_s), list(match))])

		else:
			
			if len(segm_s) == 1:
				entries.extend([(s, '!', word_s) 
				for s in segm_s])

			else:
				pass
			
	return entries

def segment(word_s):

	entries_all = list()
	segms = [word_s,]
	methods = [jieba.cut, list]
	for i, method in enumerate(methods):

		if segms == list():
			break

		segm_iter = set(segms)
		segms = list()

		for segm in segm_iter:
			entries = pipeline(segm, word_s)
			if entries:
				entries_all.extend(entries)
			else:
				segms.extend(method(segm))

	return entries_all

def main():

	df = pd.read_csv(cedict_fp, sep='\t', header=None, names=['cedict_raw'])
	df, var_dfs = preprocess(df)
	df_one_one = df[(df['count_s'] == 1)]
	df_ambig = df[(df['count_s'] > 1)]
	df_ambig = process_ambig(df_ambig)

	print(df_one_one)
	print(df_ambig)






