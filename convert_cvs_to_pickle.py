#!/usr/bin/python
import os
import pickle

pre_pickle_dict = {}
docs_dict = {}
counter = 0
doc_id = ''
hadoop_dir = '/home/cloudera/'
hadoop_output = 'index.csv'
file = open(hadoop_dir+hadoop_output,'r')
for line in file.readlines():
    line = line.strip()
    fields = line.split('\t')
    token = fields[0]
    doc_name = fields[1]
    occur_times = fields[2]
    positions = fields[3:]
    if not doc_name in docs_dict.values():
        counter = counter + 1
        doc_id = 'D'+str(counter)
        docs_dict[doc_id] = doc_name
    
    if not token in pre_pickle_dict.keys():
        pre_pickle_dict[token] = {(doc_id,occur_times):positions}
    else:
        pre_pickle_dict[token].update({(doc_id,occur_times):positions})
file.close()

with open(hadoop_dir+'doc_dict','w') as file:
    pickle.dump(docs_dict,file)

with open(hadoop_dir+'index','w') as file:
    pickle.dump(pre_pickle_dict,file)
