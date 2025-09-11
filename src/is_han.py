import re
# 字唯非漢字
pattern = re.compile(r'[\u4e00-\u9fff]')

def is_hanword(s):
    _ = 0 if pattern.search(s) is None else 1
    return _