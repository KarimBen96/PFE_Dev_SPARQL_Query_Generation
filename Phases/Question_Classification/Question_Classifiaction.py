import warnings

warnings.filterwarnings('ignore')
import csv
import pandas as pd
import en_core_web_sm

en_nlp = en_core_web_sm.load()

import logging

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
from scipy.sparse import csr_matrix

logger = logging.getLogger(__name__)


def clean_old_data(training_data_path):
    question_features = ['Question', 'WH', 'WH-Bigram', 'WH-POS', 'WH-NBOR-POS', 'Root-POS', 'Class']
    with open(training_data_path, 'w', newline='') as csv_fp:
        csv_fp_writer = csv.writer(csv_fp, delimiter='|')
        csv_fp_writer.writerow(question_features)
        csv_fp.close()


def process_question(question, question_class, en_nlp, training_data_file, csv_fp_writer):
    en_doc = en_nlp(u'' + question)
    sentence_list = list(en_doc.sents)

    # Currently question classifier classifies only the 1st sentence of the question
    sentence = sentence_list[0]

    wh_bi_gram = []
    root_token, wh_pos, wh_nbor_pos, wh_word = [""] * 4

    for token in sentence:

        # if token is of WH question type
        if token.tag_ == "WDT" or token.tag_ == "WP" or token.tag_ == "WP$" or token.tag_ == "WRB":
            wh_pos = token.tag_
            wh_word = token.text
            wh_bi_gram.append(token.text)
            wh_bi_gram.append(str(en_doc[token.i + 1]))
            wh_nbor_pos = en_doc[token.i + 1].tag_

        # if token is the root of sentence
        if token.dep_ == "ROOT":
            root_token = token.tag_

    if wh_word != "" and " ".join(wh_bi_gram) != "" and wh_pos != "" and wh_nbor_pos != "":
        csv_fp_writer.writerow(
            [question, wh_word, " ".join(wh_bi_gram), wh_pos, wh_nbor_pos, root_token, question_class])
        # print([question, wh_word, " ".join(wh_bi_gram), wh_pos, wh_nbor_pos, root_token, question_class])
    else:
        logger.error("Extraction failed: {0}:{1}".format(question, question_class))


def read_input_file(raw_data_file, training_data_path, en_nlp):
    with open(training_data_path, 'a', newline='', encoding='utf-8') as csv_fp:
        csv_fp_writer = csv.writer(csv_fp, delimiter='|')
        for row in raw_data_file:
            list_row = row.split(" ")
            question_class_list = list_row[0].split(":")
            question = " ".join(list_row[1:len(list_row)])
            question = question.strip("\n")
            question_class = question_class_list[0]

            process_question(question, question_class, en_nlp, training_data_path, csv_fp_writer)

        csv_fp.close()


def extract_training_features(raw_data_path, training_data_path, en_nlp):
    with open(raw_data_path, 'r') as fp:
        read_input_file(fp, training_data_path, en_nlp)
        fp.close()
        logger.info("Extracted features from raw data.")
        logger.info("Excluded data where features failed to extract.")


def get_data_info(question_df):
    logger.debug("\n{0}".format(question_df.head()))
    logger.debug("\n{0}".format(question_df.info()))
    logger.debug("\n{0}".format(question_df.describe()))
    logger.debug("\n{0}".format(question_df.columns))


def remove_irrelevant_features(df_question):
    df_question_class = df_question.pop('Class')

    df_question.pop('Question')
    df_question.pop('WH-Bigram')

    return df_question_class


def pre_process(question_df):
    return pd.get_dummies(question_df)


def transform_data_matrix(df_question_train):
    # Generate Compressed Sparse Row matrix:
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html
    # logger.debug("Training data: {0}".format(df_question_train.shape))

    df_question_train = csr_matrix(df_question_train)

    return df_question_train


def classer_question(question):
    classes = ["Definition", 'Yes / No', "Complex"]
    return classes[0]
