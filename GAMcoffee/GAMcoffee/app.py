import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from Controller.menu_controller import MenuController
from Model.menu_model import MenuModel

app = Flask(__name__)
app.secret_key = 'your_secret_key'
menu_model = MenuModel()

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn kích thước tệp tải lên (16 MB)

# Tạo thư mục nếu không tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Khởi tạo cơ sở dữ liệu
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            image TEXT
        )''')
        conn.commit()

init_db()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    menu_items = menu_model.get_menu_items()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/checkout')
def checkout():
    order_items = session.get('order_items', [])
    total_price = sum(item['price'] for item in order_items)
    return render_template('checkout.html', order_items=order_items, total_price=total_price)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    flash('Payment processed successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/menu_items_json')
def menu_items_json():
    menu_items = menu_model.get_menu_items()
    return jsonify(menu_items)

@app.route('/shopping-cart')
def shopping_cart():
    return render_template('shopping_cart.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):  # Password validation
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # Hash password
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                session['username'] = username
                flash('Registration successful! You are now logged in.', 'success')
                return redirect(url_for('home'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/list_menu')
def list_menu():
    if 'username' in session:
        menu_items = menu_model.get_menu_items()
        return render_template('list_menu.html', items=menu_items)
    else:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('login'))
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu():
    if 'username' in session:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            image = request.files.get('image')

            if image and image.filename:  # Kiểm tra tệp hình ảnh hợp lệ
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

                try:
                    image.save(image_path)  # Lưu hình ảnh vào thư mục
                    menu_model.store_menu(name, price, description, image_filename)
                    flash('Menu item added successfully!', 'success')
                    return redirect(url_for('list_menu'))
                except Exception as e:
                    flash(f'Error saving image: {e}', 'danger')
            else:
                flash('Please upload a valid image.', 'danger')
        return render_template('menu_form.html')
    else:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('login'))


@app.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu(item_id):
    if 'username' in session:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            image = request.files.get('image')

            if image:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            else:
                image_filename = menu_model.get_menu_item_by_id(item_id)['image']  # Keep existing image

            menu_model.update_menu(item_id, name, price, description, image_filename)
            flash('Menu item updated successfully!', 'success')
            return redirect(url_for('list_menu'))
        else:
            menu_item = menu_model.get_menu_item_by_id(item_id)
            return render_template('menu_form.html', item=menu_item)
    else:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

@app.route('/menu/delete/<int:item_id>', methods=['POST'])
def delete_menu(item_id):
    if 'username' in session:
        menu_model.delete_menu(item_id)
        flash('Menu item deleted successfully!', 'success')
        return redirect(url_for('list_menu'))
    else:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
