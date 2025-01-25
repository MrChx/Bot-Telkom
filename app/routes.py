from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from app.database import UserDatabase
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

db = UserDatabase()

@app.route('/')
def halaman_utama():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if db.validasi_pengguna(username, password):
        from bot.authBot import AuthBot  # Import di sini untuk menghindari circular import
        
        session['username'] = username
        session['is_admin'] = db.cek_admin(username)
        
        # Kirim link ke bot auth (asumsi Anda memiliki cara untuk mendapatkan user_id)
        # Misalnya dengan menambahkankolom telegram_user_id di database
        user = db.dapatkan_pengguna_berdasarkan_username(username)
        if user and 'telegram_user_id' in user:
            auth_bot = AuthBot()
            auth_bot.kirim_link_setelah_login(user['telegram_user_id'])
        
        return jsonify({
            'berhasil': True, 
            'redirect': app.config['ASSISTANT_GROUP_LINK'],
            'is_admin': session['is_admin']
        })
    
    return jsonify({'berhasil': False, 'pesan': 'Kredensial tidak valid'})

@app.route('/admin')
def halaman_admin():
    if not session.get('is_admin'):
        return redirect(url_for('halaman_utama'))
    
    users = db.dapatkan_semua_pengguna()
    statistik = db.dapatkan_statistik_pengguna()
    
    return render_template('admin.html', users=users, statistik=statistik)

@app.route('/tambah_pengguna', methods=['POST'])
def tambah_pengguna():
    if not session.get('is_admin'):
        return jsonify({'berhasil': False, 'pesan': 'Tidak diizinkan'})
    
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

@app.route('/perbarui_pengguna/<user_id>', methods=['POST'])
def perbarui_pengguna(user_id):
    if not session.get('is_admin'):
        return jsonify({'berhasil': False, 'pesan': 'Tidak diizinkan'})
    
    data = request.form.to_dict()
    data['is_admin'] = data.get('is_admin') == 'on'
    
    berhasil = db.perbarui_pengguna(user_id, data)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Pengguna berhasil diperbarui' if berhasil else 'Gagal memperbarui'
    })

@app.route('/hapus_pengguna/<user_id>', methods=['POST'])
def hapus_pengguna(user_id):
    if not session.get('is_admin'):
        return jsonify({'berhasil': False, 'pesan': 'Tidak diizinkan'})
    
    berhasil = db.hapus_pengguna(user_id)
    
    return jsonify({
        'berhasil': berhasil,
        'pesan': 'Pengguna berhasil dihapus' if berhasil else 'Gagal menghapus'
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('halaman_utama'))