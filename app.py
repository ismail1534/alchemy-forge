import os
import re
import subprocess
import uuid
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, jsonify

app = Flask(__name__)
app.secret_key = 'philosophers_stone_secret'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flawed Sanitization
def sanitize_svg(content):
    # The State Alchemist's filter: "Equivalent Exchange requires removing the dangerous parts."
    # Flaw: Only removes literal <script> tags (case-insensitive) and 'javascript:'.
    # Bypass: <svg onload=alert(1)> or <img src=x onerror=alert(1)>
    
    # Remove <script> tags
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove javascript: protocol
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    
    return content

@app.after_request
def add_header(response):
    # CSP allows unsafe-inline, making XSS possible
    # Added connect-src * to allow exfiltration via fetch/XHR
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; connect-src *; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = str(uuid.uuid4()) + '.svg'
        content = file.read().decode('utf-8', errors='ignore')
        
        # Apply the flawed sanitization
        safe_content = sanitize_svg(content)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w') as f:
            f.write(safe_content)
            
        return redirect(url_for('view_circle', filename=filename))

@app.route('/view/<filename>')
def view_circle(filename):
    return render_template('view.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, mimetype='image/svg+xml')

@app.route('/report', methods=['POST'])
def report():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Extract filename from the provided URL
        target_filename = url.split('/')[-1]
        
        # Security check: Ensure it is an SVG
        if not target_filename.endswith('.svg'):
            return jsonify({'error': 'Invalid target file'}), 400

        # FORCE LOCALHOST: This fixes the "Empty Cookie" bug
        # The bot will visit 127.0.0.1, ensuring cookies are set in the correct context
        local_url = f"http://127.0.0.1:5000/view/{target_filename}"
        
        print(f"[*] State Alchemist is investigating: {local_url}")
        
        # Launch the bot
        subprocess.Popen(['node', 'bot.js', local_url])
        
        return jsonify({'message': 'The State Alchemist has been notified and will inspect your circle shortly.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
