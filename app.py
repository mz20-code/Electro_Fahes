from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import secrets
from functools import wraps
from datetime import datetime
import json

# Import translation function
from translations import get_translation

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'data/electro_fahes.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images/technicians', exist_ok=True)
os.makedirs('static/images/inverters', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Service requests table
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

    # Technicians table
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

    # Insert sample technicians if empty
    count = conn.execute("SELECT COUNT(*) FROM technicians").fetchone()[0]
    if count == 0:
        technicians_data = [
            ('Ahmad Hassan', 'Solar Inverter Specialist', '+961 70 123 456', 'ahmad@electro.com', 'Sidon', 8, None, 4.9),
            ('Sarah Khalil', 'Electrical Systems Engineer', '+961 71 234 567', 'sarah@electro.com', 'Tyre', 6, None, 4.8),
            ('Karim Fares', 'Power Electronics Expert', '+961 76 345 678', 'karim@electro.com', 'Nabatieh', 10, None, 5.0),
            ('Layla Mansour', 'Renewable Energy Technician', '+961 03 456 789', 'layla@electro.com', 'Saida', 5, None, 4.7)
        ]
        conn.executemany(
            "INSERT INTO technicians (name, specialty, phone, email, location, experience_years, image_path, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            technicians_data
        )

    conn.commit()
    conn.close()


# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if not session.get('is_verified'):
            flash('Please verify your email to access this feature.', 'warning')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# Context processors
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}


@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    return {'t': lambda key: get_translation(lang, key)}


# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('ai_advisor'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))

        verification_token = secrets.token_urlsafe(32)
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (full_name, email, password_hash, verification_token) VALUES (?, ?, ?, ?)",
                (full_name, email, generate_password_hash(password), verification_token)
            )
            conn.commit()
            flash(f'Account created successfully! Check your email to verify.', 'success')
            # Auto-verify for demo
            conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))
        finally:
            conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('login'))

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['is_verified'] = bool(user['is_verified'])
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('home'))

        flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/verify/<token>')
def verify_email(token):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE verification_token = ?", (token,)).fetchone()

    if user:
        conn.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user['id'],))
        conn.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Invalid verification link.', 'error')

    conn.close()
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    return redirect(url_for('ai_advisor'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_name':
            new_name = request.form.get('full_name', '').strip()
            if new_name:
                conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (new_name, session['user_id']))
                conn.commit()
                session['user_name'] = new_name
                flash(get_translation(session.get('language', 'en'), 'msg_name_updated'), 'success')
            else:
                flash(get_translation(session.get('language', 'en'), 'msg_name_empty'), 'error')
        elif action == 'update_language':
            language = request.form.get('language', 'en')
            session['language'] = language
            flash(get_translation(session.get('language', 'en'), 'msg_language_updated'), 'success')
        conn.close()
        return redirect(url_for('settings'))

    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    current_language = session.get('language', 'en')
    return render_template('settings.html', user=user, current_language=current_language)


@app.route('/ai-advisor', methods=['GET', 'POST'])
@verified_required
def ai_advisor():
    result = None
    error = None

    if request.method == 'POST':
        inverter_model = request.form.get('inverter_model', '').strip()
        image = request.files.get('image')

        if not inverter_model:
            error = 'Please specify the inverter model.'
        elif not image or image.filename == '':
            error = 'Please upload an image of the inverter screen.'
        elif not allowed_file(image.filename):
            error = 'Invalid file type. Please upload an image (PNG, JPG, JPEG, GIF, WEBP).'
        else:
            try:
                filename = secure_filename(f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)

                diagnosis = generate_diagnosis(inverter_model, filepath)

                conn = get_db()
                conn.execute(
                    "INSERT INTO service_requests (user_id, inverter_model, image_path, diagnosis, status) VALUES (?, ?, ?, ?, ?)",
                    (session['user_id'], inverter_model, filepath, diagnosis, 'completed')
                )
                conn.commit()
                conn.close()

                result = {
                    'model': inverter_model,
                    'diagnosis': diagnosis,
                    'image_path': filepath
                }

                flash('Diagnosis completed successfully!', 'success')

            except Exception as e:
                error = f'An error occurred while processing your request: {str(e)}'
                flash(error, 'error')

    return render_template('ai_advisor.html', result=result, error=error)


def generate_diagnosis(model, image_path):
    """Mock AI diagnosis"""
    diagnoses = [
        {'issue': 'Low Battery Voltage', 'severity': 'Medium', 'solution': 'Check battery connections and charge level. Battery may need replacement if voltage remains low.', 'estimated_cost': '$50-150'},
        {'issue': 'Overload Protection Activated', 'severity': 'High', 'solution': 'Reduce connected load immediately. Check for short circuits or faulty appliances.', 'estimated_cost': '$30-80'},
        {'issue': 'Grid Voltage Fluctuation', 'severity': 'Low', 'solution': 'Install voltage stabilizer. Monitor grid voltage regularly.', 'estimated_cost': '$100-200'},
        {'issue': 'Temperature Warning', 'severity': 'Medium', 'solution': 'Ensure proper ventilation. Clean cooling fans. Check ambient temperature.', 'estimated_cost': '$20-60'}
    ]
    import random
    diagnosis = random.choice(diagnoses)
    return json.dumps(diagnosis, indent=2)


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
    video_list = [
        {'title': 'Solar Inverter Basics', 'description': 'Learn the fundamentals of solar inverter operation', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '10:32'},
        {'title': 'Troubleshooting Common Errors', 'description': 'Step-by-step guide to fix common inverter issues', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '15:45'},
        {'title': 'Battery Maintenance Tips', 'description': 'Keep your batteries healthy and long-lasting', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '8:20'},
        {'title': 'System Installation Guide', 'description': 'Professional installation best practices', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '22:15'}
    ]
    return render_template('videos.html', videos=video_list)


@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    requests = conn.execute("SELECT * FROM service_requests WHERE user_id = ? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('profile.html', user=user, requests=requests)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="The page you're looking for doesn't exist.", is_logged_in='user_id' in session), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error. Please try again later.", is_logged_in='user_id' in session), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
