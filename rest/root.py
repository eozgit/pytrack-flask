import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(filename='../pytrack.log', level=logging.DEBUG)
load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PYTRACK_DB')
db = SQLAlchemy(app)
