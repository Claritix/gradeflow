import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import no_subjects, login_required, apology

# Setup flask
app = Flask(__name__)

# Setup session info
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gradeflow.db")

# Route for login, homepage
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

# Logout and clear session
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Add new account to db and log in
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

# Dashboard for marks
@app.route('/', methods=["GET", "POST"])
@login_required
def dashboard():
    # Get user id
    uid = session.get("user_id")

    # Get all grades associated with user
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Get grade and term selected by user
        grade = request.form.get('grade')
        term = request.form.get('term')
        
        # Get grade_id of selected grade
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']

        # Get all terms associated with the grade
        terms = db.execute("SELECT term FROM terms WHERE grade_id = ?", grade_id)
        terms = [term['term'] for term in terms]

        # Check if term has been submitted and get term_id for term
        if term:
            term_id = db.execute("SELECT term_id FROM terms WHERE grade_id = ? AND term = ?", grade_id, term)
            term_id = term_id[0]['term_id']

        # If both grade and term have been submitted, proceed with calculating data
        if grade and term:
            # Get the amount of subjects in the grade
            totalSubjects = db.execute("SELECT COUNT(subject_name) FROM subjects WHERE grade_id=?", grade_id)
            totalSubjects = totalSubjects[0]['COUNT(subject_name)']

            # Get sum of all marks of the term
            totalMarks = db.execute("SELECT sum(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            totalMarks = totalMarks[0]['sum(score)']

            # Get average marks of the term
            avgMarks = db.execute("SELECT avg(score) FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id=?", grade_id, term_id)
            avgMarks = round(avgMarks[0]['avg(score)'], 2)

            # Get all subjects
            subjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id = ? AND term_id = ? ORDER BY score DESC", grade_id, term_id)

            # Get top 3 best subjects of the term
            bestSubjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score DESC LIMIT 3", grade_id, term_id)
            
            # Get worst 3 subjects of the term
            worstSubjects = db.execute("SELECT subject_name, score FROM marks JOIN subjects on marks.subject_id = subjects.subject_id WHERE grade_id=? AND term_id = ? ORDER BY score ASC LIMIT 3", grade_id, term_id)

            # Get randon subjects not in the above 2 lists
            randomSubjects = []

            for subject in subjects:
                # Check if subject is not in bestSubjects or worstSubjects
                if subject not in bestSubjects and subject not in worstSubjects:
                    # Add subject to randomSubjects
                    randomSubjects.append(subject)
                # Break the loop if randomSubjects has more than 5 subjects
                if len(randomSubjects) >= 5:
                    break
            
            # Render page with everything needed
            return render_template("dashboard.html", 
                                   grades=grades, terms=terms, selected_grade=grade, selected_term=term, 
                                   subject_count=totalSubjects, total_marks=totalMarks, avg_marks = avgMarks,
                                   best_subjects=bestSubjects, worst_subjects=worstSubjects, random_subjects=randomSubjects
                                )
        
        # If grade or term hasn't been chosen yet
        return render_template("dashboardempty.html", grades=grades, terms=terms, selected_grade=grade, selected_term=term)
    
    # User reached route via GET (as by clicking a link)
    elif request.method == 'GET':
        return render_template("dashboardempty.html", grades=grades)

# No subjects have been added yet
@app.route('/', methods=["GET", "POST"])
@login_required
@no_subjects
def no_subjects():
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    return render_template("dashboard.html", grades=grades)

# Grade editing page
@app.route('/grades', methods=["GET", "POST"])
@login_required
def grades():
    # Get user id and grades associated with user
    uid = session.get("user_id")
    grades = db.execute("SELECT grade_id, grade FROM grades WHERE user_id = ? ORDER BY grade ASC", uid)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Get new grade needed to be added
        new_grade = request.form.get('newGrade')
        
                # Validate if grade is provided
        if not new_grade:
            return apology("grade must be provided", 400)
            
        # Validate grade format (assuming grades should be numbers or text)
        if len(new_grade) > 20:
            return apology("grade name too long", 400)

        # Check if grade already exists for this user
        existing_grade = db.execute("SELECT * FROM grades WHERE grade = ? AND user_id = ?", new_grade, uid)
        if existing_grade:
            return apology("grade already exists", 400)
        
        # Add grade into db
        db.execute("INSERT INTO grades (grade, user_id) VALUES (?, ?)", new_grade, uid)

        # Return to grades page
        return redirect(url_for('grades'))

    # User reached route via GET (as by clicking a link)
    else:
        # Return grade editing page
        return render_template("grades.html", grades=grades)

# Delete grade
@app.route('/del-grade', methods=["POST"])
@login_required
def del_grades():
    # Get the user id and grade_id from the form
    uid = session.get("user_id")
    grade_id = request.form.get("grade")
    
    if not grade_id:
        return apology("No grade selected for deletion.", 403)

    # Ensure the grade belongs to the user (prevent other users from deleting it)
    grade = db.execute("SELECT * FROM grades WHERE grade_id = ? AND user_id = ?", grade_id, uid)

    if not grade:
        return apology("This grade does not belong to you or does not exist.", 403)
    
    # Step 1: Delete all marks related to this grade (using subjects and terms)
    db.execute("""
        DELETE FROM marks
        WHERE subject_id IN (
            SELECT subject_id FROM subjects
            WHERE grade_id = ?
        ) OR term_id IN (
            SELECT term_id FROM terms
            WHERE grade_id = ?
        );
    """, grade_id, grade_id)

    # Step 2: Delete subjects related to this grade
    db.execute("""
        DELETE FROM subjects
        WHERE grade_id = ?;
    """, grade_id)
    
    # Step 3: Delete terms related to this grade
    db.execute("""
        DELETE FROM terms
        WHERE grade_id = ?;
    """, grade_id)
    
    # Step 4: Delete the grade itself
    db.execute("""
        DELETE FROM grades
        WHERE grade_id = ?;
    """, grade_id)
    
    return redirect("/grades")

# Show and add terms
@app.route('/terms', methods=["GET", "POST"])
@login_required
def terms():
    # Get user_id and grades
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    # Check if user reached via GET and return terms list
    if request.method == 'GET':
        return render_template("terms.html", grades=grades)
    
    # If user reached via POST
    else:
        # Get submitted grade and grade_id
        grade = request.form.get('grade')
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']

        # Get all terms associated with the grade
        terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)
        
        # Return template with all required data
        return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

