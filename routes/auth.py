# routes/auth.py
import sys
import os

# Add the project root directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
from database import get_db

auth_bp = Blueprint('auth', __name__)

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = None
    cur = None
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
        
            # Comprehensive input validation
            if not username or not password or not email:
                flash('All fields are required!', 'error')
                return redirect(url_for('auth.signup'))
        
            if not validate_email(email):
                flash('Invalid email format!', 'error')
                return redirect(url_for('auth.signup'))
        
            if not validate_password(password):
                flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers', 'error')
                return redirect(url_for('auth.signup'))
            
            conn = get_db()
            cur = conn.cursor()
            
            # Check existing username
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                flash('Username already exists!', 'error')
                return redirect(url_for('auth.signup'))
            
            # Check existing email
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already registered!', 'error')
                return redirect(url_for('auth.signup'))
            
            # Create new user
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            conn.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
    
    except Exception as e:
        print(f"Error occurred during signup: {e}")
        flash('An error occurred. Please try again.', 'error')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    conn = None
    cur = None
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Please provide both username and password!', 'error')
                return redirect(url_for('auth.login'))

            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

            if user and check_password_hash(user[2], password):  # user[2] is the hashed password
                session.clear()
                session['user_id'] = user[0]  # user[0] is the id
                session['username'] = user[1]  # user[1] is the username
                flash('Welcome back!', 'success')
                return redirect(url_for('items.dashboard'))
            else:
                flash('Invalid username or password!', 'error')

    except Exception as e:
        print(f"Error occurred during login: {e}")
        flash('An error occurred. Please try again.', 'error')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
