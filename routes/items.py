# routes/items.py

import sys
import os

# Add the project root directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db
from decimal import Decimal
from functools import wraps

items_bp = Blueprint('items', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@items_bp.route('/dashboard')
@login_required
def dashboard():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT i.*, u.username as created_by 
            FROM items i 
            JOIN users u ON i.user_id = u.id 
            WHERE i.user_id = %s
            ORDER BY i.created_at DESC
        """, (session['user_id'],))
        items = cur.fetchall()
        
        # Render the dashboard template with the fetched items
        return render_template('dashboard.html', items=items)
        
    except Exception as e:
        flash(f'Error loading items: {str(e)}', 'error')
        
        # In case of an error, redirect to the dashboard route with a flash message
        return redirect(url_for('items.dashboard'))
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@items_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()

        # First, check if the item exists and belongs to the current user
        cur.execute("DELETE FROM items WHERE id = %s AND user_id = %s", (item_id, session['user_id']))

        if cur.rowcount == 0:
            flash('Item not found or you do not have permission to delete.', 'error')
        else:
            conn.commit()
            flash('Item deleted successfully!', 'success')

        return redirect(url_for('items.dashboard'))
    
    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'error')
        return redirect(url_for('items.dashboard'))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@items_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    conn = None
    cur = None
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')

            try:
                price = Decimal(price)
                if price <= 0:
                    raise ValueError("Price must be greater than zero")
            except ValueError:
                flash('Invalid price. Please enter a valid number.', 'error')
                return redirect(url_for('items.add_item'))

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO items (name, description, price, user_id) VALUES (%s, %s, %s, %s)",
                (name, description, price, session['user_id'])
            )
            conn.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('items.dashboard'))
    except Exception as e:
        flash(f'Error adding item: {str(e)}', 'error')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return render_template('add_item.html')

@items_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Check if the item exists and belongs to the current user
        cur.execute("SELECT * FROM items WHERE id = %s AND user_id = %s", (item_id, session['user_id']))
        item = cur.fetchone()
        
        if not item:
            flash('Item not found or you do not have permission to edit.', 'error')
            return redirect(url_for('items.dashboard'))

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')

            try:
                price = Decimal(price)
                if price <= 0:
                    raise ValueError("Price must be greater than zero")
            except ValueError:
                flash('Invalid price. Please enter a valid number.', 'error')
                return redirect(url_for('items.edit_item', item_id=item_id))

            cur.execute(
                "UPDATE items SET name = %s, description = %s, price = %s WHERE id = %s",
                (name, description, price, item_id)
            )
            conn.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('items.dashboard'))

        return render_template('edit_item.html', item=item)
    
    except Exception as e:
        flash(f'Error editing item: {str(e)}', 'error')
        return redirect(url_for('items.dashboard'))
    finally:
        if cur:
            cur.close
