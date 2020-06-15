#!flask/bin/python
import datetime
import json
from flask import Flask, Response
from helloworld.flaskrun import flaskrun

application = Flask(__name__)


@application.route('/api/time', methods=['GET'])
def time():
    response = Response(json.dumps({'Output': str(datetime.datetime.now())}), mimetype='application/json', status=200)
    return response


@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)


if __name__ == '__main__':
    flaskrun(application)
