# GradeFlow

## Video Demo: https://youtu.be/eSKBJSJf8mU

## Description:

GradeFlow is an app designed to log and track academic grades. You can add grades, terms and subjects through the intuitive UI interface. You can view the basic information such as averages and total marks right from the dashboard. You can add and modify marks easily from the webpage. 

The GradeFlow app is designed with an account system, in which you can store all your data inside your account. You can easily track your academic progress or just get a summary with this app.

## Technologies Used:

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask, SQLite3
- **Tools:** Git, CS50 Library

## Features:

1. **Grade and Term Entry:** Users can add their school grades and terms and save them to the account through the database.
2. **Subject Entry:** Users can add any subject they want to a specific grade and save them to the database.
3. **Marks Entry:** Users can add and modify the marks for any subject of any term easily from the website.
4. **Grade Visualization:** Users can choose specific grades and marks and then view simple data of their progress such as averages, total marks, best subjects, worst subjects etc..
5. **Account Management:** Users can register for an account and keep all the information they input synced and secure.
6. **Account Customization:** Users can change their username, password and also delete their account from the settings page of the website.

## Installation

To set up the project locally, follow these steps:

1. Clone the repository

```bash
git clone https://github.com/Claritix/gradeflow.git
cd gradeflow
```

1. Install dependencies

```bash
pip3 install -r requirements.txt
```

1. Run the webapp

```bash
flask run
```

4. Visit `http://127.0.0.1:5000` in your web browser to view the app.

## File Descriptions:

### Backend Files:

- `app.py` : This is the main Flask application that handles routing and backend logic for the web app. It processes requests, interacts with the database, and renders templates. Adds and modifies database entries and account functionality.
- `helpers.py` : Extends functionality of main [app.py](http://app.py) by adding features such as login required decorator and apology function.
- `gradeflow.db` : Main database file written in sqlite3 for storing all data, stores data such as usernames and passwords, grades, terms, subjects and marks.
- `requirements.txt` : Lists the Python dependencies required to run the project, including Flask, Flask-Session, and any other necessary libraries.

### Frontend Files

- `static/style.css` : Contains the CSS styling rules for the app's layout and design, built on top of bootstrap.
- `static/main.js` :  JavaScript file with functions to get user input and submit to backend.

### Template Files

- **`templates/apology.html`**: Displays an error message for invalid actions, such as when the user tries to access a page that doesn’t exist using grumpy cat memegen. Built by CS50.
- **`templates/dashboard.html`**: Main dashboard page for logged-in users, selectors for choosing grades and terms and then showing an overview of their grades, performance trends such as total marks and averages, and quick links to other sections of the app through the sidebar.
- **`templates/grades.html`**: Page where users can view, delete, add and manage grades associated with the account, as well as having links to the other modification pages such as terms and subjects.
- **`templates/login.html`**: Login page where users can enter their credentials to access their account. Main page redirected to when not logged in.
- **`templates/register.html`**: Registration page where new users can create an account.
- **`templates/subjects.html`**: Page displaying a list of subjects for each grade chosen by the user, user can add or remove subjects as they like.
- **`templates/dashboardempty.html`**: Template for an empty dashboard, used when there is no grade data available for the user.
- **`templates/layout.html`**: The base layout that includes shared elements like file data such as bootstrap, title elements, headers and the collapsible sidebar component.
- **`templates/marks.html`**: Displays the marks entry form, allowing users to input marks for different subjects depending on the chosen grade and term.
- **`templates/settings.html`**: Page where users can change their account username or account password as well as having the ability to delete the user account.
- **`templates/terms.html`**: Page displaying a list of term for each grade chosen by the user, user can add or remove terms as they like.

## Design Choices

1. **Account Management System:**
    
    Although I initially considered not using an account system, I decided to implement one to avoid a messy database. Without user authentication, it would be challenging to maintain clean, separate data for each user, especially if the app were publicly hosted.
    
2. **CSS Framework:**
I chose **Bootstrap** instead of TailwindCSS for its simplicity and familiarity. It provides a responsive grid system and pre-built components that accelerated development. While **Tailwind CSS** offers more customization, Bootstrap was a better fit for this project given my prior experience with it.
3. **Using Flask instead of JavaScript:**
I used **Flask** instead of JavaScript for the backend due to Python's simpler syntax and ease of use. Flask is lightweight and well-suited for handling routing, templating, and user sessions, which made it a straightforward choice for this project.

## Future Improvements

- **User Authentication**: Implementing a more sophisticated user authentication system.
- **Data Management:** Ability to export and import the data in CSV or other format for easier use/
- **Data Sync:** Syncing user data with Google Drive or other cloud options to increase security.
- **Mobile Optimization**: Making the webapp more responsive and optimized for better usability on mobile devices or tablets.