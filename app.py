from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from Phases.Question_Classification.Question_Classifiaction import classer_question
from Phases.Question_Linguistic_Treatments import Question_Linguistic_Treatments as qlt
from Phases.Mapping import Mapping as mapping


import os
import secrets

app = Flask(__name__)
app.debug = True

app.config['UPLOAD_FOLDER'] = 'Uploaded_Files'

# This is for the secret key of "session"
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.debug = True

#
#                                       START OF ADEL'S CODE
#


#
#                                       END OF ADEL'S CODE
#


#
#                                       START OF KARIM'S CODE
#


#               Some Global Variables

current_question = ""
current_question_class = ""
current_question_terms = []
current_onto_elem_necessary = []
current_mapping = []


list_stop_words = qlt.light_list_stop_words





#               Ontology Selection


@app.route('/select_ontology', methods=['GET', 'POST'])
def select_ontology():
    see_alert = False
    if request.method == 'GET':
        return render_template("Ontology_Exploration/Select_ontology.html", see_alert=see_alert)

    # else: if the method is POST
    file_ontology = request.files['file_ontology']
    filename = secure_filename(file_ontology.filename)
    file_ontology.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    session["filename_ontology"] = filename
    # return render_template("Select_ontology.html", see_alert=see_alert)
    return redirect(url_for('ask_question'))
    # return render_template("file_up_successfull.html", file=filename)





#               Asking the Question and Terms Extraction


@app.route('/ask_question', methods=['GET', 'POST'])
def ask_question():

    if request.method == 'GET':
        return render_template("Question_Classification/Ask_question.html")

    # else: if the method is POST

    question = request.form["textarea_question"]
    session["question"] = question
    current_question = question

    question_class = classer_question(question)
    session["question_class"] = question_class
    current_question_class = question_class

    return redirect(url_for('ask_question_class'))
    # return render_template("Ask_question_class.html", classe=classe)


@app.route('/ask_question_class', methods=['GET', 'POST'])
def ask_question_class():

    if request.method == 'GET':
        question_class = session["question_class"]
        question = session["question"]
        return render_template("Question_Classification/Ask_question_class.html", question_class=question_class,
                               question=question)

    # else: if the method is POST

    user_question_class = request.form["input_class_corrected"]
    if user_question_class == "":
        session["user_question_class"] = user_question_class
        current_question_class = user_question_class

    return redirect(url_for("question_key_terms_extraction"))
    # return render_template("final.html", c=user_question_class)


@app.route('/question_key_terms_extraction', methods=['GET', 'POST'])
def question_key_terms_extraction():
    question = session["question"]
    list_question_terms = question.split(' ')
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
    session["list_question_key_terms"] = user_question_key_terms
    current_question_terms = user_question_key_terms

    # return render_template("final.html", user_question_key_terms=user_question_key_terms)
    return redirect(url_for("show_mapping_result"))





#               Mapping


def build_user_mapping(our_select, onto_terms):
    """

    """

    out_user_mapping = []

    for item_1 in our_select:
        dict_ = {}
        if item_1 != 'None':
            a, b = tuple(item_1.split('---'))

            if b != 'None':
                dict_['question_ngram'] = [a]

                for item_2 in onto_terms:
                    for i in item_2:
                        if i['name'] == b:
                            dict_['onto_elem'] = i
                            out_user_mapping.append(dict_)

    return out_user_mapping




