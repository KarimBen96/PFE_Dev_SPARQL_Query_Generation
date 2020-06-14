"""
                                     IMPORTS AND DOWNLOADS
"""

import warnings
import spacy
import en_core_web_sm
import nltk

warnings.filterwarnings('ignore')

en_nlp = spacy.load('en_core_web_sm')
nlp = en_core_web_sm.load()

nltk.download('wordnet')
WNlemma = nltk.WordNetLemmatizer()

"""
                                  CODES AND FUNCTIONS  
"""

light_list_stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
                         "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                         'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
                         'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
                         'these', 'those', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                         'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                         'during', 'before', 'after', 'above', 'below', 'to', 'from',
                         'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
                         'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                         'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                         'too', 'very', 's', 't', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd',
                         'll', 'm', 'o', 're', 've', 'y', 'what', 'when', 'where', 'who', 'how', 'why']


def dict_to_list(dict):
    """
    Converts a python dictionary into a list (of strings only)
    """
    dictlist = []
    for key in dict.keys():
        temp = dict[key]
        dictlist.append(key)
        for v in temp:
            dictlist.append(str(v))

    return dictlist


def lemmatize_list(w_list, local_nlp=nlp):
    lemma_list = []

    for w in w_list:
        lemma_list.append(w)

    doc = local_nlp((' '.join([str(elem) for elem in lemma_list])))
    return [tokens.lemma_ for tokens in doc]


def question_roots(question, local_nlp=en_nlp, stop_list=light_list_stop_words):
    """
    Returns a python dictionary of the root, verbs and nouns of the question. And a list of this dictionary.
    This is done with a dependency tree of the question terms
    """

    # We remove the last character if not alphanumeric
    if not question[-1].isalnum():
        question = question[:-1]

    q = question

    question = nlp(question.lower())
    roots = {}

    for token in question:
        if token.dep_ == "ROOT":
            some_str = [child for child in token.children]
            roots[token.text] = some_str
        elif token.pos_ == "VERB" or token.pos_ == "NOUN" or token.pos_ == "PROPN":
            some_str = [child for child in token.children]
            roots[token.text] = some_str

    lemmatized_question = lemmatize_list(q.split(' '), local_nlp)
    for item in lemmatized_question:
        if not (item in lemmatize_list(dict_to_list(roots), local_nlp)):
            lemmatized_question.remove(item)

    roots_list = [w for w in lemmatized_question if w not in stop_list]

    return roots, roots_list


def question_list_lemma(question_list, local_nlp=en_nlp):
    return lemmatize_list(question_list, local_nlp)
