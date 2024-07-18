from flask import Flask, render_template, url_for, flash, redirect, request, session, jsonify
from flask_behind_proxy import FlaskBehindProxy
import sys,os

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    raise EnvironmentError("Config key for Flask app was not set")

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')