# Add new term
@app.route('/add-term', methods=['POST'])
@login_required
def addTerm():
    # Get user_id and all grades associated with user_id
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]

    # Get submitted grade and validate it belongs to user
    grade_id_result = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    if not grade_id_result:
        return apology("invalid grade selection", 403)
    
    grade_id = grade_id_result[0]['grade_id']

    # Validate new term
    term = request.form.get('new_term')
    if not term:
        return apology("term name cannot be empty", 400)
    
    # Validate term length
    if len(term) > 20:
        return apology("term name too long (maximum 20 characters)", 400)
    
    # Check if term already exists for this grade
    existing_term = db.execute("SELECT term FROM terms WHERE term = ? AND grade_id = ?", term, grade_id)
    if existing_term:
        return apology("term already exists for this grade", 400)

    try:
        # Add term into associated grade
        db.execute("INSERT INTO terms (term, grade_id) VALUES (?, ?)", term, grade_id)
    except Exception as e:
        return apology("error adding term to database", 500)


    # Get new list of terms
    terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)

    # Return template with new data
    return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

# Delete a term
@app.route('/del-term', methods=["POST"])
@login_required
def del_terms():
    # Get user id from session
    uid = session.get("user_id")
    
    # Get the selected grade and term_id from the form
    grade = request.form.get('grade')
    term_id = request.form.get('term_id')
    
    # Fetch the grade_id for the given grade and user_id
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    
    # Ensure the grade exists and belongs to the user
    if not grade_id:
        return apology("This grade does not exist or does not belong to you.", 403)
    
    grade_id = grade_id[0]['grade_id']
    
    # Ensure the term exists
    term = db.execute("SELECT * FROM terms WHERE term_id = ? AND grade_id = ?", term_id, grade_id)
    if not term:
        return apology("This grade does not exist or does not belong to you.", 403)

    # Step 1: Delete all marks associated with the selected term and grade
    db.execute("""
        DELETE FROM marks
        WHERE term_id = ? AND subject_id IN (
            SELECT subject_id FROM subjects WHERE grade_id = ?
        );
    """, term_id, grade_id)

    # Step 2: Delete all subjects associated with the selected term and grade
    db.execute("""
        DELETE FROM subjects
        WHERE grade_id = ? AND subject_id IN (
            SELECT subject_id FROM subjects WHERE grade_id = ? AND term_id = ?
        );
    """, grade_id, grade_id, term_id)

    # Step 3: Delete the term itself
    db.execute("DELETE FROM terms WHERE term_id = ? AND grade_id = ?", term_id, grade_id)

    # Fetch updated grades and terms after deletion
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]
    terms = db.execute("SELECT term_id, term FROM terms WHERE grade_id = ? ORDER BY term ASC", grade_id)

    # Return updated terms page
    return render_template("terms.html", grades=grades, selected_grade=grade, terms=terms)

# Check subjects
@app.route('/subjects', methods=["GET", "POST"])
@login_required
def subjects():
    # Get user_id and grades associated with user
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)

    # Check if user reached via GET
    if request.method == 'GET':
        return render_template("subjects.html", grades=grades)
    
    # If user reached via POST
    else:
        # Get requested grade and grade_id
        grade = request.form.get('grade')
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        grade_id = grade_id[0]['grade_id']

        # Get all subjects associated with grade
        subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)

        # Return template with data
        return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

