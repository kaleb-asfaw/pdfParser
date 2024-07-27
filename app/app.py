from flask import (
    Flask, 
    render_template, 
    redirect, 
    url_for, 
    jsonify, 
    send_file,
    request, session,
    )
from flask_behind_proxy import FlaskBehindProxy
from io import BytesIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sys, os, time, markdown2
import git
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from func.parse import get_summary_from_upload
from func.synthesize import make_mp3
import bcrypt
from bs4 import BeautifulSoup
from app.login_db import find_user_by_email, create_user, get_db_connection
from func.database import upload_audio, fetch_audio, get_mp3_file_names, upload_text, fetch_text

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

def process_text_and_audio(file):
    # unique filename using timestamp // -4 to remove pdf
    upload_timestamp = int(time.time())
    filename = f'{upload_timestamp}_{file.filename[:-4]}'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    print('FILE UPLOADED SUCCESSFULLY: ', file_path)

    try:
        summary_text = get_summary_from_upload(file_path)
    except ValueError as e:
        summary_text = SUMMARY_TEXT_DEFAULT
        print('ERROR with getting summary text for upload: ', e)

    # delete after using file
    os.remove(file_path)
    print('FILE DELETED SUCCESSFULLY: ', file_path)

    # take out markdown for text-to-speech
    html_str = markdown2.markdown(summary_text)
    soup = BeautifulSoup(html_str, 'html.parser')
    plain_text = soup.get_text()

    mp3_data = make_mp3(plain_text)
    return html_str, mp3_data, filename

@app.route('/upload', methods=["POST"])
@login_required
def upload():
    # edge cases
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    elif not file.filename.endswith('.pdf'):
        return "Invalid file type. Only PDFs are allowed."
    
    html_summary, mp3_data, filename = process_text_and_audio(file)

    # save to supabase
    upload_audio(current_user.id, f'{filename}.mp3', mp3_data)
    upload_text(current_user.id, filename, html_summary)
    
    return redirect(url_for('output', summary_text=html_summary, mp3_filename=f'{filename}.mp3'))
    


@app.route('/library', methods=['GET'])
@login_required
def library():
    # display all libraries for this user
    mp3_filenames = get_mp3_file_names(current_user.id)
    return render_template('library.html', mp3_names=mp3_filenames, user_id=current_user.id)

@app.route('/fetch_audio/<user_id>/<mp3_filename>', methods=['GET'])
@login_required
def fetch_audio_route(user_id, mp3_filename):
    try:
        binary_data = fetch_audio(user_id, mp3_filename)
        return send_file(BytesIO(binary_data), mimetype='audio/mp3')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/fetch_text/<user_id>/<filename>', methods=['GET'])
def fetch_text_route(user_id, filename):
    try:
        text = fetch_text(user_id, filename)
        html_str = markdown2.markdown(text['text'])
        return jsonify({'text': html_str})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/output', methods=['GET'])
@login_required
def output():
    
    session['summary_text'] = request.args.get('summary_text', '') #TODO: think of a better way to do this
    if not session['summary_text']:
        session['summary_text'] = SUMMARY_TEXT_DEFAULT

    mp3_filename = request.args.get('mp3_filename', '')

    return render_template('output.html', user_id=current_user.id, audio_filename=mp3_filename)


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
    