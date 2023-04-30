#!../voic_venv/bin/python3

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

from flask_ckeditor import CKEditor
from flask_ckeditor.fields import CKEditorField


DOCUMENT_PATH = "../case_documents"
COURT_ROLES = ["Other", "Lawyer", "Clerk", "Judge"]
CASE_ARTICLES = ["Generial Provisions",
                 "Jurisdiction",
                 "Enforcement",
                 "Miscellaneous Provisions"]

app = Flask(__name__)
ckeditor = CKEditor(app)

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
    
class MyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

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
        flash("All fields need to be filled")
        return redirect('/sign_up')
    elif _password != _conPassword:
        print("Passwords must Match")
        # Add Flash Error Here
        flash("Passwords must Match")
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
        flash('Successful Login!', 'success')
        print('Successful Login!')
        return redirect('/case_list')
    else:
        flash('Incorrect Email or Password')
        print('Incorrect Email or Password')
        return redirect('/log_in')


@app.route('/api/log_out')
def api_log_out():
    session.pop('user')
    flash('Logged Out', 'success')
    return redirect('/')


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
                            "LEFT OUTER JOIN junction_case_user AS j ON j.junction_role = 'Judge' AND "\
                            "c.case_number = j.junction_case\n"\
                            "LEFT JOIN court_user AS u ON j.junction_user = u.user_name\n"\
                            "WHERE c.case_released<>0;")
        else:
            cursor.execute("SELECT c.case_number, c.case_charge, c.case_time_created, "\
                            "u.user_first, u.user_last, c.case_released\n"\
                            "FROM court_case AS c\n"
                            "LEFT OUTER JOIN junction_case_user AS j ON j.junction_role = 'Judge' AND "\
                            "c.case_number = j.junction_case\n"\
                            "LEFT JOIN court_user AS u ON j.junction_user = u.user_name\n"\
                            "WHERE c.case_released<>0;")
                            #Put Where statement to check the fact blob
        cases = cursor.fetchmany(size=25)

        cursor.execute("SELECT c.case_number, c.case_charge, c.case_time_created, "\
                        "u.user_first, u.user_last, c.case_released\n"\
                        "FROM court_case AS c\n"
                        f"INNER JOIN junction_case_user AS j ON j.junction_user = '{session.get('user')}' AND "\
                        "c.case_number = j.junction_case\n"\
                        "LEFT JOIN court_user AS u ON j.junction_user = u.user_name\n"\
                        "WHERE c.case_released=0;")
        
        mycases = cursor.fetchmany(size=25)
        
    # Get user level to determine which cards should have edit button.
    currentUser = session.get('user')

    return render_template('case_list.html', mycases=mycases, cases=cases, user=currentUser, title='Case List')

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
    form = MyForm()
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
        flash('Permission Denied', 'danger')
        return redirect("/case_list")

    return render_template("case_create.html", title='Create Case', roles=COURT_ROLES, articles=CASE_ARTICLES,form=form)

@app.route("/api/case_create", methods=["POST"])
def api_case_create():
    _case_id = convert_to_alpnum(request.form["case_number"])
    _case_charge = convert_to_alpnum(request.form["case_charge"])
    _case_article = convert_to_alpnum(request.form["case_article"])
    _case_preceed = convert_to_alpnum(request.form["case_preceed_number"])
    _case_users = request.form.getlist("case_users[]")
    _case_roles = request.form.getlist("case_roles[]")
    _case_user_created = session.get("user")
    _case_time_created = time.strftime('%Y-%m-%d %H:%M:%S')

    # Users the session saved username to get the user's access level.
    if not (_case_id and _case_charge and _case_article \
            and _case_user_created):
        print("All Fields need to be filled")
        # Add Flash Error Statement Here
        flash("All fields need to be filled.", "danger")
        return redirect('/case_create')
    
    # If _case_preceed is empty, change to NULL so mysql knows its null
    if _case_preceed == '': _case_preceed = 'NULL'

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_level\n"\
                        "FROM court_user\n"\
                        f"WHERE user_name = '{_case_user_created}';")
        userLevel = cursor.fetchone()[0]
    if userLevel != "Judge" and userLevel != "Clerk":
        print(f"An Access Level Error has Occurred: {userLevel}")
        # Add Flash Error Here
        flash('User does not have access to create.', 'danger')
        return redirect('/case_create')

    #Checks if users exist
    with conn.cursor() as cursor:
        for user in _case_users:
            cursor.execute("SELECT user_name\n"\
                            "FROM court_user\n"\
                            f"WHERE user_name = '{user}';")
            if cursor.fetchone() is None:
                print("Invalid user(s)")
                flash("Invalild user(s) in case.", "danger")
                return redirect("/case_create")

    # Attempts to add case
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO court_case(case_number, case_charge, "\
                            "case_article, case_time_created, case_preceed_number)\n"\
                            f"VALUES ({_case_id}, '{_case_charge}', "\
                            f"'{_case_article}', '{_case_time_created}', {_case_preceed});")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        if 'Duplicate' in str(e):
            flash('Case already exists', 'danger')
        else:
            flash('An error has occurred', 'danger')
        return redirect("/case_create")
    
    # Attaches users to case using junction table
    try:
        with conn.cursor() as cursor:
            for user,role in zip(_case_users, _case_roles):
                cursor.execute("INSERT INTO junction_case_user(junction_user, "\
                                "junction_role, junction_case)\n"\
                                f"VALUES ('{user}', '{role}', {_case_id});")
    except Exception as e:
        print(f"Error Found: {e}\nCancelling...")
        # Add Flash Error Window
        flash("An error has occured.")
        return redirect("/case_create")
    # Commit new case to database and send user to case edit page
    os.mkdir(f"{DOCUMENT_PATH}/{_case_id}")
    conn.commit()
    return redirect(f'/case_view/{_case_id}') # Redirect to case edit page in furture


