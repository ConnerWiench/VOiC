from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import time
import os

DOCUMENT_PATH = "../case_documents"
COURT_ROLES = ["Other", "Lawyer", "Clerk", "Judge"]

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

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html',title='Join VOiC', roles=COURT_ROLES)

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
                            f"VALUES ('{_username}', '{_first}', '{_last}', '{_level}', "\
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
            cursor.execute("SELECT c.case_number, c.case_charge, c.case_time_created, "\
                            "u.user_first, u.user_last, c.case_released\n"\
                            "FROM court_case AS c\n"
                            "LEFT JOIN junction_case_user AS j ON j.junction_role = 'Judge' AND "\
                            "c.case_number = j.junction_case\n"\
                            "INNER JOIN court_user AS u ON j.junction_user = u.user_name;")
                # Keeping both for now to test later
            # cursor.execute("SELECT c.case_number, c.case_charge, c.case_time_created, "\
            #                 "u.user_first, u.user_last, c.case_released\n"\
            #                 "FROM junction_case_user AS j\n"\
            #                 "INNER JOIN court_case AS c ON j.junction_case = c.case_number\n"\
            #                 "INNER JOIN court_user AS u ON j.junction_user = u.user_name\n"\
            #                 "WHERE j.junction_role = 'Judge';")
        else:
            cursor.execute("SELECT case_number, case_document, case_time_created, "\
                            "u.user_first, u.user_last, case_released\n"\
                            "FROM court_case\n"
                            "INNER JOIN junction_case-user AS j ON j.role='Judge' AND "\
                            "court_case.number=j.case\n"\
                            "INNER JOIN court_user AS u ON j.user=u.name;")
                            #Put Where statement to check the fact blob
        cases = cursor.fetchmany(size=25)
        
    # Get user level to determine which cards should have edit button.
    currentUser = session.get('user')

    return render_template('case_list.html', cases=cases, user=currentUser)

@app.route("/api/case_list/download", methods=["POST"])
def case_list_api_download():
    docTitle = request.form["docName"]

    with conn.cursor() as cursor:
        cursor.execute("SELECT docs_path\n"\
                        "FROM court_docs\n"\
                        f"WHERE docs_title = '{docTitle}';")
        docPath = cursor.fetchone()

    try:
        return (send_file(f"{docPath}", attachment_filename=f"{docTitle}.txt"))
    except Exception as e:
        print(f"Error: {e}\nCancelling...")
        return redirect("/case_list")

@app.route("/case_create")
def case_create():
    user = session.get('user')
    if user is None:
        print("Redirecting...")
        return redirect('/log_in')
    
    # Pulls user level and checks if user is allowed to proceed.
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{user}';")
        level = cursor.fetchone()[0]
    if level != "Judge" and level != "Clerk":
        return redirect("/case_list")

    return render_template("case_create.html", roles=COURT_ROLES)

@app.route("/api/case_create", methods=["POST"])
def api_case_create():
    _case_id = convert_to_alpnum(request.form["form_id"])
    _case_charge = convert_to_alpnum(request.form["form_charge"])
    _case_verdict = convert_to_alpnum(request.form["form_verdict"])
    _case_user_created = session.get("user")
    _case_level = request.form["form_level"]
    _case_time_created = time.strftime('%Y-%m-%d %H:%M:%S')

    # Users the session saved username to get the user's access level.
    if not (_case_id and _case_charge and _case_verdict \
            and _case_user_created and _case_level):
        print("All Fields need to be filled")
        # Add Flash Error Statement Here
        return redirect('/case_create')

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_case_user_created}';")
        userLevel = cursor.fetchone()[0]
    if userLevel != "Judge" or userLevel != "Clerk":
        print("An Access Level Error has Occurred")
        # Add Flash Error Here
        return redirect('/case_create')

    # Attempts to add case with attached document
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_case(case_number, case_charge, "\
                            "case_user_created, case_verdict, "\
                            "case_time_created, case_level_required)\n"\
                            f"VALUES ({_case_id}, '{_case_charge}', '{_case_user_created}', "\
                            f"'{_case_verdict}', '{_case_time_created}', '{_case_level}');")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        # Add Flash Error Window
        return  redirect("/case_create")
    
    # Commit new case to database and send user to case edit page
    os.mkdir(f"{DOCUMENT_PATH}/{_case_id}")
    conn.commit()
    return redirect("/case_list") # Redirect to case edit page in furture


# ----- Normal Functions ----- (Move to different file eventually)

def convert_to_alpnum(oldStr):
    newStr = ""
    for i in oldStr:
        if i.isalnum() or i == ' ':
            newStr += i
    return newStr


# ----- Run setup and then run -----

if __name__ == '__main__':
    if not os.path.exists(f"{DOCUMENT_PATH}"):
        os.mkdir(f"{DOCUMENT_PATH}")
        
    app.run(debug=True, port = 1111)
conn.close()