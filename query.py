import pickle
import collections

def retrieve_postings(index,term):
    returning_dict = {}
    if not term in index.keys():
        return returning_dict
    term_postings = index.get(term)
    for key in term_postings.keys():
        if isinstance(key,str):
            total_freq = term_postings.get(key)
            returning_dict['total'] = total_freq
        elif isinstance(key,list):
            doc_id = str(key[0])[2:]
            if not "doc_list" in returning_dict.keys():
                returning_dict['doc_list'] = [doc_id]
            else:
                returning_dict['doc_list'].extend(doc_id)
    return returning_dict

def and_operator(index,term1,term2):
    term1_dict = retrieve_postings(index,term1)
    term2_dict = retrieve_postings(index,term2)

    term1_docs = term1_dict.get('doc_list')
    term2_docs = term2_dict.get('doc_list')

    term1_index=0
    term2_index=0
    returning_arr = []
    while term1_index < len(term1_docs) and term2_index < len(term2_docs):
        if term1_docs[term1_index] == term2_docs[term2_index]:
            returning_arr.append(term1_docs[term1_docs])
            term1_index = term1_index+1
            term2_index = term2_index+1
        else:
            if term1_docs[term1_index] < term2_docs[term2_index]:
                term1_index = term1_index+1
            else:
                term2_index = term2_index+1
    return returning_arr

def or_operator(index,term1,term2):
    term1_dict = retrieve_postings(index,term1)
    term2_dict = retrieve_postings(index,term2)

    term1_docs = term1_dict.get('doc_list')
    term2_docs = term2_dict.get('doc_list')

    term_docs = term1_docs.copy()
    term_docs.extend(term2_docs)

    returning_arr = set(term_docs)
    return returning_arr

