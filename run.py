#!voic_venv/bin/python3
from flask import Flask
from frontend.routes import *

import dotenv

if __name__ == '__main__':
    dotenv.load_dotenv()
    app.run(debug=True, port=3453)