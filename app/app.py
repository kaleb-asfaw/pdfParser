from flask import Flask, render_template, send_from_directory, abort
from flask_behind_proxy import FlaskBehindProxy
import sys,os

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    app.config['SECRET_KEY'] = 'a5783ee1abf428d9a22445b69e1c1ab4'

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/library', methods=['GET'])
def library():
    return render_template('library.html')

@app.route('/output', methods=['GET'])
def output():
    return render_template('output.html')


@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory('static/recordings', filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('pdfhome.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")