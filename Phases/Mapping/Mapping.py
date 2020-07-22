#
#               This is the Mapping Phase
#


import spacy

nlp = spacy.load('en_core_web_sm')
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

import re

import nltk
from nltk.tokenize import word_tokenize
from nltk import ngrams
from nltk.tokenize import word_tokenize
from Phases.Ontology_Exploration.Ontology_Exploration import *
from enum import Enum





#
#               Defining Global Variables
#


class Type(Enum):
    CLASS = 1
    OBJECT_PROPERTY = 2
    DATA_PROPERTY = 3
    ANNOTATION_PROPERTY = 4

    
    
    
    
    


#
#               General Functions
#



def sep_str_onto_elem(str_text):
    """
    This function returns a list of...

    il ne faudrait pas qu'un mot respecte 2 regles differentes, il faut bloquer certain cas.
    certains cas seront regles manuellement ---> c'est fait mais comme un cas particulier
    """

    pattern = "[^A-Z][a-z]+|[A-Z][a-z]+|[A-Z]+[^a-z]|[A-Z][a-z]+[A-Z]+[^a-z]"
    str_return = re.findall(pattern, str_text)

    pattern_1 = "[A-Z][A-Z]+[a-z]+"
    res_1 = re.findall(pattern_1, str_text)
    if len(res_1) != 0:
        pattern_2 = "[A-Z][A-Z]+"
        res_2 = re.findall(pattern_2, str_text)
        if len(res_2) != 0:
            res_2 = res_2[0][:-1]
            res_3 = re.findall(pattern, str_text)
            for i in range(len(res_3)):
                if res_2 in res_3[i]:
                    tempo = res_3[i]
                    res_3 = [sub.replace(res_3[i], res_2) for sub in res_3]
                    res_3 = [sub.replace(res_3[i + 1], tempo[-1] + res_3[i + 1]) for sub in res_3]
            str_return = res_3

    return str_return



def lemmatize_word(word, nlp=nlp):
    tempo = []
    tempo.insert(0, word)

    doc = nlp((' '.join([str(elem) for elem in tempo])))
    ll = [tokens.lemma_ for tokens in doc]

    if len(ll) > 0:
        if ll[0] == '-PRON-':
            return tempo

    return ll



def lemmatize_list(w_list, nlp=nlp):
    lemma_list = []

    for w in w_list:
        lemma_list.append(lemmatize_word(w)[0])

    return lemma_list



def tuple_to_string(tupl):
    st = ' '.join(tupl)
    return st



def list_to_string(lis):
    st = ' '.join(lis)
    return st


  
  
"""
def ngram_generation(str_question, n_gram):
    
    Updated: it returns a list of strings instead of a list of lists

    This function generate a list of all the n_grams (of lengh n_gram - the parameter -) and each
    element of that list is a list

    Parameters:
    - str_question: should be a question in string form but if it is a list ---> will be converted
    - n_gram: number of elements in the n_gram
   

    if type(str_question) is list:
        question = ''
        for item in str_question:
            question += item + ' '
        str_question = question[:-1]

    str_question = str_question.lower()
    list_ngram = []
    n_grams = ngrams(str_question.split(), n_gram)
    for item in n_grams:
        list_ngram.append(tuple_to_string(item))

    return list_ngram

"""


def ngram_generation(str_question, n_gram):

    if type(str_question) is list:
        question = ''
        for item in str_question:
            question += item + ' '
        str_question = question[:-1]

    str_question = str_question.lower()
    list_ngram = []
    comb = nltk.combinations( str_question.split(), n_gram)
    #n_grams = ngrams(str_question.split(), n_gram)
    for item in comb:
        list_ngram.append(tuple_to_string(item))

    return list_ngram



def rate_list_compare(list_1, list_2, nlp=nlp):
    """

    """

    rate = 0
    # l = max(len(list_1), len(list_2))
    l = len(list_1) + len(list_2)

    list_1 = [i.lower() for i in list_1]
    list_2 = [i.lower() for i in list_2]

    list_1 = lemmatize_list(list_1)
    list_2 = lemmatize_list(list_2)

    for item in list_1:
        if item in list_2:
            rate += 2
    rate = rate / l

    return rate



def light_rate_list_compare(list_1, list_2, nlp=nlp):
    """
    Checks only if, at least, 1 term of list_1 is in list_2
    """

    list_1 = [i.lower() for i in list_1]
    list_2 = [i.lower() for i in list_2]

    list_1 = lemmatize_list(list_1)
    list_2 = lemmatize_list(list_2)

    for item in list_1:
        if item in list_2:
            return True

    return False



def get_onto_elems_necessary(question_terms, onto):
    """
    - (question_terms): are already pre-processed (lemma...)
    - (onto): is the entire ontology
    """

    list_onto_elems_necessary = []  # a list of dictionaries (like the ontology ones)

    for o in onto.onto_elems_list:
        # if rate_list_compare(question_terms, o.processed_name) > 0:
        if light_rate_list_compare(question_terms, o.processed_name):
            list_onto_elems_necessary.append(o)


    # for i in onto.onto_elems_list:
    #  list_onto_elems_necessary_names.append(i.name)

    return list_onto_elems_necessary


  
  
