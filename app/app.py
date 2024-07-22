from flask import (Flask, 
                   render_template, 
                   send_from_directory, 
                   abort, 
                   redirect, url_for,
                   request, session,)
from flask_behind_proxy import FlaskBehindProxy
import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from func.parse import get_summary_from_upload

SUMMARY_TEXT_DEFAULT = "Sorry, we couldn't find the summary text. Try uploading your file again."

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    app.config['SECRET_KEY'] = 'a5783ee1abf428d9a22445b69e1c1ab4'

# configure upload folder location
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'func/pdf_placeholder')

@app.route('/', methods=['GET'])
def home():
    session['summary_text'] = SUMMARY_TEXT_DEFAULT
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and file.filename.endswith('.pdf'):
        # put temp.pdf in /func/pdf_placeholder
        filename = file.filename   # TODO: change to be unique for the user & time
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print('FILE UPLOADED SUCCESSFULLY: ', file_path)  # success message

        # call get_summary (TODO: add functionality to get audio)
        new_filepath = 'func/pdf_holder/' + filename
        summary_text = get_summary_from_upload(new_filepath)
        session['summary_text'] = summary_text
        
        # Delete the file after processing
        os.remove(file_path)
        print('FILE DELETED SUCCESSFULLY: ', file_path)  # success message
        
        # send text to /output
        return redirect(url_for('output'))
    else:
        return "Invalid file type. Only PDFs are allowed."

@app.route('/library', methods=['GET'])
def library():
    return render_template('library.html')

@app.route('/output', methods=['GET', 'POST'])
def output():
    t = session.get('summary_text')
    session['summary_text'] = SUMMARY_TEXT_DEFAULT
    return render_template('output.html', summary_text = t)


@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory('static/recordings', filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")