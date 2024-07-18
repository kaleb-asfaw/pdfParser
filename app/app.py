from flask import Flask, render_template, url_for, flash, redirect, request, session, jsonify
from flask_behind_proxy import FlaskBehindProxy
import sys,os

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    app.config['SECRET_KEY']('a5783ee1abf428d9a22445b69e1c1ab4')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')