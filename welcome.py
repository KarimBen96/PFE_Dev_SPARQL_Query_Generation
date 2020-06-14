from flask import Flask, render_template, request, redirect, url_for, session

import app


@app.route('/welcome', methods=['GET'])
def welcome():
    return render_template("Welcome.html")