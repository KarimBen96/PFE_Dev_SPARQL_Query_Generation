#
#               This is the Mapping Phase
#


import os
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
import spacy

nlp = spacy.load('en_core_web_sm')
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

import time
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk import ngrams
from nltk.tokenize import word_tokenize

#
#               Defining Global Variables
#


type_class = "Class"
type_object_prop = "Object_Property"
type_data_prop = "Data_Property"
type_annotation_prop = "Annotation"

# file_name_class = "./Ontology_Stuff/Classes.csv"
file_name_class = "./Ontology_Elements_Files/Ontology_HERO/Classes.csv"
# file_name_object_prop = "./Ontology_Stuff/ObjectProperties.csv"
file_name_object_prop = "./Ontology_Elements_Files/Ontology_HERO/ObjectProperties.csv"
# file_name_data_prop = "./Ontology_Stuff/DataProperties.csv"
file_name_data_prop = "./Ontology_Elements_Files/Ontology_HERO/DataProperties.csv"
# file_name_annotation_prop = "./Ontology_Stuff/AnnotationsProperties.csv"
file_name_annotation_prop = "./Ontology_Elements_Files/Ontology_HERO/AnnotationsProperties.csv"

list_class = []
list_object_prop = []
list_data_prop = []
list_annotation_prop = []

# List of ontology data names (only names)
list_class_prepro = []
list_data_prepro = []
list_object_prepro = []
list_annotation_prepro = []


#
#               Some Pre-processing before the functions
#


def init_onto_for_mapping():
    """
    This function initiate the ontology elements for the mapping phase
    Maybe it should be done in Ontology Exploration

    :return:
    """

    list_class = onto_type_file_to_dict(file_name_class, type_class)
    list_object_prop = onto_type_file_to_dict(file_name_object_prop, type_object_prop)
    list_data_prop = onto_type_file_to_dict(file_name_data_prop, type_data_prop)
    list_annotation_prop = onto_type_file_to_dict(file_name_annotation_prop, type_annotation_prop)

    for i in list_class[:]:
        i['IRI'] = i['IRI'].rstrip("\n")
    for i in list_data_prop[:]:
        i['IRI'] = i['IRI'].rstrip("\n")
    for i in list_object_prop[:]:
        i['IRI'] = i['IRI'].rstrip("\n")
    for i in list_annotation_prop[:]:
        i['IRI'] = i['IRI'].rstrip("\n")


    for i in list_class[:]:
        list_class_prepro.append(sep_str_onto_elem(i['name']))
    for i in list_data_prop[:]:
        list_data_prepro.append(sep_str_onto_elem(i['name']))
    for i in list_object_prop[:]:
        list_object_prepro.append(sep_str_onto_elem(i['name']))
    for i in list_annotation_prop[:]:
        list_annotation_prepro.append(sep_str_onto_elem(i['name']))


#
#               The Functions
#


def onto_type_file_to_dict(file_name, type_prop):
    """
    Convert a file of data of the ontology to a list of dictionnaries. A dictionnary
    for each line of the file that is structured as follow:
    {"name": "", "IRI": "", "type": ""}
    The list contains only one type of property
    by the type of the property

    The fuction returns a list of dictionnaries
    """

    list_file_line = []
    dict_tempo = {"name": "", "IRI": "", "type": ""}
    onto_elem_type = type_prop

    with open(file_name) as f:
        f = open(file_name, "r")
        lines = f.readlines()
        for l in lines:
            dict_tempo = {"name": "", "IRI": "", "type": ""}
            dict_tempo["type"] = onto_elem_type
            dict_tempo["name"] = (l.split(","))[0]
            dict_tempo["IRI"] = (l.split(","))[1]
            list_file_line.append(dict_tempo)

    return list_file_line


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
    return [tokens.lemma_ for tokens in doc]


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


def ngram_generation(str_question, n_gram):
    """
    Updated: it returns a list of strings instead of a list of lists

    This function generate a list of all the n_grams (of lengh n_gram - the parameter -) and each
    element of that list is a list

    Parameters:
    - str_question: should be a question in string form but if it is a list ---> will be converted
    - n_gram: number of elements in the n_gram
    """

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


def get_onto_elem_for_mapping(list_ngrams_, onto_elem_necessary_):
    """
    Returns a list of dictionaries like:
                                        question_ngram:...   onto_elem:...   rate_compare

    The returned list is also ordered following the (rate_compare) in descendent

    Updated: onto_elem_necessary_   is not used
    """

    list_dict = []

    for n in list_ngrams_:  # We are in the 1-gram or 2-grams or ...

        #        for ll in list_onto[1:]:
        for ll in onto_elem_necessary_:

            for w in n:  # We are in one of all the 1-grams or 2-grams or ...
                w_list = w.split()
                if rate_list_compare(w_list, sep_str_onto_elem(ll['name'])) > 0:
                    # print('{:<45}{:<45}{:<}'.format(str(w_list), str(ll), round(rate_list_compare(w_list, ll), 2)))
                    dict_tempo = {}
                    dict_tempo["question_ngram"] = w_list
                    dict_tempo["onto_elem"] = ll
                    dict_tempo["rate_compare"] = round(rate_list_compare(w_list, sep_str_onto_elem(ll['name'])), 2)
                    list_dict.append(dict_tempo)

    list_dict = sorted(list_dict, key=lambda d: d['rate_compare'], reverse=True)

    return list_dict


def get_word_pos_tag(word):
    text = word_tokenize(word)
    _, p = nltk.pos_tag(text)[0]

    return p


def check_pos_tag_noun(word):
    p = get_word_pos_tag(word)
    aig = (p == 'NN' or p == 'NNS' or p == 'NNP' or p == 'NNPS')

    return aig


def mapping_definition(question_terms, onto_terms_necessary):
    """

    """

    list_ngram = []
    list_final = []

    for i in range(1, 5):
        # we add a cond in case it's not possible: if we 2 terms ---> we can't have 4 gram !!!
        if len(ngram_generation(question_terms, i)) > 0:
            list_ngram.append(ngram_generation(question_terms, i))

    list_tempo = get_onto_elem_for_mapping(list_ngram, onto_terms_necessary)

    for item in list_tempo:

        if len(item['question_ngram']) == 1:  # if we have 1-gram in the question term

            if check_pos_tag_noun(item['question_ngram'][0]):
                if (item['rate_compare'] == 1) and (item['onto_elem']['type'] == 'Class'):
                    list_final.append(item)

                elif item['rate_compare'] == 1:
                    list_final.append(item)

        else:  # if we have 2-grams or 3-grams or 4-grams
            if (item['rate_compare'] == 1) and (item['onto_elem']['type'] == 'Class'):
                list_final.append(item)

            elif item['rate_compare'] == 1:
                list_final.append(item)

    #    print("we mapped a definition")
    return list_final
