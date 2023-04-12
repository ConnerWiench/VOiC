from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import time
import os
import uuid
import secrets
from dotenv import load_dotenv
import bcrypt
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

DOCUMENT_PATH = "../case_documents"
COURT_ROLES = ["Other", "Lawyer", "Clerk", "Judge"]

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

app.secret_key = os.environ.get('SECRET_KEY').encode('utf-8')  #encode('utf-8') method converts the string value to bytes using the UTF-8 encoding.

conn = mysql.connector.connect(
    host = "localhost",
    user = "voic",
    password = "Raspberry@111",
    database = "voic_db",
)

# configure mail settings
app.config['MAIL_SERVER'] = 'smtp.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# reCAPTCHA configuration
app.config["RECAPTCHA_PUBLIC_KEY"] ="6LebRGIlAAAAAE7dmHl-qy8vaI9_VT0xplNbyzJK"
app.config["RECAPTCHA_PRIVATE_KEY"] ="6LebRGIlAAAAAL8wypO04j9vgw5EY9tEmj02H7Na"

recaptcha=RecaptchaField()

class RecaptchaFunction(FlaskForm):
    recaptcha = RecaptchaField()

# ----- Flask Functions -----
@app.route('/')
def main():
    return render_template('index.html',title='VOiC - Virtual Office in the Cloud')

@app.route('/sign_up')
def sign_up():
    form = RecaptchaFunction()
    return render_template('sign_up.html',title='Join VOiC', roles=COURT_ROLES, form=form)

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

    # Generate a unique token
    token = secrets.token_hex(16)

    # Attempts to add user into database
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_user(user_name, user_first, user_last, "\
                            "user_level, user_created, user_password, user_phone, "\
                            "user_question, user_answer, user_token)\n"\
                            f"VALUES ('{_username}', '{_first}', '{_last}', '{_level}', "\
                            f"'{_created}', '{_hashed_password}', '{_phone}', "\
                            f"'{_question}', '{_answer}', '{token}');")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        return redirect('/sign_up')
    
    # Commit changes to the database and send user to login on successful sign up.
    conn.commit()
    return redirect('/log_in') # Some sort of redirect to login page

@app.route('/log_in')
def log_in():
    form = RecaptchaFunction()
    return render_template('log_in.html', title='Log in', form=form)

@app.route('/api/log_in', methods=['POST'])
def api_log_in():
    _username = request.form['loginEmail']
    _password = request.form['loginPassword']

    if not (_username and _password):
        flash('All fields need to be filled')
        print('All fields need to be filled')
        return redirect('/log_in')
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_name, user_password\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_username}'")
        data = cursor.fetchone()

    if data is None:
        flash('Incorrect Email or Password')
        print('Incorrect Email or Password')
        return redirect('/log_in')
    
    if check_password_hash(str(data[1]), _password):
        session['user'] = data[0]
        flash('Successful Login!')
        print('Successful Login!')
        return redirect('/profile')
    else:
        flash('Incorrect Email or Password')
        print('Incorrect Email or Password')
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

    return render_template('case_list.html', cases=cases, user=currentUser,title='Case List')

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

    return render_template("case_create.html",title='Create Case' ,roles=COURT_ROLES)

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

@app.route('/forgot',methods=["POST","GET"])
def forgot():
    if 'login' in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form["username"]
        token = str(uuid.uuid4())
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM court_user WHERE user_name =%s", [email])
            data = cursor.fetchone()
            
            msg = Message(subject='Forgot password requst',sender='niraulashashwot1990@outlook.com',recipients=[email])
            msg.body=render_template("sent.html",token=token, data=data)
            print("ready to email")
            mail.send(msg)
            print('mail sent')    
            cursor.execute("UPDATE court_user SET user_token=%s WHERE user_name=%s", [token, email])
            print('cursor.connection.commit()')
            conn.commit()
            cursor.close()
        
        flash("Email already sent to your email", 'success')
        return redirect('/log_in')
    
    else:
        flash("Email do not match",'danger')
            
    return render_template('forgot.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    if 'login' in session:
        return redirect('/')
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        token1 = str(uuid.uuid4())
        if password != confirm_password:
            flash("Password do not match", 'danger')
            return redirect('reset')
        password = generate_password_hash(password)
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM court_user WHERE user_token =%s", [token])
            data = cursor.fetchone()
        
        if data:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE court_user SET user_token=%s, user_password=%s WHERE user_token=%s", [token1,password, token])
            conn.commit()
            flash("Your password successfully updated", 'success')
            return redirect('/log_in')
        else:
            flash("Your token is invalid",'danger')
            return redirect('/')
    
    return render_template('reset.html')

@app.route('/profile')
def profile():
    # get user_name from session object
    user_name = session.get('user')
    print(user_name)

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_name,user_first,user_last,user_level, user_phone, user_question, user_answer FROM court_user WHERE user_name = %s", (user_name,))
        data = cursor.fetchone()
        print(data)
    return render_template('profile.html',title= 'Profile' ,user_name=data[0], user_first=data[1], user_last=data[2], user_level=data[3], user_phone=data[4], user_question=data[5], user_answer=data[6])

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_name = session.get('user')
    if 'user_name' in request.form:
        user_name = request.form['user_name']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    phone_number = request.form['phone_number']
    question = request.form['question']
    answer = request.form['answer']

    with conn.cursor() as cursor:
        cursor.execute("UPDATE court_user SET user_name=%s, user_first=%s, user_last=%s, user_phone=%s,user_question=%s, user_answer=%s WHERE user_name=%s", (user_name,first_name, last_name, phone_number,question, answer, user_name))
        conn.commit()

    return redirect(url_for('profile'))

if __name__ == '__main__':
    if not os.path.exists(f"{DOCUMENT_PATH}"):
        os.mkdir(f"{DOCUMENT_PATH}")
        
    app.run(debug=True, port = 4111)
conn.close()