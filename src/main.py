import csv, yaml
from src.process_cedict import get_pairs
from directories import cedict_fp, multipair_word_fp, multipair_monochar_fp

def main():

	data_multipair, data_monochar = get_pairs(cedict_fp)
    


