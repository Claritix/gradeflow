import requests

from flask import Flask, redirect, render_template, session, request, url_for
from cs50 import SQL
from functools import wraps

app = Flask(__name__)
db = SQL("sqlite:///gradeflow.db")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def no_subjects(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Get the selected grade from the request (e.g., from the session or query string)
        selected_grade = request.form.get('grade')  # Assuming the grade is passed in the route URL
        
        grade_id = db.execute("SELECT grade_id FROM grades WHERE grade = ?", selected_grade)
        grade_id = grade_id[0]['grade_id']

        # Query the database to check if there are subjects for the selected grade
        # Replace 'subjects' and 'grade' with your actual table and column names
        subjects = db.execute(
            "SELECT * FROM subjects WHERE grade_id = ?", grade_id
        )
        
        # If there are subjects, redirect or display a message
        if subjects:
            return redirect(url_for('/'))  # Redirect to another route if there are subjects
        
        # Otherwise, allow the original route to be accessed
        return func(*args, **kwargs)
    
    return decorated_function