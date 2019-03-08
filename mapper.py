#!/usr/bin/python
import re
import sys
import collections
import pickle
import os

if __name__ == '__main__':
    STOPWORDS = ['and','but','is','the','to']
    tokens_list = []
    for line in sys.stdin:
        line = line.replace('-','')
        tokens = re.split('[^a-zA-Z]+',line.lower().strip())
        if '' in tokens:
            tokens.remove('')
        tokens_list.extend(tokens)
        if '' in tokens_list:
            tokens_list.remove('')
           
    token_dict = {}
    doc_name = os.getenv('map_input_file')
    for index,token in enumerate(tokens_list):
        if token in STOPWORDS:
            continue
        if not token in token_dict.keys():
            token_dict[token] = [str(index)]
        else:
            token_dict[token].append(str(index))
    
    output = {}
    for token in token_dict.keys():
        token_count = len(token_dict[token])
        index_str = '\t'.join(token_dict[token])
        print("{0}\t{1}\t{2}\t{3}".format(token,doc_name,str(token_count),index_str))



    
