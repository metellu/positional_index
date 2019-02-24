import pickle
import collections

def and_operator(term1,term2,index):
    returning_arr = []
    if not term1 in index.keys():
        return returning_arr
    term1_postings=index.get(term1)

    if not term2 in index.keys():
        return returning_arr
    term2_postings=index.get(term2)