#!/usr/bin/python

import os
import argparse
import pickle
import re
from collections import defaultdict

def collect_docs(dir_path):
    doc_dict = {}
    counter = 0
    if not os.path.isdir(dir_path):
        print("The specified path is not a directory.")
        exit(1)
    else:
        for doc in os.listdir(dir_path):
            print(doc)
            if os.path.isfile(dir_path+doc):
                counter = counter+1
                doc_id = "D"+str(counter)
                if not doc_dict.has_key(doc_id):
                    doc_dict[doc_id] = dir_path+doc
    file = open(dir_path+"/doc_dict","w+")
    pickle.dump(doc_dict,file)
    file.close
    return doc_dict

def build_semi_positional_index(doc,doc_id,stopwords):
    doc_name=os.path.basename(doc)
    file = open(doc,"r")
    term_arr = []
    for line in file.readlines():
        #remove hyphen, so that word like 'state-of-the-art' can be
        #treated properly as one word.
        line = line.replace('-','')
        #tokenize and normalize(lowercase) the document
        #put the tokens into an array for processing
        term_arr.extend(re.split('[^a-zA-Z]+',line.lower().strip()))
        if '' in term_arr:
            term_arr.remove('')

    inverted_index = {}
    file.close()
    
    for index,term in enumerate(term_arr):
        if term in stopwords:
            #skip all specified stopwords
            continue
        if term in inverted_index.keys():
            #If the dict contains the term,
            #the index of the current term will be appended
            #to the postings.
            term_indice = inverted_index.get(term)
            term_indice.append(index)
        else:
            inverted_index[term] = [index]
    semi_positional_index = defaultdict(list)
    for term,postings in inverted_index.items():
        semi_positional_index[term]={(doc_id,len(postings)):postings}
    return semi_positional_index
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--docpath',dest="path",help='Specify a path to directory that contains the documents.',required=True)
    args = parser.parse_args()
    DOC_PATH = args.path
    
    if os.path.exists(DOC_PATH+"/index"):
        os.remove(DOC_PATH+"/index")
    if os.path.exists(DOC_PATH+"/doc_dict"):
        os.remove(DOC_PATH+"/doc_dict")

    STOPWORDS = ['and','but','is','the','to']
    doc_index_arr = []
    index_key_arr = []
    docs = collect_docs(DOC_PATH)
    for doc_id,doc in docs.items():
        doc_index = build_semi_positional_index(doc,doc_id,STOPWORDS)
        doc_index_arr.append(doc_index)
        index_key_arr.extend(doc_index.keys())
        if "" in index_key_arr:
            index_key_arr.remove("")
        #print(doc_index)
    
    uniq_index_key = set(index_key_arr)
    

    json_file = open(DOC_PATH+"/index","w+")
    positional_index = {}
    for term in uniq_index_key:
        occurence = 0
        for index in doc_index_arr:
            if term in index.keys():
                occurence = occurence+index.get(term).keys()[0][1]
                if not term in positional_index.keys():
                    positional_index[term] = index.get(term)
                else:
                    positional_index[term].update(index.get(term))
        positional_index[term].update({term:occurence})
    print(positional_index)

    pickle.dump(positional_index,json_file,0)
    json_file.close()