# Add new subject
@app.route('/add-subject', methods=["POST"])
@login_required
def add_subject():
    # Get user_id and all grades associated with user
    uid = session.get("user_id")
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)

    # Get requested grade and grade_id
    grade = request.form.get('grade')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    grade_id = grade_id[0]['grade_id']

    # Validate subject input
    if not request.form.get('subject'):
        return apology("subject name cannot be empty", 400)

    # Get new subject and convert to lowercase
    subject = request.form.get('subject').lower().strip()

    # Validate subject name length
    if len(subject) < 2:
        return apology("subject name too short (minimum 2 characters)", 400)
    if len(subject) > 30:
        return apology("subject name too long (maximum 30 characters)", 400)

    # Check for invalid characters in subject name
    if not subject.replace(" ", "").isalnum():
        return apology("subject name can only contain letters, numbers and spaces", 400)

    # Check if subject already exists in this grade
    existing_subject = db.execute("SELECT subject_name FROM subjects WHERE subject_name = ? AND grade_id = ?", 
                                subject, grade_id)
    if existing_subject:
        return apology("subject already exists in this grade", 400)

    # Check maximum number of subjects per grade (if there's a limit)
    subject_count = db.execute("SELECT COUNT(*) as count FROM subjects WHERE grade_id = ?", grade_id)
    if subject_count[0]['count'] >= 20:  # Assuming max 20 subjects per grade
        return apology("maximum number of subjects reached for this grade", 400)

    try:
        # Add subject into db
        db.execute("INSERT INTO subjects (subject_name, grade_id, important) VALUES (?, ?, ?)", 
                  subject, grade_id, 0)
    except Exception as e:
        return apology("error adding subject to database", 500)

    # Get new subject list
    subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)

    # Return template with new data
    return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

# Delete subject
@app.route('/del-subject', methods=["POST"])
@login_required
def del_subject():
    # Get user id from session
    uid = session.get("user_id")
    
    # Get the selected grade and subject from the form
    grade = request.form.get('grade')
    subject_id = request.form.get('subject')

    # Fetch the grade_id for the given grade and user_id
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)

    # Ensure the grade exists and belongs to the user
    if not grade_id:
        return apology("This grade does not exist or does not belong to you.", 403)
    
    grade_id = grade_id[0]['grade_id']
    
    # Ensure the subject exists in the selected grade
    subject = db.execute("SELECT subject_id FROM subjects WHERE subject_id = ? AND grade_id = ?", subject_id, grade_id)
    if not subject:
        return apology("This subject does not exist or does not belong to the selected grade.", 403)

    # Step 1: Delete all marks associated with the subject
    db.execute("DELETE FROM marks WHERE subject_id = ?", subject_id)

    # Step 2: Delete the subject
    db.execute("DELETE FROM subjects WHERE subject_id = ? AND grade_id = ?", subject_id, grade_id)

    # Fetch updated grades and subjects after deletion
    grades = db.execute("SELECT grade FROM grades WHERE user_id = ?", uid)
    grades = [grade['grade'] for grade in grades]
    subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id)

    # Return updated subjects page
    return render_template("subjects.html", grades=grades, subjects=subjects, selected_grade=grade)

# Marks page
@app.route('/marks', methods=["POST", "GET"])
@login_required
def marks():
    # Get user_id and grades associated with user
    uid = session.get("user_id")
    grades = db.execute("SELECT grade_id, grade FROM grades WHERE user_id = ?", uid)

    # If user reached via link
    if request.method == 'GET':
        return render_template("marks.html", grades=grades)

    # If user reached via post
    else:
        # Get selected grade and term
        grade = request.form.get('grade')
        term = request.form.get('term')

        # Get grade id and all terms associated with grade
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
        terms = db.execute("SELECT term FROM terms WHERE grade_id = ?", grade_id[0]['grade_id'])
        
        # Get all subjects associated with grade
        subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id[0]['grade_id'])

        # If user selected term
        if term:
            # Get term_id
            term_id = db.execute("SELECT term_id FROM terms WHERE term = ? AND grade_id = ?", term, grade_id[0]['grade_id'])
            term_id = term_id[0]['term_id']

            # Get score for each subject
            for subject in subjects:
                result = db.execute("SELECT marks.score FROM subjects JOIN marks ON subjects.subject_id = marks.subject_id WHERE marks.term_id = ? AND subjects.subject_id = ?", term_id, subject['subject_id'])

                # Assign the score or set a default value if no score is found
                subject['score'] = result[0]['score'] if result else 0

        # Return template with data
        return render_template("marks.html", grades=grades, terms=terms, selected_grade=grade, subjects=subjects, selected_term=term)

