from flask import Flask, request, render_template, make_response
import os, json, time
from pathlib import Path
from typing import List, Dict

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
APPS_FILE = DATA_DIR / 'applications.json'

if not APPS_FILE.exists():
    APPS_FILE.write_text('[]', encoding='utf-8')

app = Flask(__name__, template_folder='templates')
ADMIN_SESSION = os.environ.get('ADMIN_SESSION', 'ECHIDNA_ADMIN')
FLAG = os.environ.get('FLAG', 'flag{NOISY_ECHIDNA_ADMIN_XSS_FLAG}')

def load_apps() -> List[Dict]:
    try:
        return json.loads(APPS_FILE.read_text(encoding='utf-8') or '[]')
    except Exception:
        return []

def save_apps(apps: List[Dict]) -> None:
    APPS_FILE.write_text(json.dumps(apps, indent=2), encoding='utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['GET','POST'])
def apply():
    if request.method == 'POST':
        name = request.form.get('name','')
        email = request.form.get('email','')
        resume = request.form.get('resume','')
        apps = load_apps()
        new_id = (apps[-1]['id'] + 1) if apps else 1
        apps.append({
            'id': new_id,
            'name': name,
            'email': email,
            'resume': resume,
            'ts': time.time()
        })
        save_apps(apps)
        return render_template('apply_thanks.html')
    return render_template('apply.html')

# ADMIN ONLY ROUTES:
@app.route('/applications')
def applications():
    if request.cookies.get('admin_session','') != ADMIN_SESSION:
        return make_response('Forbidden', 403)

    apps = load_apps()
    save_apps([])
    return render_template('applications.html', apps=apps)

@app.route('/admin')
def admin():
    if request.cookies.get('admin_session','') != ADMIN_SESSION:
        return make_response('Forbidden', 403)
    return render_template('admin.html', flag=FLAG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)