@app.route('/case_view/<case_id>')
def case_view(case_id):
    # ----- Gate Conditions -----
    user = session.get('user')
    if user is None:
        print("Redirecting...")
        return redirect('/log_in')
    
    # Is the case existing and released or should this user have access
    with conn.cursor() as cursor:
        cursor.execute("SELECT case_released\n"\
                        "FROM court_case\n"\
                        f"WHERE case_number='{case_id}';")
        released = cursor.fetchone()
        if released:
            released = released[0]
        else:
            flash('Case does not exists', 'danger')
            return redirect('/case_list')

        cursor.execute("SELECT junction_role\n"\
                        "FROM junction_case_user\n"\
                        f"WHERE junction_case={case_id}\n"\
                        f"AND junction_user='{session.get('user')}';")
        userRole = cursor.fetchone()
        if userRole is not None:
            userRole = userRole[0]
    
    if released == 0 and userRole is None:
        print("User does not have permission for this case.")
        flash("Case Access Denied", 'danger')
        return redirect('/case_list')
    # ----- End Gate -----

    with conn.cursor(buffered=True) as cursor:
        cursor.execute("SELECT c.case_number, c.case_charge, c.case_article, c.case_verdict, "\
                        "c.case_time_created, c.case_preceed_number, t.case_number, c.case_released\n"\
                        "FROM court_case AS c\n"\
                        f"LEFT JOIN court_case AS t ON c.case_number=t.case_preceed_number\n"\
                        f"WHERE c.case_number={case_id};")
        case = cursor.fetchone()

        cursor.execute("SELECT junction_user, junction_role\n"\
                        "FROM junction_case_user\n"\
                        f"WHERE junction_case={case_id};")
        people = cursor.fetchall()

        cursor.execute("SELECT docs_title, docs_type, docs_approved\n"\
                        "FROM court_docs\n"
                        f"WHERE docs_case={case_id};")
        docs = cursor.fetchall()

    return render_template('case_view.html', case=case, people=people, docs=docs, role=userRole, roles=COURT_ROLES)

