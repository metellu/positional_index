import pickle
import collections
import re
import argparse
import pickle

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
        print "Invalid query"
        exit(1)
    #Add space before and after the parenthesis, so that 
    #we can split the query by space.
    query = query.replace('(','( ')
    query = query.replace(')',' )')

    #Normalize the query
    query = query.lower()

    query_terms = re.split(r'\s+',query)
    possible_operators = ['and','or','(',')']

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
    print(output)
    result = []
    for elem in output:
        if not elem in ['and','or']:
            result.append(retrieve_postings(index,elem))
        elif elem == 'and':
            r_operand = result.pop()
            l_operand = result.pop()
            result.append(and_operator(index,l_operand,r_operand))
        elif elem == 'or':
            r_operand = result.pop()
            l_operand = result.pop()
            result.append(or_operator(index,l_operand,r_operand))
            print(result)
    if len(result) != 1:
        #If by now, the result array contains more than one element,
        #the query must be invalid.
        print "Invalid query."
        exit(1)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q','--query',help='Specify search query',dest='query',required=True)
    parser.add_argument('-d','--doc',help='Specify the path of index file',dest='path',required=True)
    arg = parser.parse_args()
    QUERY = arg.query
    DOC_PATH = arg.path
    print(QUERY)
    print(DOC_PATH)

    file = open(DOC_PATH,"r")
    positional_index = pickle.load(file)
    #QUERY="really"
    result = parse_query(QUERY,positional_index)
    print(result)