def get_onto_elems_for_mapping(question_terms, onto_elems_necessary, onto=None):
    """
    Returns a list of dictionaries like:
                                        question_ngram:...   OntologyElement:...   rate_compare

    """

    list_dict = []
    list_ngrams_ = []
    list_ngrams_2 = []

    max_grams = min(5, len(question_terms) + 1)
    for i in range(1, max_grams):
        # we add a cond in case it's not possible: if we 2 terms ---> we can't have 4 gram !!!
        list_ngrams_.append(ngram_generation(question_terms, i))

    for n in list_ngrams_:  # We are in the 1-gram or 2-grams or ...
        for w in n:  # We are in one of all the 1-grams or 2-grams or ...
            w_list = w.split()
            list_ngrams_2.append(w_list)


    for n in list_ngrams_2:
        for o in onto_elems_necessary:
            if rate_list_compare(n, o.processed_name) > 0:
                dict_tempo = {"question_ngram": n, "onto_elem": o,
                              "rate_compare": round(rate_list_compare(n, o.processed_name), 2)}
                list_dict.append(dict_tempo)

    list_dict = sorted(list_dict, key=lambda d: d['rate_compare'], reverse=True)

    return list_dict

  
  
  
  


#
#               Functions used in the Mapping Functions
#



def get_word_pos_tag(word):
    text = word_tokenize(word)
    _, p = nltk.pos_tag(text)[0]

    return p



def check_pos_tag_noun(word):
    p = get_word_pos_tag(word)
    aig = (p == 'NN' or p == 'NNS' or p == 'NNP' or p == 'NNPS')

    return aig



def check_onto_sim_rate(onto_elems_for_mapping, rate):
    """
    Updated: => rate and not == rate, it won't have any impact on rate == 1

    Checks if, in the (onto_terms_necessary), there is at least an element whose rate is (rate)
    If there is, 1 or more, we return them (as a list of onto_elem) in a list
    """

    aig = False
    list_return = []

    for item in onto_elems_for_mapping:
        if item['rate_compare'] >= rate:
            list_return.append(item)
            aig = True

    return aig, list_return


def check_biggest_ngram_onto(onto_elems_for_mapping):
    """
    From the (onto_elems_for_mapping) list, it checks and returns the biggest ngrams
    - (onto_elems_for_mapping) is a list of dictionaries like:
                                        question_ngram:...   OntologyElement:...   rate_compare

    """

    len_ngram = 0
    list_return = []

    a = 0

    for l in onto_elems_for_mapping:
        if len(l['onto_elem'].processed_name) >= a:
            a = len(l['onto_elem'].processed_name)

    for l in onto_elems_for_mapping:
        if len(l['onto_elem'].processed_name) == a:
            list_return.append(l)

    return a, list_return



#
#               Mapping Functions
#


def mapping_definition(onto_elems_for_mapping):


    list_tempo = onto_elems_for_mapping
    biggest_rate = list_tempo[0]['rate_compare']
    a, b = check_onto_sim_rate(list_tempo, 1)

    if a:  # if we have rate = 1 or many, we take the biggest n-gram
        c, d = check_biggest_ngram_onto(b)
        list_final = d

    else:  # else, we take the top 5 and we check for rate = 0.8 or more
        if len(list_tempo) >= 5:
            top_5 = list_tempo[:5]
        else:
            top_5 = list_tempo
        a, b = check_onto_sim_rate(list_tempo, 0.8)

        if a:  # if positive, we take them all, it's unlikely to have more than 1
            c, d = check_biggest_ngram_onto(b)
            list_final = d

        else:  # else, we take all the type class in the top 5
            list_final = [x for x in top_5 if str(x['onto_elem'].type) == str(Type.CLASS)]
            if len(list_final) == 0:  # else, we take all the biggest rates
                list_final = [x for x in top_5 if x['rate_compare'] == biggest_rate]

    return list_final


def mapping_listing (onto_elems_for_mapping):

    list_tempo = onto_elems_for_mapping
    biggest_rate = list_tempo[0]['rate_compare']
    a, b = check_onto_sim_rate(list_tempo, 1)

    if a:  # if we have rate = 1 or many, we take the biggest n-gram
        c, d = check_biggest_ngram_onto(b)
        list_final = d
        if(str(list_final[0]['onto_elem'].type))==str(Type.CLASS):
            tag='entity_list'
        else:
            tag = 'property_list'

    else:  # else, we take the top 5 and we check for rate = 0.8 or more
        if len(list_tempo) >= 5:
            top_5 = list_tempo[:5]
        else:
            top_5 = list_tempo
        a, b = check_onto_sim_rate(list_tempo, 0.8)

        if a:  # if positive, we take them all, it's unlikely to have more than 1
            c, d = check_biggest_ngram_onto(b)
            list_final = d
            if (str(list_final[0]['onto_elem'].type)) == str(Type.CLASS):
                tag = 'entity_list'
            else:
                tag = 'property_list'

        else:  # else, we take all the type class in the top 5
            list_final = [x for x in top_5 if str(x['onto_elem'].type) == str(Type.CLASS)]
            if len(list_final) == 0:  # else, we take all the biggest rates
                list_final = [x for x in top_5 if x['rate_compare'] == biggest_rate]
                if (str(list_final[0]['onto_elem'].type)) == str(Type.CLASS):
                    tag = 'entity_list'
                else:
                    tag = 'property_list'

    return tag,list_final


def mapping_How_complex(onto_elems_for_mapping):
    list_tempo = onto_elems_for_mapping
    top_10=list_tempo[:10]
    list_object=[]
    list_classe = []
    list_final=[]
    for j in top_10:         # we search an oject property IRI
        if ((str(j['onto_elem'].type) == str(Type.OBJECT_PROPERTY)or str(j['onto_elem'].type) ==str(Type.DATA_PROPERTY))
        and (j['rate_compare']>=0.8)):
                list_object.append(j)

        else:  # we search a relation between 2 classes
                if str(j['onto_elem'].type) == str(Type.CLASS):
                    list_classe.append(j)


    if(len(list_object)!=0):#priority to object properties
        c, list_final = check_biggest_ngram_onto(list_object)
        tag = 'How_complex'
    else:# check the classes
        if(len(list_classe)>=2):
            list_final=list_classe
            tag = 'HObject_property_find'

    return tag,list_final


