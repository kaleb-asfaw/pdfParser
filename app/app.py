from flask import (Flask, 
                   render_template, 
                   send_from_directory, 
                   abort, 
                   redirect, url_for,
                   request, session,)
from flask_behind_proxy import FlaskBehindProxy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sys,os
import base64
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from func.parse import get_summary_from_upload
from func.synthesize import make_mp3
import bcrypt
from app.login_db import find_user_by_email, create_user, get_db_connection

SUMMARY_TEXT_DEFAULT = "Sorry, we couldn't find the summary text. Try uploading your file again."



app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    app.config['SECRET_KEY'] = 'a5783ee1abf428d9a22445b69e1c1ab4'

# configure upload folder location
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'func/pdf')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email):
        self.id = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None
    return User(user['email'])
    

@app.route('/', methods=['GET'])
def home():
    session['summary_text'] = SUMMARY_TEXT_DEFAULT
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        user = find_user_by_email(email)
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            user_obj = User(email)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            error_message = 'Invalid credentials. Please try again.'
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        confirm_password = request.form['confirm-password'].encode('utf-8')

        if password != confirm_password:
            return 'Passwords do not match', 400

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        create_user(email, hashed_password)
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and file.filename.endswith('.pdf'):
        # put temp.pdf in /func/pdf_placeholder
        filename = 'temp.pdf'   # TODO: change to be unique for the user & time
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print('FILE UPLOADED SUCCESSFULLY: ', file_path)  # success message

        # call get_summary (TODO: add functionality to get audio)
        rootpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        new_filepath = rootpath + '/func/pdf/' + filename
        try:
            summary_text = get_summary_from_upload(new_filepath)
            # Generate MP3 audio content
            mp3_data = make_mp3(summary_text)
            # Encode MP3 data in base64 and store in session
            session['summary_audio'] = base64.b64encode(mp3_data).decode('utf-8')
            session['summary_text'] = summary_text
            
        except ValueError as e:
            print('ERROR with getting summary text for upload: ', e)
        
        # Delete the file after processing
        os.remove(file_path)
        print('FILE DELETED SUCCESSFULLY: ', file_path)  # success message
        
        # send text to /output
        return redirect(url_for('output'))
    else:
        return "Invalid file type. Only PDFs are allowed."

@app.route('/library', methods=['GET'])
@login_required
def library():
    return render_template('library.html')

@app.route('/output', methods=['GET', 'POST'])
@login_required
def output():
    t = session.get('summary_text')
    a = session.get('summary_audio', '')
    if a:
        a = base64.b64decode(a)
    session['summary_text'] = SUMMARY_TEXT_DEFAULT
    return render_template('output.html', summary_text = t, summary_audio = a)


@app.route('/download/<filename>')
@login_required
def download(filename):
    try:
        return send_from_directory('static/recordings', filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")