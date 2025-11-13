from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import secrets
from functools import wraps
from datetime import datetime
import json
from translations import get_translation, get_all_translations

# ==========================
# Flask App Configuration
# ==========================
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'data/electro_fahes.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure folders exist
os.makedirs('data', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images/technicians', exist_ok=True)
os.makedirs('static/images/inverters', exist_ok=True)

# ==========================
# Database Functions
# ==========================
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Check if language column exists, if not add it
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'language' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
            conn.commit()
            print("Added 'language' column to users table")
    except Exception as e:
        print(f"Migration check: {e}")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            inverter_model TEXT,
            image_path TEXT,
            diagnosis TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            phone TEXT,
            email TEXT,
            location TEXT,
            experience_years INTEGER,
            image_path TEXT,
            rating REAL DEFAULT 5.0
        );
    """)
    # Insert demo data if empty
    count = conn.execute("SELECT COUNT(*) FROM technicians").fetchone()[0]
    if count == 0:
        technicians_data = [
            ('Ahmad Hassan', 'Solar Inverter Specialist', '+961 70 123 456', 'ahmad@electro.com', 'Sidon', 8, None, 4.9),
            ('Sarah Khalil', 'Electrical Systems Engineer', '+961 71 234 567', 'sarah@electro.com', 'Tyre', 6, None, 4.8),
            ('Karim Fares', 'Power Electronics Expert', '+961 76 345 678', 'karim@electro.com', 'Nabatieh', 10, None, 5.0),
            ('Layla Mansour', 'Renewable Energy Technician', '+961 03 456 789', 'layla@electro.com', 'Saida', 5, None, 4.7)
        ]
        conn.executemany("""
            INSERT INTO technicians (name, specialty, phone, email, location, experience_years, image_path, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, technicians_data)
    conn.commit()
    conn.close()

# ==========================
# Utility Functions
# ==========================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            lang = session.get('language', 'en')
            flash(get_translation(lang, 'msg_login_required'), 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def verified_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            lang = session.get('language', 'en')
            flash(get_translation(lang, 'msg_login_required'), 'warning')
            return redirect(url_for('login'))
        if not session.get('is_verified'):
            lang = session.get('language', 'en')
            flash(get_translation(lang, 'msg_verify_email'), 'warning')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# ==========================
# Template Context
# ==========================
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}


@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    return {'t': lambda key: get_translation(lang, key)}

# ==========================
# Routes
# ==========================
@app.route('/')
def index():
    # If user is logged in, redirect directly to AI Advisor
    if 'user_id' in session:
        return redirect(url_for('ai_advisor'))
    # Show landing page only for non-logged-in users
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get('language', 'en')
    
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not email or not password:
            flash(get_translation(lang, 'msg_all_fields_required'), 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash(get_translation(lang, 'msg_password_length'), 'error')
            return redirect(url_for('register'))

        token = secrets.token_urlsafe(32)
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (full_name, email, password_hash, verification_token, language) VALUES (?, ?, ?, ?, ?)",
                (full_name, email, generate_password_hash(password), token, lang)
            )
            conn.commit()
            flash(get_translation(lang, 'msg_account_created'), 'success')

            # Auto-verify for demo
            conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
            conn.commit()
        except sqlite3.IntegrityError:
            flash(get_translation(lang, 'msg_email_exists'), 'error')
            return redirect(url_for('login'))
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('language', 'en')
    
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['is_verified'] = bool(user['is_verified'])
            session['user_email'] = user['email']
            
            # Safely get language with fallback
            try:
                session['language'] = user['language'] if user['language'] else 'en'
            except (KeyError, IndexError):
                session['language'] = 'en'
            
            flash(get_translation(session['language'], 'msg_welcome_back').format(name=user['full_name']), 'success')
            return redirect(url_for('home'))
        else:
            flash(get_translation(lang, 'msg_wrong_credentials'), 'error')

    return render_template('login.html')