# Submit marks
@app.route('/submit-marks', methods=["POST"])
@login_required
def submit_marks():
    # Get user_id
    uid = session.get("user_id")

    # Get requested grade, term and respective grade_id, term_id
    grade = request.form.get('grade')
    term = request.form.get('term')
    grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ? AND user_id = ?", grade, uid)
    term_id = db.execute("SELECT term_id FROM terms WHERE term = ? AND grade_id = ?", term, grade_id[0]['grade_id'])
    term_id = term_id[0]['term_id']

    # Get all subjects associated with grade
    subjects = db.execute("SELECT subject_id, subject_name, important FROM subjects WHERE grade_id = ?", grade_id[0]['grade_id'])

    # Get all requested marks and insert into db
    for subject in subjects:
        subject_id = subject['subject_id']
        # Get subject from website
        subject['score'] = request.form.get(f'marks_{subject_id}')

        # Check if score was submitted and insert into db
        if subject['score']:
            try:
                score_float = float(subject['score'])
                if score_float < 0 or score_float > 100:
                    return apology(f"invalid score for {subject['subject_name']} (must be between 0 and 100)", 400)
                
                db.execute(
                    "INSERT INTO marks (subject_id, term_id, score) VALUES (?, ?, ?) ON CONFLICT(subject_id, term_id) DO UPDATE SET score = excluded.score",
                    subject_id, term_id, score_float
                )
            except ValueError:
                return apology(f"invalid score format for {subject['subject_name']}", 400)
        
    # Redirect to marks
    return redirect(url_for('marks')) 

# Settings page
@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html")

# Change password
@app.route('/change-password', methods=["POST"])
@login_required
def change_password():
    # Ensure username was submitted
    if not request.form.get("old"):
        return apology("must provide old password", 403)

    # Ensure password was submitted
    elif not request.form.get("password"):
        return apology("must provide new password", 403)

    # Ensure the two passwords match
    elif request.form.get("password") != request.form.get("confirmation"):
        return apology("password don't match", 400)

    # Initialize variables
    old = request.form.get("old")
    new = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Get user id
    uid = session.get("user_id")

    # Get current password hash
    current_hash = db.execute("SELECT hash FROM users WHERE id = ?", uid)

    # Check if submitted old password and current password match
    # If not, return an apology
    if not check_password_hash(current_hash[0]['hash'], old):
        return apology("old password doesn't match", 400)

    # Update to new password
    new_hash = generate_password_hash(new)
    db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, uid)

    # Return to login clearing session ID
    return redirect("/login")

# Change username
@app.route("/change-username", methods=["POST"])
def change_username():
    if request.method == "POST":
        # Ensure current password was submitted
        if not request.form.get("current_password"):
            return apology("must provide old password", 403)

        # Ensure new username was submitted
        elif not request.form.get("new_username"):
            return apology("must provide new username", 403)

        # Initialize variables
        old_password = request.form.get("current_password")
        new_username = request.form.get("new_username")

        # Get user id from session
        uid = session.get("user_id")

        # Get current password hash
        current_hash = db.execute("SELECT hash FROM users WHERE id = ?", uid)

        # Check if the old password matches the current hash in the database
        if not check_password_hash(current_hash[0]['hash'], old_password):
            return apology("old password doesn't match", 400)

        # Update the username
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, uid)

        return redirect("/login")

# Delete account
@app.route("/reset", methods=["POST"])
def reset():
    # Ensure user is logged in (this check is required to make sure the user is authenticated)
    if not session.get("user_id"):
        flash("You must be logged in to reset data.", "danger")
        return redirect("/login")
    
    # Get the user id from session
    user_id = session["user_id"]
    
    # Execute the SQL queries to delete all associated data in the correct order
    db.execute("""
        DELETE FROM marks
        WHERE subject_id IN (
            SELECT subject_id FROM subjects
            WHERE grade_id IN (
                SELECT grade_id FROM grades
                WHERE user_id = ?
            )
        ) OR term_id IN (
            SELECT term_id FROM terms
            WHERE grade_id IN (
                SELECT grade_id FROM grades
                WHERE user_id = ?
            )
        );
    """, user_id, user_id)

    db.execute("""
        DELETE FROM subjects
        WHERE grade_id IN (
            SELECT grade_id FROM grades
            WHERE user_id = ?
        );
    """, user_id)
    
    db.execute("""
        DELETE FROM terms
        WHERE grade_id IN (
            SELECT grade_id FROM grades
            WHERE user_id = ?
        );
    """, user_id)
    
    db.execute("""
        DELETE FROM grades
        WHERE user_id = ?;
    """, user_id)
    
    # Finally, delete the user from the users table
    db.execute("""
        DELETE FROM users
        WHERE id = ?;
    """, user_id)
    
    return redirect("/login")

    

