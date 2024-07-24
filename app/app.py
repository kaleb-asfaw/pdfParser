from flask import (Flask, render_template, send_from_directory, abort, redirect, url_for, request, session)
from flask_behind_proxy import FlaskBehindProxy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sys, os, base64, time, markdown2
import git
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from func.parse import get_summary_from_upload
from func.synthesize import make_mp3
import bcrypt
from bs4 import BeautifulSoup
from app.login_db import find_user_by_email, create_user, get_db_connection

SUMMARY_TEXT_DEFAULT = "Sorry, we couldn't find the summary text. Try uploading your file again."

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
if not os.environ.get('FLASK_KEY'):
    app.config['SECRET_KEY'] = 'a5783ee1abf428d9a22445b69e1c1ab4'

# configure upload folder location
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'func/recordings')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None
    return User(user['id'], user['email'])

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
            user_obj = User(user['id'], email)
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
        
        user = find_user_by_email(email)
        if user:
            return 'User already exists', 400

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        user_id = create_user(email, hashed_password)
        user_obj = User(user_id, email)
        login_user(user_obj)
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user_email = current_user.email
    return render_template('dashboard.html', user_email=user_email)

@app.route('/upload', methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and file.filename.endswith('.pdf'):
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)
        
        filename = f'{int(time.time())}_{file.filename}'  # unique filename using timestamp
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        print('FILE UPLOADED SUCCESSFULLY: ', file_path)

        try:
            summary_text = get_summary_from_upload(file_path)
            # takes out markdown for text-to-speech
            html_str = markdown2.markdown(summary_text)
            soup = BeautifulSoup(html_str, 'html.parser')
            plain_text = soup.get_text()
            print(plain_text)
            mp3_data = make_mp3(plain_text)
            # Save MP3 file
            mp3_filename = f'{int(time.time())}.mp3'
            mp3_path = os.path.join(user_folder, mp3_filename)
            with open(mp3_path, 'wb') as mp3_file:
                mp3_file.write(mp3_data)
            
            # Save file paths to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_files (user_id, pdf_path, mp3_path, summary_text) VALUES (?, ?, ?, ?)",
                           (current_user.id, file_path, mp3_path, summary_text))
            conn.commit()
            conn.close()
            
        except ValueError as e:
            print('ERROR with getting summary text for upload: ', e)

        return redirect(url_for('output'))
    else:
        return "Invalid file type. Only PDFs are allowed."

@app.route('/library', methods=['GET'])
@login_required
def library():
    return render_template('library.html')

@app.route('/output', methods=['GET'])
@login_required
def output():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_files WHERE user_id = ? ORDER BY id DESC LIMIT 1", (current_user.id,))
    user_file = cursor.fetchone()
    conn.close()
    
    if user_file:
        summary_text = markdown2.markdown(user_file['summary_text'])
        audio_filename = os.path.basename(user_file['mp3_path'])
    else:
        summary_text =  markdown2.markdown(SUMMARY_TEXT_DEFAULT)
        audio_filename = None

    return render_template('output.html', summary_text=summary_text, audio_filename=audio_filename)

@app.route('/download/<filename>')
@login_required
def download(filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
    try:
        return send_from_directory(user_folder, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/pdfPal/pdfParser')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")