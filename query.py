import pickle
import collections
import re
import argparse
import pickle
import os
import json

def retrieve_postings(index,term):
    returning_arr = []
    if not term in index.keys():
        return returning_arr
    term_postings = index.get(term)
    for key in term_postings.keys():
        if isinstance(key,tuple):
            doc_id = str(key[0])[1:]

            
            if not doc_id in returning_arr:
                returning_arr.append(doc_id)
    return returning_arr

def and_operator(index,term1_docs,term2_docs):
    term1_index=0
    term2_index=0
    returning_arr = []
    while term1_index < len(term1_docs) and term2_index < len(term2_docs):
        if term1_docs[term1_index] == term2_docs[term2_index]:
            returning_arr.append(term1_docs[term1_index])
            term1_index = term1_index+1
            term2_index = term2_index+1
        else:
            if term1_docs[term1_index] < term2_docs[term2_index]:
                term1_index = term1_index+1
            else:
                term2_index = term2_index+1
    return returning_arr

def or_operator(index,term1_docs,term2_docs):
    term_docs = term1_docs[:]
    term_docs.extend(term2_docs)

    #For OR, the code simply merge the two docs arrays,
    #then remove the duplicate ones.
    returning_arr = list(set(term_docs))
    return returning_arr

def parse_query(query,index):
    if len(re.findall(r'\(',query)) != len(re.findall(r'\)',query)):
        print "Invalid query: parenthesis don't match."
        exit(1)
    
    #Add space before and after the parenthesis, so that 
    #we can split the query by space.
    query = query.replace('(','( ')
    query = query.replace(')',' )')

    #Normalize the query
    query = query.lower()
    query = query.replace('-','')
    query_terms = re.split(r'\s+',query)
    possible_operators = ['and','or','(',')']
    operator_num = 0
    for term in query_terms:
        for operator in ['and','or']:
            if operator == term:
                operator_num = operator_num+1
                break
    non_operator_num = len([term for term in query_terms if not term in possible_operators])

    if operator_num > 0 and non_operator_num != operator_num+1:
        print("Invalid query. ")
        exit(1)

    operator_stack = []
    output = []
    
    for term in query_terms:
        if term in possible_operators:
            if len(operator_stack) == 0:
                operator_stack.append(term)
            else:
                if term == '(':
                    operator_stack.append(term)
                elif term == ')':
                    #When parsing reaches the right parenthesis, 
                    #the code need to deal with the content that surrounded
                    #by the parenthesis pair.
                    operator = operator_stack.pop()
                    while operator != '(':
                        output.append(operator)
                        operator = operator_stack.pop()
                else:
                    operator_stack.append(term)
                    #If the operator stack has no parenthesis and contains 2 elements.
                    #dump the first element to the output array. By doing this, the code
                    #can ensure that the boolean calculation of elements outside parenthesis
                    #takes place from left to right. 
                    if not '(' in operator_stack and len(operator_stack) == 2:
                        output.append(operator_stack.pop(0))
        else:
            output.append(term)
    while len(operator_stack) != 0:
        output.append(operator_stack.pop())
    
    flag = False
    for elem in output:
        if elem in ['and','or']:
            flag = True
            break
    
    if flag == False:
        counter = len(output)-1
        while counter>0:
            output.append('and')
            counter = counter - 1
    #print(output)
    result = []
    terms = []
    for elem in output:
        if not elem in ['and','or']:
            result.append(retrieve_postings(index,elem))
            terms.append(elem)
        elif elem == 'and':
            #Retrieve the closest two previous elements.
            r_operand = result.pop()
            l_operand = result.pop()
            result.append(and_operator(index,l_operand,r_operand))
        elif elem == 'or':
            #Retrieve the closest two previous elements.
            r_operand = result.pop()
            l_operand = result.pop()
            result.append(or_operator(index,l_operand,r_operand))
            #print(result)
    if operator_num > 0 and len(result) != 1:
        #If by now, the result array contains more than one element,
        #the query must be invalid.
        print "Invalid query."
        exit(1)
    result_dict = {}
    result_dict['doc_ids'] = result[0]
    result_dict['terms'] = terms
    return result_dict

def form_final_output(index,docs_dict,result_dict):
    doc_ids = ['D'+str(id) for id in result_dict['doc_ids']]
    
    returning_dict = {}
    print("Matched Document(s):")
    for id in doc_ids:
        print("- "+docs_dict[id])
    print("\nTerm Match Details:")
    for term in result_dict['terms']:
        print("["+term+"]:")
        tmp_dict = {}
        if not term in index.keys():
            print("- No matches.")
            continue
        postings = index.get(term)
        for key in postings.keys():
            if isinstance(key,tuple):
                if key[0] in doc_ids:
                    positions = ",".join(map(str,postings.get(key)))
                    print("- "+docs_dict.get(key[0],key[0])+": "+positions)
                    tmp_dict[docs_dict.get(key[0])] = postings.get(key)
        if len(tmp_dict.keys()) == 0:
            print("- No matches.")
        returning_dict[term] = tmp_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q','--query',help='Specify search query',dest='query',required=True)
    parser.add_argument('-d','--doc',help='Specify the path of index file',dest='path',required=True)
    arg = parser.parse_args()
    QUERY = arg.query
    DOC_PATH = arg.path

    #Loading index from disc.
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH,"r") as file:
            positional_index = pickle.load(file)
    else:
        print("Cannot find index file at the specified location.")
        exit(1)
    DOC_DICT_PATH = DOC_PATH.replace("index","doc_dict")
    if os.path.exists(DOC_DICT_PATH):
        with open(DOC_DICT_PATH,"r") as file:
            docs_dict = pickle.load(file)
    else:
        doc_dict = {}
    result = parse_query(QUERY,positional_index)
    if len(result['doc_ids']) == 0:
        print("No matches.")
    else:
        form_final_output(positional_index,docs_dict,result)