@app.route('/verify/<token>')
def verify_email(token):
    lang = session.get('language', 'en')
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE verification_token = ?", (token,)).fetchone()
    if user:
        conn.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user['id'],))
        conn.commit()
        flash(get_translation(lang, 'msg_email_verified'), 'success')
    else:
        flash(get_translation(lang, 'msg_invalid_verification'), 'error')
    conn.close()
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    lang = session.get('language', 'en')
    name = session.get('user_name', 'User')
    session.clear()
    flash(get_translation(lang, 'msg_goodbye').format(name=name), 'info')
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    lang = session.get('language', 'en')
    conn = get_db()
    
    # Get total requests count
    total_requests = conn.execute(
        "SELECT COUNT(*) FROM service_requests WHERE user_id = ?", 
        (session['user_id'],)
    ).fetchone()[0]
    
    # Get recent requests
    recent_requests = conn.execute(
        "SELECT * FROM service_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('home.html', 
                         total_requests=total_requests,
                         recent_requests=recent_requests)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    lang = session.get('language', 'en')
    conn = get_db()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_name':
            new_name = request.form.get('full_name', '').strip()
            if new_name:
                conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (new_name, session['user_id']))
                conn.commit()
                session['user_name'] = new_name
                flash(get_translation(lang, 'msg_name_updated'), 'success')
            else:
                flash(get_translation(lang, 'msg_name_empty'), 'error')

        elif action == 'update_language':
            new_lang = request.form.get('language', 'en')
            conn.execute("UPDATE users SET language = ? WHERE id = ?", (new_lang, session['user_id']))
            conn.commit()
            session['language'] = new_lang
            flash(get_translation(new_lang, 'msg_language_updated'), 'success')

        conn.close()
        return redirect(url_for('settings'))

    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    current_language = session.get('language', 'en')
    return render_template('settings.html', user=user, current_language=current_language)


@app.route('/ai-advisor', methods=['GET', 'POST'])
@verified_required
def ai_advisor():
    lang = session.get('language', 'en')
    result = None
    error = None

    if request.method == 'POST':
        inverter_model = request.form.get('inverter_model', '').strip()
        image = request.files.get('image')

        if not inverter_model:
            error = get_translation(lang, 'error_no_model')
        elif not image or image.filename == '':
            error = get_translation(lang, 'error_no_image')
        elif not allowed_file(image.filename):
            error = get_translation(lang, 'error_invalid_file')
        else:
            try:
                filename = secure_filename(f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)

                diagnosis = generate_diagnosis(inverter_model, filepath)

                conn = get_db()
                conn.execute("""
                    INSERT INTO service_requests (user_id, inverter_model, image_path, diagnosis, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (session['user_id'], inverter_model, filepath, diagnosis, 'completed'))
                conn.commit()
                conn.close()

                result = {'model': inverter_model, 'diagnosis': diagnosis, 'image_path': filepath}
                flash(get_translation(lang, 'msg_diagnosis_complete'), 'success')

            except Exception as e:
                error = f'{get_translation(lang, "error_processing")}: {str(e)}'
                flash(error, 'error')

    return render_template('ai_advisor.html', result=result, error=error)


def generate_diagnosis(model, image_path):
    import random
    diagnoses = [
        {'issue': 'Low Battery Voltage', 'severity': 'Medium', 'solution': 'Check battery connections and charge level.', 'estimated_cost': '$50-150'},
        {'issue': 'Overload Protection Activated', 'severity': 'High', 'solution': 'Reduce load and inspect appliances.', 'estimated_cost': '$30-80'},
        {'issue': 'Grid Voltage Fluctuation', 'severity': 'Low', 'solution': 'Install voltage stabilizer.', 'estimated_cost': '$100-200'},
        {'issue': 'Temperature Warning', 'severity': 'Medium', 'solution': 'Improve ventilation and clean cooling fans.', 'estimated_cost': '$20-60'},
    ]
    return json.dumps(random.choice(diagnoses), indent=2)


@app.route('/technicians')
@verified_required
def technicians():
    conn = get_db()
    techs = conn.execute("SELECT * FROM technicians ORDER BY rating DESC").fetchall()
    conn.close()
    return render_template('technicians.html', technicians=techs)


@app.route('/videos')
@verified_required
def videos():
    videos = [
        {'title': 'Solar Inverter Basics', 'description': 'Learn the fundamentals', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '10:32'},
        {'title': 'Troubleshooting Errors', 'description': 'Fix common inverter issues', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '15:45'},
        {'title': 'Battery Maintenance', 'description': 'Tips for long battery life', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '8:20'},
        {'title': 'Installation Guide', 'description': 'Best setup practices', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '22:15'},
    ]
    return render_template('videos.html', videos=videos)


@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    requests = conn.execute("SELECT * FROM service_requests WHERE user_id = ? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('profile.html', user=user, requests=requests)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found.", is_logged_in='user_id' in session), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error.", is_logged_in='user_id' in session), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)