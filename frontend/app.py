from flask import Flask, render_template, request, redirect, session, flash, url_for
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
    password = "Raspberry@111",
    database = "voic_db",
)

# ----- Flask Functions -----

@app.route('/')
def main():
    return render_template('index.html',title='VOiC - Virtual Office in the Cloud')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html',title='Join VOiC')

@app.route('/api/sign_up', methods=['POST'])
def api_sign_up():
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
        return redirect('/sign_up')
    elif _password != _conPassword:
        print("Passwords must Match")
        # Add Flash Error Here
        return redirect('/sign_up')

    # Hashes the password for proper security
    _hashed_password = generate_password_hash(_password)

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
        return redirect('/sign_up')
    
    # Commit changes to the databse and send user to login on successful sign up.
    conn.commit()
    return redirect('/log_in') # Some sort of redirect to login page

@app.route('/log_in')
def log_in():
    return render_template('log_in.html',title='Log in')

@app.route('/api/log_in', methods=['POST'])
def api_log_in():
    _username = request.form['loginEmail']
    _password = request.form['loginPassword']

    if not (_username and _password):
        print("All fields need to be filled")
        # Add Flash Error Statement
        return redirect('/log_in')
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_name, user_password\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_username}'")
        data = cursor.fetchone()

    if data is None:
        print("Incorrect Email or Password")
        # Add Flash Error Statement
        return redirect('/log_in')
    
    if check_password_hash(str(data[1]), _password):
        print("Successful Login!")
        session['user'] = data[0]
        return redirect('/case_list')
    else:
        print("Incorrect Email or Password")
        # Add Flash Error Statement
        return redirect('/log_in')

@app.route('/password')
def password():
    return render_template('password.html',title='Forgotten Password')


@app.route("/case_list")
def case_list(facts = None):
    if not session.get('user'):
        print("Redirecting...")
        return redirect('/log_in')

    # Pull up to 25 case information arrays to list
    with conn.cursor() as cursor:
        if facts == None:
            cursor.execute("SELECT case_number, case_document, case_time_created, "\
                            "u.user_first, u.user_last, case_level_required\n"\
                            "FROM court_case\n"
                            "INNER JOIN court_user AS u ON court_case.case_user_created=u.user_name;")
        else:
            cursor.execute("SELECT case_number, case_document, case_time_created, "\
                            "u.user_first, u.user_last, case_level_required\n"\
                            "FROM court_case\n"
                            "INNER JOIN court_user AS u ON court_case.case_user_created=u.user_name;")
                            #Put Where statement to check the fact blob
        cases = cursor.fetchmany(size=25)
        
    # Get user level to determine which cards should have edit button.
    currentUser = session.get('user')
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{currentUser}';")
        userLevel = cursor.fetchone()[0]
    # If nothing else, put user at minimum level.
    if userLevel is None:
        userLevel = 0

    return render_template('case_list.html', cases=cases, userLevel=userLevel)

@app.route("/case_create")
def case_create():
    if not session.get('user'):
        print("Redirecting...")
        return redirect('/log_in')
    
    # Pulls user level and sets the page to only show user eligible levels
    user = session.get('user')
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{user}';")
        level = cursor.fetchone()[0]

    # If there is no user level for some reason, set to 0
    if level is None:
        level = 0

    return render_template("case_create.html", level=level)

@app.route("/api/case_create", methods=["POST"])
def api_case_create():
    _case_id = convert_to_alpnum(request.form["form_id"])
    _case_charge = convert_to_alpnum(request.form["form_charge"])
    _case_verdict = convert_to_alpnum(request.form["form_verdict"])
    _case_user_created = session.get("user")
    _case_level = int(request.form["form_level"])
    _case_time_created = time.strftime('%Y-%m-%d %H:%M:%S')
    _case_document = convert_to_alpnum(request.form["form_document"])
    _case_file_path = f"{DOCUMENT_PATH}{_case_document}"

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
        userLevelMax = cursor.fetchone()[0]
    if _case_level > userLevelMax or _case_level < 0:
        print("An Access Level Error has Occurred")
        # Add Flash Error Here
        return redirect('/case_create')
    
    # Attempts to add document into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_docs(docs_title, docs_path)\n"\
                            f"VALUES ('{_case_document}', '{_case_file_path}');")
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
                            f"'{_case_document}', '{_case_verdict}', '{_case_time_created}', "\
                            f"{_case_level});")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        # Add Flash Error Window
        return  redirect("/case_create")
    
    # Commit new caze to database and send user to case edit page
    conn.commit()
    return redirect("/case_list") # Redirect to case edit page in furture


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