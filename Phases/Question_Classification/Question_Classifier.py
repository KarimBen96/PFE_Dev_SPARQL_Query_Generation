import logging
import os

import numpy
import pandas
import re


import en_core_web_sm

from scipy.sparse import csr_matrix
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC

import nltk
from nltk.tokenize import word_tokenize

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "")
TRAINING_DATA_KARIM = "training_data_karim.csv"
RAW_DATA_KARIM = "raw_data_karim.txt"
QUESTION_CLASSIFICATION_MODEL = "question_classifier.pkl"


logger = logging.getLogger(__name__)



def pre_process(dta):
    return pandas.get_dummies(dta)



def remove_irrelevant_features(df_question):
    df_question_class = df_question.pop('Class')

    df_question.pop('Question')
    df_question.pop('WH-Bigram')

    return df_question_class



def transform_data_matrix(df_question_train, df_question_predict):
    df_question_train_columns = list(df_question_train.columns)
    df_question_predict_columns = list(df_question_predict.columns)

    df_question_trans_columns = list(set(df_question_train_columns + df_question_predict_columns))

    logger.debug("Union Columns: {0}".format(len(df_question_trans_columns)))

    trans_data_train = {}

    for feature in df_question_trans_columns:
        if feature not in df_question_train:
            trans_data_train[feature] = [0 for i in range(len(df_question_train.index))]
        else:
            trans_data_train[feature] = list(df_question_train[feature])

    df_question_train = pandas.DataFrame(trans_data_train)
    logger.debug("Training data: {0}".format(df_question_train.shape))
    df_question_train = csr_matrix(df_question_train)

    trans_data_predict = {}

    for feature in trans_data_train:
        if feature not in df_question_predict:
            trans_data_predict[feature] = 0
        else:
            trans_data_predict[feature] = list(df_question_predict[feature])  # KeyError

    df_question_predict = pandas.DataFrame(trans_data_predict)
    logger.debug("Target data: {0}".format(df_question_predict.shape))
    df_question_predict = csr_matrix(df_question_predict)

    return df_question_train, df_question_predict



def naive_bayes_classifier(x_train, y, x_predict):
    gnb = GaussianNB()
    gnb.fit(x_train, y)
    prediction = gnb.predict(x_predict)
    return prediction



def support_vector_machine(df_question_train, df_question_class, df_question_predict):
    lin_clf = LinearSVC()
    lin_clf.fit(df_question_train, df_question_class)
    prediction = lin_clf.predict(df_question_predict)
    return prediction, lin_clf



def predict_question_class(question_clf, df_question_predict):
    return question_clf.predict(df_question_predict), question_clf



def load_classifier_model(model_type="linearSVC"):
    # HELP: Not using the persistent classifier. SVC fails when it encounters previously unseen features at training.
    # Refer the comment in query_container

    training_model_path = os.path.join(CORPUS_DIR, QUESTION_CLASSIFICATION_MODEL)
    from sklearn.externals import joblib
    if model_type == "linearSVC":
        return joblib.load(training_model_path)



def get_question_predict_data(en_doc=None, df_question_test=None):
    if df_question_test is None:
        # currently only supports single sentence classification
        sentence_list = list(en_doc.sents)[0:1]

    else:
        sentence_list = df_question_test["Question"].tolist()
        en_nlp = en_core_web_sm.load()


    question_data_frame = []

    for sentence in sentence_list:

        wh_bi_gram = []
        root_token, wh_pos, wh_nbor_pos, wh_word = [""] * 4

        if df_question_test is not None:
            en_doc = en_nlp(u'' + sentence)
            sentence = list(en_doc.sents)[0]

        for token in sentence:

            if token.tag_ == "WDT" or token.tag_ == "WP" or token.tag_ == "WP$" or token.tag_ == "WRB":
                wh_pos = token.tag_
                wh_word = token.text
                wh_bi_gram.append(token.text)
                wh_bi_gram.append(str(en_doc[token.i + 1]))
                wh_nbor_pos = en_doc[token.i + 1].tag_

            if token.dep_ == "ROOT":
                root_token = token.tag_

        question_data_frame_obj = {'WH': wh_word, 'WH-POS': wh_pos, 'WH-NBOR-POS': wh_nbor_pos, 'Root-POS': root_token}
        question_data_frame.append(question_data_frame_obj)
        logger.debug("WH : {0} | WH-POS : {1} | WH-NBOR-POS : {2} | Root-POS : {3}"
                     .format(wh_word, wh_pos, wh_nbor_pos, root_token))

    df_question = pandas.DataFrame(question_data_frame)

    return df_question



