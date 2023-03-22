from flask import Flask, render_template, request, redirect, session, flash
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import time

DOCUMENT_PATH = "../case_documents/"

app = Flask(__name__)
app.secret_key = b"This is a super secret key"

conn = mysql.connector.connect(
    host = "localhost",
    user = "voic",
    password = "raspberry",
    database = "voic_db",
)

# ----- Flask Functions -----

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    print("API CALLED")
    _username = request.form['signEmail']
    _first = request.form['signFirst']
    _last = request.form['signLast']
    _level = request.form['signLevel']
    _password = request.form['signPsk']
    _conPassword = request.form['signConPsk']
    _phone = request.form['signPhone']
    _question = request.form['signQuestion']
    _answer = request.form['signAnswer']
    _created = time.strftime('%Y-%m-%d %H:%M:%S')

    # Validate Values
    if not (_username and _first and _last and _level and _password \
            and _conPassword and _phone and _question and _answer):
        print("All fields need to be filled")
        # Add Flash Error Here
        return redirect('/register')
    elif _password != _conPassword:
        print("Passwords must Match")
        # Add Flash Error Here
        return redirect('/register')

    # Hashes the password for proper security
    _hashed_password = generate_password_hash(_password)

    print("INSERT INTO court_user(user_name, user_first, user_last, "\
            "user_level, user_created, user_password, user_phone, "\
            "user_question, user_answer)\n"\
            f"VALUES ('{_username}', '{_first}', '{_last}', {_level}, "\
            f"'{_created}', '{_hashed_password}', '{_phone}', "\
            f"'{_question}', '{_answer}');")
    # Attempts to add user into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_user(user_name, user_first, user_last, "\
                            "user_level, user_created, user_password, user_phone, "\
                            "user_question, user_answer)\n"\
                            f"VALUES ('{_username}', '{_first}', '{_last}', {_level}, "\
                            f"'{_created}', '{_hashed_password}', '{_phone}', "\
                            f"'{_question}', '{_answer}');")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        return redirect('/register')

    return redirect('/register') # Some sort of redirect to login page

@app.route('/api/login', methods=['POST'])
def api_login():
    _username = request.form['loginEmail']
    _password = request.form['loginPassword']

    if not (_username and _password):
        print("All fields need to be filled")
        # Add Flash Error Statement
        return redirect('/register')
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_name, user_password\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_username}'")
        data = cursor.fetchone()

    if data is None:
        print("Incorrect Email or Password")
        # Add Flash Error Statement
        return redirect('/register')
    
    if check_password_hash(str(data[1]), _password):
        print("Successful Login!")
        session['user'] = data[0]
        return redirect('/case_list')
    else:
        print("Incorrect Email or Password")
        # Add Flash Error Statement
        return redirect('/register')


@app.route("/case_list")
def case_list(facts = None):
    if not session.get('user'):
        print("Redirecting...")
        return redirect('/register')

    with conn.cursor() as cursor:
        if facts == None:
            cursor.execute("SELECT case_number, case_document, case_time_created\n"\
                            "FROM court_case;")
        else:
            cursor.execute("SELECT case_number, case_document, case_time_created\n"\
                            "FROM court_case;")
                            #Put Where statement to check the fact blob
        cases = cursor.fetchall()
        
    return render_template('case_list.html', cases=cases)

@app.route("/case_create")
def case_create():
    if not session.get('user'):
        print("Redirecting...")
        return redirect('/register')
    
    # Pulls user level and sets the page to only show user eligible levels
    user = session.get('user')
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{user}';")
        level = cursor.fetchone()
    # If there is no user level for some reason, set to 0
    if level[0] is None:
        level[0] = 0

    return render_template("case_create.html", level=level[0])

@app.route("/api/case_create", methods=["POST"])
def api_case_create():
    _case_id = convert_to_alpnum(request.form["form_id"])
    _case_charge = convert_to_alpnum(request.form["form_charge"])
    _case_verdict = convert_to_alpnum(request.form["form_verdict"])
    _case_user_created = session.get("user")
    _case_level = session.get("form_level")
    _case_time_created = time.strftime('%Y-%m-%d %H:%M:%S')
    _case_document = convert_to_alpnum(request.form["form_document"])
    _case_file_path = f"{DOCUMENT_PATH}{_case_document}"

    # Debug Line
    print(f"Information: {_case_id}, {_case_charge}, {_case_verdict}, {_case_user_created}, {_case_time_created}, {_case_file_path}")

    # Users the session saved username to get the user's access level.
    if not (_case_id and _case_charge and _case_verdict \
            and _case_document and _case_user_created and _case_level):
        print("All Fields need to be filled")
        # Add Flash Error Statement Here
        return redirect('/case_create')

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_case_user_created}';")
        userLevelMax = cursor.fetchone()
    if _case_level > userLevelMax or _case_level < 0:
        print("An Access Level Error has Occurred")
        # Add Flash Error Here
        return redirect('/case_create')
    
    # Attempts to add document into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_docs(docs_title, docs_path)"\
                        f"VALUES ({_case_document}, {_case_file_path})")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        # Add Flash Error Window
        return  redirect("/case_create")

    # Attempts to add case with attached document
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_case(case_number, case_charge, "\
                            "case_user_created, case_document, case_verdict, "\
                            "case_time_created, case_level_required)\n"\
                            f"VALUES ({_case_id}, '{_case_charge}', '{_case_user_created}', "\
                            f"'{_case_document}', '{_case_verdict}', '{_case_time_created}'"\
                            f"{_case_level});")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        # Add Flash Error Window
        return  redirect("/case_create")
    
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