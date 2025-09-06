import csv, copy
import ahocorasick
from tqdm import tqdm
import pandas as pd
from collections import defaultdict, Counter

from src.parse_string_unic import unicode_parse
from directories import cedict_fp

def build_automaton(keywords):
	# ChatGPT-generated
	automaton = ahocorasick.Automaton()
	for idx, word in enumerate(keywords):
		automaton.add_word(word, (idx, word))
	automaton.make_automaton()
	return automaton

def screen_text(text: str, automaton) -> bool:
	# ChatGPT-generated, edited
	text = text.strip()
	return any(True for _ in automaton.iter(text))

def process_cedict(fp, mode='s2t'):

	...


def main():
	
	df = pd.read_csv(cedict_fp, sep="\t")