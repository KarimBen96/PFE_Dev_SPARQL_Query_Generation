from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from Phases.Ontology_Exploration import Ontology_Exploration as oe
from Phases.Question_Classification import Question_Classifier as qc
from Phases.Question_Linguistic_Treatments import Question_Linguistic_Treatments as qlt
from Phases.Mapping import Mapping as mapping
from Phases.Query_Building import Query_Building as qb


import os
import secrets
import copy
import re

app = Flask(__name__)
app.debug = True

app.config['UPLOAD_FOLDER'] = 'Uploaded_Files'

# This is for the secret key of "session"
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.debug = True







#################################################
#
#               Some Global Variables
#
#################################################

global current_question
global current_question_class
global current_question_terms
global current_question_ngrams

global current_onto_elems_necessary
global current_onto_elems_for_mapping
global current_mapping
global current_ontology
global final_mapping



list_stop_words = qlt.light_list_stop_words








#####################################################
#
#               Ontology Selection
#
#####################################################





@app.route('/select_ontology', methods=['GET', 'POST'])   # KARIM
def select_ontology():
    """

    """

    see_alert = False
    if request.method == 'GET':
        return render_template("Ontology_Exploration/Select_ontology.html", see_alert=see_alert)


    # else: if the method is POST
    file_ontology = request.files['file_ontology']
    filename = secure_filename(file_ontology.filename)
    onto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_ontology.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # session["filename_ontology"] = filename

    global current_ontology
    current_ontology = None

    current_ontology = oe.load_ontology(onto_path)
    current_ontology = oe.Ontology(oe.build_ontology(current_ontology), 'HERO')


    # return render_template("Select_ontology.html", see_alert=see_alert)
    # return render_template("file_up_successfull.html", file=filename)
    return redirect(url_for('ask_question'))





###############################################################
#
#               Asking the Question and Terms Extraction
#
###############################################################





@app.route('/ask_question', methods=['GET', 'POST'])   # KARIM
def ask_question():
    """

    """

    if request.method == 'GET':
        return render_template("Question_Classification/Ask_question.html")


    # else: if the method is POST

    question = request.form["textarea_question"]

    global current_question
    current_question = None
    current_question = question

    # question_class = classer_question(question)
    question_class = qc.classer_question(question)

    global current_question_class
    current_question_class = None
    current_question_class = question_class

    return redirect(url_for('ask_question_class'))
    # return render_template("Ask_question_class.html", classe=classe)





@app.route('/ask_question_class', methods=['GET', 'POST'])   # KARIM
def ask_question_class():
    """

    """

    global current_question_class
    question_class = current_question_class
    global current_question
    question = current_question

    first_question_class = question_class

    if request.method == 'GET':
        return render_template("Question_Classification/Ask_question_class.html", question_class=question_class,
                               question=question)



    # else: if the method is POST

    user_question_class = request.form["input_class_corrected"]
    if user_question_class != "":
        current_question_class = user_question_class


    file_name = 'Phases/Question_Classification/some_user_questions.txt'
    with open(file_name, 'a') as file:
        line = '{:<13}{:<13}{:<}'.format(first_question_class, current_question_class, question)
        file.write(line)
        file.write('\n')


    # return render_template("final.html", c=user_question_class)
    return redirect(url_for("question_key_terms_extraction"))





@app.route('/question_key_terms_extraction', methods=['GET', 'POST'])   # KARIM
def question_key_terms_extraction():
    """

    """

    global current_question_terms

    global current_ontology

    global current_mapping
    current_mapping = None

    global current_onto_elems_necessary
    current_onto_elems_necessary = None

    global current_onto_elems_for_mapping
    current_onto_elems_for_mapping = None


    question = current_question
    list_question_terms = re.findall('[A-Za-z]+', question)
    list_question_lemma = qlt.question_list_lemma(list_question_terms)
    qrt, list_question_key_terms = qlt.question_roots(question)

    session["list_question_key_terms"] = list_question_key_terms
    current_question_terms = list_question_key_terms


    if request.method == 'GET':
        return render_template("Question_Linguistic_Treatments/Question_key_terms_extraction.html", question=question,
                               list_question_terms=list_question_terms,
                               list_question_key_terms=list_question_key_terms,
                               list_question_lemma=list_question_lemma)



    # else: if the method is POST

    user_question_key_terms = request.form.getlist("checkbox_terms")
    if len(user_question_key_terms) > 0:
        session["list_question_key_terms"] = user_question_key_terms
        current_question_terms = user_question_key_terms

    # Here begins the mapping
    # mapping.init_onto_for_mapping()

    current_onto_elems_necessary, lol74 = mapping.get_onto_elems_necessary(current_question_terms, current_ontology)

    current_onto_elems_for_mapping = mapping.get_onto_elems_for_mapping(current_question_terms,
                                                                        current_onto_elems_necessary)

    current_mapping = mapping.mapping_definition(current_onto_elems_for_mapping)


    # return render_template("final.html", user_question_key_terms=user_question_key_terms)
    return redirect(url_for("show_mapping_result_clean"))