def classify_question(en_doc=None, df_question_train=None, df_question_test=None):
    """ Determine whether this is a who, what, when, where or why question """

    if df_question_train is None:
        training_data_path = os.path.join(CORPUS_DIR, TRAINING_DATA_KARIM)
        df_question_train = pandas.read_csv(training_data_path, sep='|', header=0)

    df_question_class = remove_irrelevant_features(df_question_train)

    if df_question_test is None:
        df_question_predict = get_question_predict_data(en_doc=en_doc)
    else:
        df_question_predict = get_question_predict_data(df_question_test=df_question_test)

    df_question_train = pre_process(df_question_train)
    df_question_predict = pre_process(df_question_predict)

    df_question_train, df_question_predict = transform_data_matrix(df_question_train, df_question_predict)

    question_clf = load_classifier_model()

    logger.debug("Classifier: {0}".format(question_clf))


    predicted_class, svc_clf = support_vector_machine(df_question_train, df_question_class, df_question_predict)

    if df_question_test is not None:
        return predicted_class, svc_clf, df_question_class, df_question_train
    else:
        return predicted_class





def get_word_pos_tag(word):
    text = word_tokenize(word)
    _, p = nltk.pos_tag(text)[0]
    return p



def check_yes_no_class(question_):
    """
    """

    question_ = question_.split()

    p = get_word_pos_tag(question_[0])
    if p == 'VB' or p == 'VBD' or p == 'VBG' or p == 'VBN' or p == 'VBP' or p == 'VBZ' or p == 'MD':
        return True
    elif not (p == 'WDT' or p == 'WP' or p == 'WP$' or p == 'WRB'):
        return True

    return False



def classer_question(question_):
    """
    This is the function that calssifies a quetion for app.py
    """

    classes = ["Definition", 'Yes / No', 'List', "Complex"]


    if check_yes_no_class(question_):
        return classes[1]

    en_nlp = en_core_web_sm.load()
    en_doc = en_nlp(u'' + question_)
    q_class = classify_question(en_doc)

    if q_class == 'DEF':
        return classes[0]
    elif q_class == 'LIST':
        return classes[2]
    else:
        return classes[3]




if __name__ == "__main__":
    from time import time

    print(os.getcwd())

    logging.basicConfig(level=logging.DEBUG)
    start_time = time()
    en_nlp_l = en_core_web_sm.load()

    question = 'How to compile linux kernel ?'
    en_doc_l = en_nlp_l(u'' + question)

    """
    test_questions = ['What is expected from university teachers',
                      'How is a teacher hired',
                      'How is a teacher evaluated',
                      'How is a teacher tenured',
                      'How is a teacher ranked',
                      'How is a typically university organized',
                      'Why are universities organized into departments',
                      'How is chosen a president of a university',
                      'How is called each year of the four years formula',
                      'What is the most common degree',
                      'What is the most popular type of institution',
                      'What is the most prestigious type of institution',
                      'How is organized the academic year',
                      'How are students evaluated',
                      'How are students organized in discussion sessions',
                      'How is a teacher assigned',
                      'how is a pizza preapred',
                      'How do we apply for a Ph D',
                      'what are the creteria to select a candidate',
                      'How do we apply an orthopedic surgery',
                      'what are the conditions to accept an employee',
                      'how do you selelct your interns',
                      'how is a VISA Acceptation given',
                      'what are the conditions to build a hospital',
                      'what are the criteria to construct a factory in a land',
                      'how is a diabet test done',
                      'how do we form a facebook group']


    cpt = 0

    for item in test_questions:
        q = en_nlp_l(u'' + item)
        q_class = classify_question(q)

        cpt += 1
        if q_class != ['COMPLEX']:
            cpt -= 1
            print(item + '   :   ' + q_class)

    print(str(cpt) + '   ---   ' + str(len(test_questions)))

    """

    question_class = classify_question(en_doc_l)

    logger.info("Class: {0}".format(question_class))

    end_time = time()
    logger.info("Total prediction time : {0}".format(end_time - start_time))
