import os
import random
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# === Config ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
sessions = {}

# === Helpers ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_otp():
    return str(random.randint(1000, 9999))

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_upload', methods=['GET'])
def start_upload():
    return render_template('upload_start.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    otp = generate_otp()
    otp_folder = os.path.join(UPLOAD_FOLDER, otp)
    os.makedirs(otp_folder, exist_ok=True)

    uploaded_files = request.files.getlist("pdfs")
    saved_files = []

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(otp_folder, filename))
            saved_files.append(filename)

    if not saved_files:
        return "❌ No valid PDF uploaded.", 400

    sessions[otp] = saved_files
    return render_template('done.html', otp=otp)

@app.route('/download/<otp>/<filename>')
def download_file(otp, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, otp), filename)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
