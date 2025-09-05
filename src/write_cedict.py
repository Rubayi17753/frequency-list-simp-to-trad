from directories import cedict_fp
from src.process_cedict import get_cedict_data
from src.write_bulk_to_file import write_bulk_to_file

def write_s2t():
	cedict_data = get_cedict_data(cedict_fp)
	fps = [f'output/cedict/s2t/{x}.tsv' for x in cedict_data.keys()]
	datas = cedict_data.values()
	write_bulk_to_file(fps, datas)

def write_t2s():
	cedict_data = get_cedict_data(cedict_fp, mode='t2s')
	fps = [f'output/cedict/t2s/{x}.tsv' for x in cedict_data.keys()]
	datas = cedict_data.values()
	write_bulk_to_file(fps, datas)

def main():
	write_s2t()
	write_t2s()