import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import no_subjects, login_required, apology

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gradeflow.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure the two passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password don't match", 400)

        # Initalize
        username = request.form.get("username")
        password = request.form.get("password")
        repassword = request.form.get("confirmation")

        # Hash password
        hashed_pw = generate_password_hash(password)

        # Insert the user into database while checking if there are no users with the same username
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_pw)
        except ValueError:
            return apology("user already exists", 400)

        # Get ID of user
        id = db.execute(
            "SELECT id FROM users WHERE username = ?", username
        )

        # Remember the registered user
        session["user_id"] = id[0]["id"]

        # Redirect to home page
        flash("Registered!")
        return redirect("/")

@app.route('/', methods=["GET", "POST"])
@login_required
def dashboard():
    uid = session.get("user_id")

    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    if request.method == 'POST':
        grade = request.form.get('grade')
        term = request.form.get('term')
        
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']

        terms = db.execute("SELECT term FROM terms WHERE grade_id = ?", grade_id)
        terms = [term['term'] for term in terms]

        if term:
            term_id = db.execute("SELECT term_id FROM terms WHERE grade_id = ? AND term = ?", grade_id, term)
            term_id = term_id[0]['term_id']

        if grade and term:
            totalSubjects = db.execute("SELECT COUNT(subject_name) FROM subjects WHERE grade_id=?", grade_id)
            totalSubjects = totalSubjects[0]['COUNT(subject_name)']

            totalMarks = db.execute("SELECT sum(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            totalMarks = totalMarks[0]['sum(score)']

            avgMarks = db.execute("SELECT avg(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            avgMarks = avgMarks[0]['avg(score)']

            bestSubjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score DESC LIMIT 3", grade_id, term_id)
            
            worstSubjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score ASC LIMIT 3", grade_id, term_id)
            
            importantSubjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? AND important = 1 LIMIT 3", grade_id, term_id) 

            return render_template("dashboard.html", 
                                   grades=grades, terms=terms, selected_grade=grade, selected_term=term, 
                                   subject_count=totalSubjects, total_marks=totalMarks, avg_marks = avgMarks,
                                   best_subjects=bestSubjects, worst_subjects=worstSubjects, important_subjects=importantSubjects
                                )
        
        return render_template("dashboardempty.html", grades=grades, terms=terms, selected_grade=grade, selected_term=term)
    
    elif request.method == 'GET':
        return render_template("dashboardempty.html", grades=grades)

@app.route('/', methods=["GET", "POST"])
@login_required
@no_subjects
def no_subjects():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    return render_template("dashboard.html", grades=grades)

@app.route('/grades', methods=["GET", "POST"])
@login_required
def grades():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade_id, grade FROM grades WHERE user_id = ? ORDER BY grade ASC", uid)

    if request.method == 'POST':
        new_grade = request.form.get('newGrade')
        
        db.execute("INSERT INTO grades (grade, user_id) VALUES (?, ?)", new_grade, uid)

        return redirect(url_for('grades'))

    else:
        return render_template("grades.html", grades=grades)
    
@app.route('/del-grade', methods=["POST"])
@login_required
def del_grades():
    uid = session.get("user_id")
    grade_id = request.form.get('grade')
    db.execute("DELETE FROM grades WHERE grade_id = ? AND user_id = ?", grade_id, uid)
    db.execute("DELETE FROM subjects WHERE grade_id = ? AND user_id = ?", grade_id, uid)

    return redirect(url_for('grades'))

@app.route('/terms', methods=["GET", "POST"])
@login_required
def terms():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    if request.method == 'GET':
        return render_template("terms.html", grades=grades)
    
    else:
        grade = request.form.get('grade')
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']

        terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)
        
        return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

@app.route('/add-term', methods=['POST'])
@login_required
def addTerm():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    grade = request.form.get('grade')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    grade_id = grade_id[0]['grade_id']
    
    term = request.form.get('new_term')
    
    db.execute("INSERT INTO terms (term, grade_id) VALUES (?, ?)", term, grade_id)
    terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)

    return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

@app.route('/del-term', methods=["POST"])
@login_required
def del_terms():
    uid = session.get("user_id")
    grade = request.form.get('grade')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    grade_id = grade_id[0]['grade_id']

    term_id = request.form.get('term_id')
    
    db.execute("DELETE FROM terms WHERE grade_id = ? AND term_id = ?", grade_id, term_id)    
    db.execute("DELETE FROM subjects WHERE grade_id = ? AND term_id = ?", grade_id, term_id)

    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]
    terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)
    return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

    
@app.route('/subjects', methods=["GET", "POST"])
@login_required
def subjects():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)

    if request.method == 'GET':
        return render_template("subjects.html", grades=grades)
    
    else:
        grade = request.form.get('grade')

        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']
        terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)

        subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)
        print(subjects)
        return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

@app.route('/add-subject', methods=["POST"])
@login_required
def add_subject():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grade = request.form.get('grade')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    grade_id = grade_id[0]['grade_id']

    subject = request.form.get('subject').lower()

    db.execute("INSERT INTO subjects (subject_name, grade_id, important) VALUES (?, ?, ?)", subject, grade_id, 0)  

    subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)
    return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

@app.route('/del-subject', methods=["POST"])
@login_required
def del_subject():
    uid = session.get("user_id")
    grade = request.form.get('grade')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    grade_id = grade_id[0]['grade_id']

    subject = request.form.get('subject')

    db.execute("DELETE FROM subjects WHERE subject_id = ? AND grade_id = ?", subject, grade_id)

    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)

    return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

@app.route('/marks', methods=["POST", "GET"])
@login_required
def marks():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade_id, grade FROM grades WHERE user_id = ?", uid)

    if request.method == 'GET':
        return render_template("marks.html", grades=grades)

    else:
        grade = request.form.get('grade')
        term = request.form.get('term')

        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        terms = db.execute("SELECT term FROM terms WHERE grade_id = ?", grade_id[0]['grade_id'])

        subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id[0]['grade_id'])
        print(subjects)

        return render_template("marks.html", grades=grades, terms=terms, selected_grade=grade, subjects=subjects, selected_term=term)

        

@app.route('/stats')
@login_required
def stats():
    uid = session.get("user_id")
    return render_template("stats.html")

@app.route('/settings')
@login_required
def settings():
    uid = session.get("user_id")
    return render_template("settings.html")

