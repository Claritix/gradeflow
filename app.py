import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
# from flask_session import Session

from helpers import no_subjects

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] =  True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gradeflow.db")

@app.route('/', methods=["GET", "POST"])
def dashboard():
    grades = db.execute("SELECT grade FROM grades")
    grades = [grade['grade'] for grade in grades]

    if request.method == 'POST':
        grade = request.form.get('grade')
        term = request.form.get('term')
        
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ?", grade)
        grade_id = grade_id[0]['grade_id']

        terms = db.execute("SELECT term FROM terms WHERE grade_id = ?", grade_id)
        terms = [term['term'] for term in terms]

        if term:
            term_id = db.execute("SELECT term_id FROM terms WHERE grade_id = ? AND term = ?", grade_id, term)
            term_id = term_id[0]['term_id']

        if grade and term:
            totalSubjects = db.execute("SELECT COUNT(subject) FROM subjects WHERE grade_id=?", grade_id)
            totalSubjects = totalSubjects[0]['COUNT(subject)']

            totalMarks = db.execute("SELECT sum(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            totalMarks = totalMarks[0]['sum(score)']

            avgMarks = db.execute("SELECT avg(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            avgMarks = avgMarks[0]['avg(score)']

            bestSubjects = db.execute("SELECT subject, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score DESC LIMIT 3", grade_id, term_id)
            
            worstSubjects = db.execute("SELECT subject, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score ASC LIMIT 3", grade_id, term_id)
            
            importantSubjects = db.execute("SELECT subject, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? AND important = 1 LIMIT 3", grade_id, term_id) 

            return render_template("dashboard.html", 
                                   grades=grades, terms=terms, selected_grade=grade, selected_term=term, 
                                   subject_count=totalSubjects, total_marks=totalMarks, avg_marks = avgMarks,
                                   best_subjects=bestSubjects, worst_subjects=worstSubjects, important_subjects=importantSubjects
                                )
        
        return render_template("dashboardempty.html", grades=grades, terms=terms, selected_grade=grade, selected_term=term)
    
    elif request.method == 'GET':
        return render_template("dashboardempty.html", grades=grades)

@app.route('/', methods=["GET", "POST"])
@no_subjects
def no_subjects():
    grades = db.execute("SELECT grade FROM grades")
    grades = [grade['grade'] for grade in grades]

    return render_template("dashboard.html", grades=grades)

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

