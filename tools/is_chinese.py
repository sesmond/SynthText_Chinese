from __future__ import division


def is_chinese(ch):
    # uc=ch.decode('utf-8')
    if u'\u4e00' <= ch <= u'\u9fff':
        return True
    else:
        return False



txt_source = '/home/yuz/lijiahui/syntheticdata/SynthText/data/newsgroup/chinese_txt_source.txt'
f = open(txt_source, 'r')
for line in f.readlines():
    print(line)
    for ch in line.decode('utf-8'):
        print(is_chinese(ch) or ch.isalnum())
