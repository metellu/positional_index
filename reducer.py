#!/usr/bin/python
import os
import sys
import pickle

if __name__ == '__main__':
    output = {}
    doc_dict = {}
    doc_counter = 0
    for line in sys.stdin:
        line = line.strip()
        fields = line.split('\t')
        token = fields[0]
        doc_name = fields[1]
        amount = fields[2]
        index  = fields[3:]
        if not token in output.keys():
            output[token] = {(doc_name,amount):index}
        else:
            output[token].update({(doc_name,amount):index})
    #if not os.path.exists('/usr/cloudera/wlyu2'):
    #    os.mkdir('/usr/cloudera/wlyu2')
    for word in output.keys():
        word_index = output[word]
        for occur_arr in word_index.keys():
            print("{0}\t{1}\t{2}\t{3}".format(word,occur_arr[0],occur_arr[1],'\t'.join(word_index[occur_arr])))