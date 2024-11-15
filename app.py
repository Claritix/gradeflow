import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] =  True

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/grades')
def grades():
    return render_template("grades.html")

@app.route('/marks')
def marks():
    return render_template("marks.html")

@app.route('/stats')
def stats():
    return render_template("stats.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")