from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from functools import wraps
from app.database import UserDatabase
from config import Config
import os
import uuid
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = UserDatabase()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def halaman_utama():
    return render_template('login.html')

# user
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    telegram_id = request.form.get('telegram_id')
    
    if db.validasi_pengguna(username, password):
        session['username'] = username
        session['is_admin'] = db.cek_admin(username)
        
        if telegram_id:
            db.update_login_status(username, telegram_id)
        
        return jsonify({
            'berhasil': True, 
            'redirect': app.config['ASSISTANT_GROUP_LINK'],
            'is_admin': session['is_admin']
        })
    
    return jsonify({'berhasil': False, 'pesan': 'Kredensial tidak valid'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('halaman_utama'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'berhasil': False, 'pesan': 'Akses ditolak: Admin only'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if (username == os.getenv('ADMIN_USERNAME') and 
            password == os.getenv('ADMIN_PASSWORD')):
            session['is_admin'] = True
            return jsonify({'berhasil': True, 'redirect': '/admin/dashboard'})
        
        return jsonify({'berhasil': False, 'pesan': 'Kredensial admin tidak valid'})
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = db.dapatkan_semua_pengguna()
    statistik = db.dapatkan_statistik_pengguna()
    tutorials = db.dapatkan_semua_tutorial()
    return render_template('admin_dashboard.html', users=users, statistik=statistik, tutorials=tutorials)

@app.route('/admin/tambah_pengguna', methods=['POST'])
@admin_required
def tambah_pengguna():
    data = request.form
    berhasil = db.tambah_pengguna(
        data['username'], 
        data['password'], 
        data.get('is_admin') == 'on'
    )
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Pengguna berhasil ditambahkan' if berhasil else 'Username sudah ada'
    })

@app.route('/admin/perbarui_pengguna/<user_id>', methods=['POST'])
@admin_required
def perbarui_pengguna(user_id):
    data = request.form.to_dict()
    
    if not data.get('password'):
        data.pop('password', None)
    
    data['is_admin'] = data.get('is_admin') == 'on'
    
    berhasil = db.perbarui_pengguna(user_id, data)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Pengguna berhasil diperbarui' if berhasil else 'Gagal memperbarui'
    })

@app.route('/admin/hapus_pengguna/<user_id>', methods=['POST'])
@admin_required
def hapus_pengguna(user_id):
    berhasil = db.hapus_pengguna(user_id, permanent=True)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Pengguna berhasil dihapus' if berhasil else 'Gagal menghapus'
    })

# tutorial
# @app.route('/admin/tutorials')
# @admin_required
# def admin_tutorials():
#     tutorials = db.dapatkan_semua_tutorial()
#     return render_template('admin_tutorials.html', tutorials=tutorials)

@app.route('/admin/tambah_tutorial', methods=['POST'])
@admin_required
def tambah_tutorial():
    title = request.form['title']
    text_content = request.form['text_content']
    image_file_id = request.form.get('image_file_id', None)
    
    success = db.tambah_tutorial(title, text_content, image_file_id)
    return jsonify({'berhasil': bool(success), 'pesan': 'Tutorial berhasil ditambahkan'})

@app.route('/admin/perbarui_tutorial/<tutorial_id>', methods=['POST'])
@admin_required
def perbarui_tutorial(tutorial_id):
    data = {
        'title': request.form['title'],
        'text_content': request.form['text_content']
    }
    
    if request.form.get('image_file_id'):
        data['image_file_id'] = request.form['image_file_id']
    
    berhasil = db.perbarui_tutorial(tutorial_id, data)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Tutorial berhasil diperbarui' if berhasil else 'Gagal memperbarui tutorial'
    })

@app.route('/admin/hapus_tutorial/<tutorial_id>', methods=['POST'])
@admin_required
def hapus_tutorial(tutorial_id):
    berhasil = db.hapus_tutorial(tutorial_id)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Tutorial berhasil dihapus' if berhasil else 'Gagal menghapus tutorial'
    })

@app.route('/api/tutorials/<command>')
def get_tutorial_api(command):
    tutorial = db.dapatkan_tutorial_berdasarkan_command(command)
    
    if not tutorial:
        return jsonify({'berhasil': False, 'pesan': 'Tutorial tidak ditemukan'})
    
    return jsonify({
        'berhasil': True,
        'tutorial': {
            'title': tutorial['title'],
            'text_content': tutorial['text_content'],
            'image_file_id': tutorial['image_file_id']
        }
    })

@app.route('/api/tutorials')
def get_all_tutorials_api():
    tutorials = db.dapatkan_semua_tutorial()
    
    tutorials_data = [{
        'id': str(tutorial['_id']),
        'title': tutorial['title'],
        'command': tutorial['command']
    } for tutorial in tutorials]
    
    return jsonify({
        'berhasil': True,
        'tutorials': tutorials_data
    })