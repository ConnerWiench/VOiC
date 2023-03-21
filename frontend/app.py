from flask import Flask, render_template, request, redirect, session, json
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import time

DOCUMENT_PATH = "../case_documents/"

app = Flask(__name__)

conn = mysql.connector.connect(
    host = "localhost",
    user = "voic",
    password = "raspberry",
    database = "mydb",
)

# ----- Flask Functions -----

@app.route('/')
def main():
    # if not session.get('user'):
        # print("Redirecting...")
        # return redirect('/register')
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    _username = request.form['signUser']
    _first = request.form['signFirst']
    _last = request.form['signLast']
    _level = request.form['signLevel']
    _password = request.form['signPsk']
    _conPassword = request.form['signConPsk']
    _email = request.form['signEmail']
    _created = time.strftime('%Y-%m-%d %H:%M:%S')

    # Validate Values
    if not (_username and _email and _first and _last and _level and _password and _conPassword):
        print("All fields need to be filled")
        return json.dumps({'html':'<span>Enter the required fields</span>'})
    elif _password != _conPassword:
        print("Passwords must Match")
        return json.dumps({'html':'<span>Passwords must Match</span>'})

    # Hashes the password for proper security
    _hashed_password = generate_password_hash(_password)

    # Need to add email column to mydb court_user column
    # Attempts to add user into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_user(user_name, user_first, user_last, "\
                            "user_level, user_created, user_password)\n"\
                            f"VALUES ('{_username}', '{_first}', '{_last}', {_level}, "\
                            f"'{_created}', '{_hashed_password}';)")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        return # Add actual returnls

    return # Some sort of redirect to login page


@app.route("/case_list")
def case_list(facts = None):

    with conn.cursor() as cursor:
        if facts == None:
            cursor.execute("SELECT case_number, case_document, case_time_created\n"\
                            "FROM court_case;")
        else:
            cursor.execute("SELECT case_number, case_document, case_time_created\n"\
                            "FROM court_case;")
                            #Put Where statement to check the fact blob
        cases = cursor.fetchall()
    for case in cases:
        print(case)
        
    return render_template('case_list.html', cases=cases)

@app.route("/case_create")
def case_create():
    return render_template("case_create.html")

@app.route("/api/case_create", methods=["POST"])
def api_case_create():
    _case_id = convert_to_alpnum(request.form["form_id"])
    _case_charge = convert_to_alpnum(request.form["form_charge"])
    _case_verdict = convert_to_alpnum(request.form["form_verdict"])
    _case_user_created = session.get("user")
    _case_time_created = time.strftime('%Y-%m-%d %H:%M:%S')
    _case_document = convert_to_alpnum(request.form["form_document"])
    _case_file_path = f"{DOCUMENT_PATH}{_case_document}"

    # Users the session saved username to get the user's access level.
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name == {_case_user_created};")
        _case_level_required = cursor.fetchone()
    
    # Attempts to add document into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_docs(docs_title, docs_path)"\
                        f"VALUES ({_case_document}, {_case_file_path})")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        return  # Put API rejection string here

    # Attempts to add case with attached document
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_case(case_number, case_charge, "\
                            "case_user_created, case_document, case_verdict, "\
                            "case_time_created, case_level_required)\n"\
                            f"VALUES ({_case_id}, '{_case_charge}', '{_case_user_created}', "\
                            f"'{_case_document}', '{_case_verdict}', '{_case_time_created}'"\
                            f"{_case_level_required});")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        return  # Put API rejection string here
    
    return # Redirect to case edit page


# ----- Normal Functions ----- (Move to different file eventually)

def convert_to_alpnum(str):
    newStr = ""
    for i in str:
        if i.isalnum() or i == ' ':
            newStr += i
    return newStr


if __name__ == '__main__':
    app.run(debug=True, port = 1111)
conn.close()