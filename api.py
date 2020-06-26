import sys
import os
from datetime import datetime
from flask import Flask
import psycopg2

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello!"


@app.route('/time')
def path():
    return str(datetime.now())


@app.route("/connect")
def postgres_test():
    try:
        conn_str = os.environ.get("PYTRACK_DB")
        conn = psycopg2.connect(conn_str + " connect_timeout=1")
        conn.close()
        return 'Connected.'
    except:
        return 'Connection failed.'
