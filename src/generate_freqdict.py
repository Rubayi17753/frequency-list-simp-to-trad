import csv, copy
import jieba
import pdb
from collections import defaultdict
from tqdm import tqdm

one_one = ...
ambig = ...

def parse(s):

	result = list()
	match = None
	
	for data, label in zip((one_one, ambig), ('', 1)):
		while not match:
			match = s.get(data, None)
			
			if match:

				if label:
					if len(s) > 1:
						label = match
					else:
						label = match
					

				return (s, match, label)

def segment(s):

	entries = list()
	match = None

	segms = [s,]

	for segm in segms:
		segms = parse(segm)