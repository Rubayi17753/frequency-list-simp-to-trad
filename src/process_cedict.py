import csv
import ahocorasick
from tqdm import tqdm
from collections import defaultdict

from src.parse_string_unic import parse_string_with_unicode

def build_automaton(keywords):
    # ChatGPT-generated

    automaton = ahocorasick.Automaton()
    for idx, word in enumerate(keywords):
        automaton.add_word(word, (idx, word))
    automaton.make_automaton()
    return automaton

def filter_for_strings(data: list, badwords: list) -> list:
    # ChatGPT-generated, edited

    automaton = build_automaton(badwords)
    clean_texts, dirty_texts = list(), list()

    for text in tqdm(data):
        has_badword = any(True for _ in automaton.iter(text))
        if not has_badword:
            clean_texts.append(text)
        else:
            dirty_texts.append(text)

    return clean_texts, dirty_texts

def get_pairs(cedict_fp) -> dict:

    output = defaultdict(int)
    output_var = list()

    with open(cedict_fp, 'r', encoding='utf-8') as f:

        for i, row in tqdm(enumerate(f)):
            if not row.startswith('#'):
                row = row.replace('[', '\t[', 1).replace(']', ']\t', 1)

                if len(row) < 3:
                    print('\t'.join((str(i), '!!', *row)))
                
                else:
                    tword_sword, pinyin, glosses, *_ = row.strip().split('\t')
                    tword_sword = tword_sword.strip()

                    if tword_sword.count(' ') != 1:
                        print(' '.join((str(i), '!!', *row)))

                    else:
                        tword, sword = tword_sword.split(' ')
                        tchars = parse_string_with_unicode(tword)
                        schars = parse_string_with_unicode(sword)

                        if len(tchars) != len(schars):
                            print('\t'.join((str(i), '>>' *row)))

                        else:
                            if 'variant' not in glosses:
                                for tchar, schar in zip(tchars, schars):
                                    output[(tchar, schar)] += 1
                            else:
                                output_var.append((i, tword, sword, glosses))                        

        output, output_var = filter_for_strings()

        return output, output_var

def query_multipair(data: dict):

    output = defaultdict(list)

    for (tchar, schar), kount in data.items():
        output[schar].append((tchar, kount))

    output = {schar: tchar_tups for schar, tchar_tups in output.items() if len(tchar_tups) > 1}
    return output




    



             
