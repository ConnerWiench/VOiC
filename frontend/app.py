from flask import Flask, render_template, request, redirect, session
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import time

app = Flask(__name__)

conn = mysql.connector.connect(
    host = "localhost",
    user = "voic",
    password = "raspberry",
    database = "mydb",
)

@app.route('/')
def main():
    # if not session.get('user'):
        # print("Redirecting...")
        # return redirect('/register')
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route("/case_list")
def case_list(facts = None):

    with conn.cursor() as cursor:
        if facts == None:
            cursor.execute("SELECT case_number, case_document, case_time_created\
                            FROM court_case;")
        else:
            cursor.execute("SELECT case_number, case_document, case_time_created\
                            FROM court_case;")
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
    _case_id = request.form["form_id"]
    _case_charge = request.form["form_charge"]
    _case_user_created = session.get("user")
    _case_time_created = time.ctime()
    _case_document = request.form["form_document"]

    with conn.cursor() as cursor:
        cursor.execute(f"SELECT user_level\
                        FROM court_user\
                        WHERE user_name == {_case_user_created};")
        _case_level_required = cursor.fetchone()

    


if __name__ == '__main__':
    app.run(debug=True, port = 1111)
    conn.close()