@app.route('/case_view/<case_id>/remove_user', methods=["POST"])
def case_view_remove_user(case_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT junction_role\n"\
                        "FROM junction_case_user\n"\
                        f"WHERE junction_case={case_id}\n"\
                        f"AND junction_user='{session.get('user')}';")
        userRole = cursor.fetchone()[0]
    
    if not ((userRole == "Judge") or (userRole == "Clerk")):
        print("User does not have permission to do this.")
        return redirect(f'/case_view/{case_id}')

    rem_user = request.form["rem_user"]

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM junction_case_user\n"\
                            f"WHERE junction_case={case_id}\n"\
                            f"AND junction_user='{rem_user}';")
    except Exception as e:
        print(f"Error: {e}\nCancelling...")
        return redirect(f'/case_view/{case_id}')
    
    conn.commit()
    flash('User removed', 'success')
    return redirect(f'/case_view/{case_id}')
        
@app.route('/case_view/<case_id>/add_user', methods=["POST"])
def case_view_add_user(case_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT junction_role\n"\
                        "FROM junction_case_user\n"\
                        f"WHERE junction_case={case_id}\n"\
                        f"AND junction_user='{session.get('user')}';")
        userRole = cursor.fetchone()[0]
    
    if not ((userRole == "Judge") or (userRole == "Clerk")):
        print("User does not have permission to do this.")
        flash('Permission Denied', 'danger')
        return redirect(f'/case_view/{case_id}')

    new_user = request.form["new_user"]
    new_role = request.form["new_role"]

    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO junction_case_user(junction_user, "\
                            "junction_role, junction_case)\n"\
                            f"VALUES ('{new_user}', '{new_role}', {case_id});")
    except Exception as e:
        print(f"Error: {e}\nCancelling...")
        if 'Duplicate' in str(e):
            flash('User already exist', 'danger')
        else:
            flash('An error has occured', 'danger')

    conn.commit()
    flash('User added', 'success')
    return redirect(f'/case_view/{case_id}')

@app.route('/case_view/<case_id>/verdict', methods=['POST'])
def case_view_change_verdict(case_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT junction_role\n"\
                        "FROM junction_case_user\n"\
                        f"WHERE junction_case={case_id}\n"\
                        f"AND junction_user='{session.get('user')}';")
        userRole = cursor.fetchone()[0]
    
    if not userRole == "Judge":
        print("User does not have permission to do this.")
        flash('Permission Denied', 'danger')
        return redirect(f'/case_view/{case_id}')

    new_release = request.form["new_release"]
    new_verdict = request.form["new_verdict"]

    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE court_case\n"\
                            f"SET case_released={new_release}, case_verdict='{new_verdict}'\n"\
                            f"WHERE case_number={case_id};")
    except Exception as e:
        print(f"Error: {e}\nCancelling...")
        flash('An error has occured', 'danger')

    conn.commit()
    flash('Status Updated', 'success')
    return redirect(f'/case_view/{case_id}')

@app.route('/profile')
def profile():
    # get user_name from session object
    user_name = session.get('user')
    print(user_name)

    with conn.cursor() as cursor:
        cursor.execute("SELECT user_name,user_first,user_last,user_level, user_phone, user_question, user_answer, user_address1, user_address2, user_postcode FROM court_user WHERE user_name = %s", (user_name,))
        data = cursor.fetchone()
        print(data)
    return render_template('profile.html',title= 'Profile' ,user_name=data[0], user_first=data[1], user_last=data[2], user_level=data[3], user_phone=data[4], user_question=data[5], user_answer=data[6],address1=data[7], address2=data[8], postcode=data[9])

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_name = session.get('user')
    token = session.get('token')
    if 'user_name' in request.form:
        user_name = request.form['user_name']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    phone_number = request.form['phone_number']
    question = request.form['question']
    answer = request.form['answer']
    address1=request.form['address1']
    address2=request.form['address2']
    postcode=request.form['postcode']
    password = None
    if "password" in request.form:
        password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    token1 = str(uuid.uuid4())
    
    if password != confirm_password:
        flash("Password do not match", 'danger')
    password = generate_password_hash(password)

    print(first_name)
    print(address1)
    print(password)
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM court_user WHERE user_token =%s", [token])
        data = cursor.fetchone()
        
    if data:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE court_user SET user_token=%s, user_password=%s WHERE user_token=%s", [token1,password, token])
        conn.commit()
        flash("Your password successfully updated", 'success')
    else:
        flash("Your token is invalid",'danger')  
    
    with conn.cursor() as cursor:
        cursor.execute("UPDATE court_user SET user_name=%s, user_first=%s, user_last=%s, user_phone=%s,user_question=%s, user_answer=%s, user_address1=%s, user_address2=%s, user_postcode=%s WHERE user_name=%s", (user_name,first_name, last_name, phone_number,question, answer,address1, address2, postcode, user_name))
        conn.commit()

    flash('Profile Updated!', 'success')
    return redirect(url_for('profile'))

# ----- Normal Functions ----- (Move to different file eventually)

def convert_to_alpnum(oldStr):
    newStr = ""
    for i in oldStr:
        if i.isalnum() or i == ' ':
            newStr += i
    return newStr

@app.route('/document')
def document():

    return render_template('document.html',title= 'Document')


if __name__ == '__main__':
    if not os.path.exists(f"{DOCUMENT_PATH}"):
        os.mkdir(f"{DOCUMENT_PATH}")
        
    app.run(debug=True, port = 1211)
conn.close()