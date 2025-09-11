import pandas as pd
import csv, copy
import jieba
import pdb
from itertools import chain
from tqdm import tqdm

from directories import freqlist_fp
from src.cedict_data import one_one, ambig

def pipeline(segm_s, word_s):
		
	entries = list()
	match = None
	
	for data, label in zip((one_one, ambig), ('', 1)):		
		match = data.get(segm_s, None)

		if match:

			if label == 1:	
				# if word in ambig
				entries.extend([(s, '?', ''.join(tt)) 
				for s, tt in dict(match).items()])

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

		segm_iter = set(segms)
		segms = list()

		for segm in segm_iter:
			entries = pipeline(segm, word_s)
			if entries:
				entries_all.extend(entries)
			else:
				segms.extend(method(segm))

		print(segms)
		if segms == list():
			break

	return entries_all

def main():

	print('Loading and processing raw freqlist')
	df = pd.read_csv(freqlist_fp, encoding='utf-8', sep='\t', header=None, names=['word_s', 'freq'])
	df['entries'] = df['word_s'].apply(segment)

	print(df)
	exit()
	






