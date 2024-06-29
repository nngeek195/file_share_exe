import os
import threading
import webbrowser
import socket
from flask import Flask, request, send_from_directory, jsonify, render_template_string, abort
from werkzeug.utils import secure_filename
from tkinter import Tk, Button, Label

# Set the upload folder relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, 'uploads')

app = Flask(__name__)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Flask Routes
@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    server_ip = get_ip()
    server_port = 5000
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="Niranga">
    <meta name="description" content="This is a free source used for CIS students in SUSL">
    <title>2N Share</title>
    <link rel="icon" href="logo.png" type="image/x-icon">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #F2F3F4;
            text-align: center;
        }
        .header, .footer {
            background-color: #58D68D;
            color: white;
            padding: 20px 0;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
        }
        .footer p {
            margin: 0;
            text-align: right;
            padding-right: 10px;
        }
        h1, h2 {
            color: #333;
        }
        .button {
            display: inline-block;
            margin: 10px auto;
            background-color: #4CAF50;
            color: white;
            padding: 14px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
        }
        .button:hover {
            background-color: #45a049;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin-bottom: 10px;
        }
        .link_section {
            display: inline-block;
            margin: 10px auto;
            background-color: #ff00f7;
            color: white;
            padding: 14px 20px;
            border: none;
            border-radius: 4px;
            cursor: progress;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <section id="link_section">
            <a href="https://www.linkedin.com/in/niranga-nayanajith-548a0a302/" class="linkedin-logo">
                <p><strong>TAP ME &#128640;</strong></p>
            </a>
        </section>
    </div>
    
    <h1>2N Share</h1>
    <p>Server running at: <strong>{{ server_ip }}:{{ server_port }}</strong></p>
    <form id="uploadForm" method="post" enctype="multipart/form-data">
        <input type="file" name="files" id="fileInput" class="button" multiple>
        <input type="submit" value="Upload" class="button">
    </form>

    <h2>Uploaded Files</h2>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('uploaded_file', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    <div class="footer">
        <a href="https://www.linkedin.com/in/niranga-nayanajith-548a0a302/" target="_blank">
            <p>@2N Technologies</p>
        </a>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const files = document.getElementById('fileInput').files;
            const formData = new FormData();

            for (const file of files) {
                formData.append('files', file);
            }

            fetch('/upload', {
                method: 'POST',
                body: formData
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Failed to upload files');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('An error occurred while uploading files');
            });
        });
    </script>
</body>
</html>
    ''', files=files, server_ip=server_ip, server_port=server_port)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify(success=False)
    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"File saved to: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")
    return jsonify(success=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

# Function to run Flask app
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# Tkinter GUI
def start_server():
    threading.Thread(target=run_flask).start()
    webbrowser.open("http://127.0.0.1:5000")

def create_gui():
    root = Tk()
    root.title("2N Share")

    Label(root, text="2N Share", font=("Helvetica", 24)).pack(pady=10)
    Button(root, text="Start Server", command=start_server, font=("Arial", 14)).pack(pady=5)
    Button(root, text="Open Web Interface", command=lambda: webbrowser.open("http://127.0.0.1:5000"), font=("Arial", 14)).pack(pady=5)
    Button(root, text="Exit", command=root.quit, font=("Arial", 14)).pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    create_gui()
