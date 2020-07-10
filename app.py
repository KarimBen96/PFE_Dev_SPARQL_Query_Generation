from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from Phases.Question_Classification.Question_Classifiaction import classer_question
from Phases.Question_Linguistic_Treatments import Question_Linguistic_Treatments as qlt
# from Phases.Mapping import Mapping as mapping
from Phases.mapping import mapping as mapping

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


@app.route('/show_mapping_result', methods=['GET', 'POST'])
def show_mapping_result():

    current_onto_elem_necessary, lol74 = mapping.get_onto_elem_necessary(current_question_terms)
    current_mapping = mapping.mapping_definition(current_question_terms, current_onto_elem_necessary)
    session["mapping"] = current_mapping

    if request.method == 'GET':
        return render_template("Mapping/Mapping_result_1.html", current_mapping=current_mapping)


    # else: if the method is POST

    return render_template("final.html", user_question_key_terms=None)





#
#                                       END OF KARIM'S CODE
#


#


if __name__ == '__main__':
    # session = session()
    app.run(debug=True)
