import pandas as pd
import csv, copy
import jieba
import pdb
from itertools import chain
from tqdm import tqdm

import dirs
from src.process_cedict2 import one_one, ambig_words, ambig_chars

def pipeline(segm_s, word_s):
		
	entries = list()
	match = None
	
	for data, label in zip((one_one, ambig_words), ('', 1)):		
		match = data.get(segm_s, None)

		if match:

			if label == 1:	
				# if word in ambig_words
				entries.extend([(s, '?', ''.join(tt)) 
				for s, tt in dict(match).items()])

			else:
				# if word in one_one	
				entries.extend([(s, t, label) 
				for s, t in zip(list(segm_s), list(match))])

			break

		else:

			if len(segm_s) == 1:

				ambig_tt = ambig_chars.get(segm_s, '')
				if ambig_tt:
					entries.append((segm_s, '!', ''.join(ambig_tt)))
				else:
					entries.append((segm_s, '!!', word_s))

				break

			else:
				pass
			
	return entries

def segment(word_s):

	entries_all = list()
	segms = [word_s,]

	methods = [jieba.cut, list, list]
	for i, method in enumerate(methods):

		segm_iter = list(segms)
		segms = list()

		for segm in segm_iter:

			entries = pipeline(segm, word_s)
			if entries:
				entries_all.extend(entries)
			else:
				segms.extend(method(segm))

		if segms == list():
			break

	return entries_all

def main():

	try:
		df = pd.read_csv(dirs.freqlist_fp, sep='\t', header=None, names=['word_s', 'freq'])
	except FileNotFoundError:
		print("Freqdict not found")

	print('Processing raw freqlist')
	df['entries'] = df['word_s'].apply(segment)

	print('Explode and aggregate by entry')
	df = df.explode('entries').copy()

	df = df.groupby('entries').agg(freq=('freq', 'sum')).reset_index()
	df[['char_s', 'char_t', 'notes']] = df['entries'].apply(pd.Series)
	del df['entries']
	df = df.sort_values('freq', ascending=0).reset_index(drop=True)

	print(df)
	exit()


	