###########################################
#
#               Mapping
#
##########################################




def build_user_mapping_clean(our_select, onto_terms):   # KARIM
    """
    - (our_select): is the result of the select from the template of mapping it is a list
    - (onto_terms): is a list of ontology elems (like the one for mapping)

    Returns a list of ontology elems which are in (our_select) because (our_select) only contains strings which
    have to be processed
    """

    out_user_mapping = []

    for item_1 in our_select:
        dict_ = {}

        if item_1 != 'None' and item_1 != 'Remove':
            a, b = tuple(item_1.split('---'))

            if b != 'None':

                if ':' in b:
                    dict_['question_ngram'] = [a]
                    b1, b2 = tuple(b.split(' : '))

                    for i in onto_terms:
                        if i.name == b1:
                            dict_['onto_elem'] = i
                            out_user_mapping.append(dict_)
                else:
                    dict_['question_ngram'] = [a]
                    for i in onto_terms:
                        if i.name == b:
                            dict_['onto_elem'] = i
                            out_user_mapping.append(dict_)

        if item_1 == 'Remove':
            dict_['question_ngram'] = 'Remove'
            dict_['onto_elem'] = 'Remove'
            out_user_mapping.append(dict_)

        if item_1 == 'None':
            dict_['question_ngram'] = 'None'
            dict_['onto_elem'] = 'None'
            out_user_mapping.append(dict_)


    return out_user_mapping




@app.route('/show_mapping_result_clean', methods=['GET', 'POST'])   # KARIM
def show_mapping_result_clean():
    """

    """

    global current_ontology
    global current_mapping
    global current_onto_elems_necessary
    global current_onto_elems_for_mapping


    # ici on fait du bricolage   --->   une fois get_onto_elem_necessary updated on modifie ici aussi
    simple_onto_terms = []


    # du bricolage a cause du cas 'how do we define an assistant'
    if type(current_mapping) is not list:
        llb = [current_mapping]
        current_mapping = llb

    current_mapping_display = copy.deepcopy(current_mapping)


    for i in current_mapping:
        l_tempo = []
        for j in current_onto_elems_necessary:
            if mapping.light_rate_list_compare(i['question_ngram'], j.processed_name):
                l_tempo.append(j)
        simple_onto_terms.append(l_tempo)


    cpt = 0
    for i in simple_onto_terms:
        l_tempo = []
        for j in i:
            l_tempo.append(j.name + ' : ' + str(j.type))
        current_mapping_display[cpt]['onto_elems_necessary'] = l_tempo
        cpt += 1


    l = []
    for m in current_mapping_display:
        tuple_t = (m['question_ngram'], m['onto_elem'].IRI, m['rate_compare'], m['onto_elems_necessary'])
        l.append(tuple_t)



    if request.method == 'GET':
        return render_template("Mapping/Mapping_result_2.html", current_mapping=current_mapping, mapping_to_display=l)





    # else: if the method is POST

    select = request.form.getlist('select_user_mapping')

    user_mapping = build_user_mapping_clean(select, current_onto_elems_necessary)

    global final_mapping
    final_mapping = []

    for i, j in zip(user_mapping, current_mapping):

        if i['question_ngram'] == 'None':
            final_mapping.append(j)

        elif i['question_ngram'] != 'Remove':
            final_mapping.append(i)


    print('final mapping:  ' + str(final_mapping))


    """
    return render_template("final_for_mapping.html", current_mapping=current_mapping,
                           simple_current_mapping=current_mapping, sl=select, user_mapping=user_mapping,
                           final_mapping=final_mapping)
    """
    return redirect(url_for('query_building'))







###########################################
#
#               Query Building
#
###########################################





@app.route('/query_building', methods=['GET', 'POST'])   # ADEL
def query_building():
    """

    """

    see_alert = False
    global final_mapping
    if request.method == 'GET':
        fquery = qb.query_builder('definition', final_mapping[0]['onto_elem'].IRI)
        return render_template("Query_Building/Query_Building.html", see_alert=see_alert, tquery=fquery)








if __name__ == '__main__':
    # session = session()
    app.run(debug=True)