@app.route('/show_mapping_result', methods=['GET', 'POST'])
def show_mapping_result():

    """
    current_question_terms = ['bachelor', 'degree']

    mapping.init_onto_for_mapping()

    current_onto_elem_necessary, lol74 = mapping.get_onto_elem_necessary(current_question_terms)

    current_mapping = mapping.mapping_definition(current_question_terms, current_onto_elem_necessary)
    for i in current_mapping:
        print(current_mapping)
        print("\n")

    # simple_current_mapping = [current_mapping[0]['question_ngram'], current_mapping[0]['onto_elem']]
    # print(simple_current_mapping)

    """

    onto_terms = [[{'name': 'Degree', 'IRI': 'http://www.UniversityReferenceOntology.og/HERO#Degree', 'type': 'Class'},
                  {'name': 'MasterDegree', 'IRI': 'http://www.UniversityReferenceOntology.og/HERO#MasterDegree',
                   'type': 'Class'}],
                  [{'name': 'Bachelor', 'IRI': 'http://www.UniversityReferenceOntology.og/HERO#Bachelor',
                    'type': 'Class'},
                  {'name': 'BachelorDiploma', 'IRI': 'http://www.UniversityReferenceOntology.og/HERO#BachelorDiploma',
                   'type': 'Class'}]]


    simple_onto_terms = [['Degree', 'MasterDegree'],
                        ['Bachelor', 'BachelorDiploma']]




    current_mapping = [{'question_ngram': ['degree'],
                        'onto_elem': {'name': 'Degree', 'IRI': 'http://www.UniversityReferenceOntology.og/HERO#Degree',
                                      'type': 'Class'}, 'rate_compare': 1.0, 'onto_terms_necessary': simple_onto_terms[0]},
                       {'question_ngram': ['bachelor'],
                        'onto_elem': {'name': 'Bachelor', 'IRI': 'http://www.UniversityReferenceOntology.org/HERO'
                                                                 '#Bachelor',
                                      'type': 'Class'}, 'rate_compare': 1.0, 'onto_terms_necessary': simple_onto_terms[1]}]

    simple_current_mapping = [{'question_ngram': ['degree'],
                                'onto_elem': {'name': 'Degree',
                                              'IRI': 'http://www.UniversityReferenceOntology.og/HERO#Degree',
                                              'type': 'Class'}},
                                {'question_ngram': ['bachelor'],
                                 'onto_elem': {'name': 'Bachelor',
                                               'IRI': 'http://www.UniversityReferenceOntology.org/HERO#Bachelor',
                                               'type': 'Class'}}]



    l = []
    for m in current_mapping:
        tuple_t = (m['question_ngram'], m['onto_elem']['IRI'], m['rate_compare'], m['onto_terms_necessary'])
        l.append(tuple_t)

    session["mapping"] = current_mapping

    if request.method == 'GET':
        return render_template("Mapping/Mapping_result_1.html", current_mapping=current_mapping, mapping_to_display=l)


    # else: if the method is POST

    select = request.form.getlist('select_user_mapping')

    user_mapping = build_user_mapping(select, onto_terms)

    final_mapping = []

    simple_current_mapping = [{'question_ngram': ['degree'],
                                'onto_elem': {'name': 'Degree',
                                              'IRI': 'http://www.UniversityReferenceOntology.og/HERO#Degree',
                                              'type': 'Class'}},
                                {'question_ngram': ['bachelor'],
                                 'onto_elem': {'name': 'Bachelor',
                                               'IRI': 'http://www.UniversityReferenceOntology.org/HERO#Bachelor',
                                               'type': 'Class'}}]


    if len(user_mapping) != 0:

        for i in user_mapping:
            for j in simple_current_mapping:
                if i['question_ngram'] == j['question_ngram']:
                    if i['onto_elem']['name'] != j['onto_elem']['name']:
                        final_mapping.append(i)
                        simple_current_mapping.remove(j)

        for i in simple_current_mapping:
            final_mapping.append(i)

    else:
        final_mapping = simple_current_mapping

    """
    print(current_mapping)
    print("\n\n\n")
    print(user_mapping)
    print("\n\n\n")
    print(final_mapping)
    """


    return render_template("final_for_mapping.html", current_mapping=current_mapping,
                           simple_current_mapping=simple_current_mapping ,sl=select, user_mapping=user_mapping,
                           final_mapping=final_mapping)






#
#                                       END OF KARIM'S CODE
#



if __name__ == '__main__':
    # session = session()
    app.run(debug=True)
