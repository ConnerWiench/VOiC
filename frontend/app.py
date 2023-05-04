import os  # import the os module to access environment variables
from flask import Flask  # import the Flask class
from dotenv import load_dotenv  # import the load_dotenv function from python-dotenv package
from flask_ckeditor import CKEditor  # import the CKEditor class
from flask_mail import Mail  # import the Mail class
from frontend import app  # import the app instance created in the frontend module

load_dotenv()  # load environment variables from .env file
ckeditor = CKEditor(app)  # initialize the CKEditor extension with the app instance

DOCUMENT_PATH = "../case_documents"  # set the document path
COURT_ROLES = ["Other", "Lawyer", "Clerk", "Judge"]  # set the court roles
CASE_ARTICLES = ["Generial Provisions",
                 "Jurisdiction",
                 "Enforcement",
                 "Miscellaneous Provisions"]  # set the case articles

app.secret_key = os.environ.get('SECRET_KEY').encode('utf-8')  # set the app secret key

# configure mail settings
app.config['MAIL_SERVER'] = 'smtp.outlook.com'  # set the mail server
app.config['MAIL_PORT'] = 587  # set the mail port
app.config['MAIL_USE_TLS'] = True  # set the mail use TLS to True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # set the mail username
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # set the mail password

mail = Mail(app)  # initialize the Mail extension with the app instance

# reCAPTCHA configuration
app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get('RECAPTCHA_PUBLIC_KEY')  # set the reCAPTCHA public key
app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get('RECAPTCHA_PRIVATE_KEY')  # set the reCAPTCHA private key
