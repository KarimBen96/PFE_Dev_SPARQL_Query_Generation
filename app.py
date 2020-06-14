import os

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from Phases.Question_Classification.Question_Classifiaction import classer_question
from Phases.Question_Linguistic_Treatments import Question_Linguistic_Treatments as qlt

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


list_stop_words = qlt.light_list_stop_words


@app.route('/select_ontology', methods=['GET', 'POST'])
def select_ontology():
    see_alert = False
    if request.method == 'GET':
        return render_template("Select_ontology.html", see_alert=see_alert)

    # else: if the method is POST
    file_ontology = request.files['file_ontology']
    filename = secure_filename(file_ontology.filename)
    file_ontology.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    session["filename_ontolody"] = filename
    # return render_template("Select_ontology.html", see_alert=see_alert)
    return redirect(url_for('ask_question'))
    # return render_template("file_up_successfull.html", file=filename)


@app.route('/ask_question', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'GET':
        return render_template("Ask_question.html")

    # else: if the method is POST
    question = request.form["textarea_question"]
    session["question"] = question
    # question = request.form.get("textarea_question")
    question_class = classer_question(question)
    session["question_class"] = question_class
    return redirect(url_for('ask_question_class'))
    # return render_template("Ask_question_class.html", classe=classe)


@app.route('/ask_question_class', methods=['GET', 'POST'])
def ask_question_class():
    if request.method == 'GET':
        question_class = session["question_class"]
        question = session["question"]
        return render_template("Ask_question_class.html", question_class=question_class, question=question)

    # else: if the method is POST
    user_question_class = request.form["input_class_corrected"]
    if user_question_class == "":
        session["user_question_class"] = user_question_class
    return redirect(url_for("question_key_terms_extraction"))
    # return render_template("final.html", c=user_question_class)


@app.route('/question_key_terms_extraction', methods=['GET', 'POST'])
def question_key_terms_extraction():
    question = session["question"]
    list_question_terms = question.split(' ')
    list_question_lemma = qlt.question_list_lemma(list_question_terms)
    qrt, list_question_key_terms = qlt.question_roots(question)

    session["list_question_key_terms"] = list_question_key_terms

    if request.method == 'GET':
        return render_template("Question_key_terms_extraction.html", question=question,
                               list_question_terms=list_question_terms,
                               list_question_key_terms=list_question_key_terms,
                               list_question_lemma=list_question_lemma)

    # else: if the method is POST
    user_question_key_terms = request.form.getlist("checkbox_terms")
    session["list_question_key_terms"] = user_question_key_terms

    return render_template("final.html", user_question_key_terms=user_question_key_terms)


#
#                                       END OF KARIM'S CODE
#


#


if __name__ == '__main__':
    session = session()
    app.run(debug=True)



