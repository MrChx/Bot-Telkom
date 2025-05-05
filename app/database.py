from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import sys
from datetime import datetime

class UserDatabase:
    def __init__(self):
        try:
            client_options = {
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 10000,
                'retryWrites': True
            }
            
            print(f"Mencoba koneksi ke MongoDB...")
            self.client = MongoClient(Config.MONGODB_URI, **client_options)
            
            self.client.admin.command('ping')
            print("Berhasil terkoneksi ke MongoDB!")
            
            self.db = self.client[Config.MONGODB_DATABASE]
            self.users_collection = self.db['users']
            self.tutorials_collection = self.db['tutorials']
            
        except Exception as e:
            print(f"Error koneksi MongoDB: {str(e)}", file=sys.stderr)
            print("Pastikan:")
            print("1. Connection string MongoDB benar")
            print("2. Network memiliki akses ke MongoDB Atlas")
            print("3. IP Address sudah di-whitelist di MongoDB Atlas")
            raise

    # User Managemen
    def tambah_pengguna(self, username, password, is_admin=False):
        if self.users_collection.find_one({'username': username}):
            return False
        
        hashed_password = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'password': hashed_password,
            'is_admin': is_admin,
            'aktif': True,
            'login_timestamp': None,
            'telegram_id': None
        }
        
        self.users_collection.insert_one(user_data)
        return True
    
    def update_login_status(self, username, telegram_id):
        return self.users_collection.update_one(
            {'username': username},
            {
                '$set': {
                    'login_timestamp': datetime.utcnow(),
                    'telegram_id': int(telegram_id)
                }
            }
        )
        
    def is_login_valid(self, telegram_id):
        user = self.users_collection.find_one({'telegram_id': int(telegram_id)})
        
        if not user or not user.get('login_timestamp'):
            print(f"[DEBUG] User dengan telegram_id {telegram_id} tidak ditemukan atau belum login.")
            return False
        
        time_diff = datetime.utcnow() - user['login_timestamp']
        print(f"[DEBUG] Selisih waktu login: {time_diff.total_seconds()} detik")
        
        return time_diff.total_seconds() < 24 * 3600

    def validasi_pengguna(self, username, password):
        user = self.users_collection.find_one({'username': username, 'aktif': True})
        return user and check_password_hash(user['password'], password)

    def dapatkan_semua_pengguna(self):
        return list(self.users_collection.find({'aktif': True}, {'password': 0}))

    def dapatkan_pengguna_berdasarkan_id(self, user_id):
        try:
            return self.users_collection.find_one({'_id': ObjectId(user_id), 'aktif': True}, {'password': 0})
        except:
            return None
        
    def dapatkan_pengguna_berdasarkan_username(self, username):
        return self.users_collection.find_one({'username': username}, {'password': 0})

    def perbarui_pengguna(self, user_id, update_data):
        try:
            if 'password' in update_data and update_data['password']:
                update_data['password'] = generate_password_hash(update_data['password'])
            
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': update_data}
            )
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def hapus_pengguna(self, user_id, permanent=False):
        try:
            if permanent:
                # Hard delete: completely remove user from database
                self.users_collection.delete_one({'_id': ObjectId(user_id)})
            else:
                # Soft delete: mark user as inactive
                self.users_collection.update_one(
                    {'_id': ObjectId(user_id)}, 
                    {'$set': {'aktif': False}}
                )
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def dapatkan_statistik_pengguna(self):
        return {
            'total_pengguna': self.users_collection.count_documents({'aktif': True}),
            'total_admin': self.users_collection.count_documents({'is_admin': True, 'aktif': True}),
            'total_tutorial': self.tutorials_collection.count_documents({})
        }

    def cek_admin(self, username):
        user = self.users_collection.find_one({'username': username, 'is_admin': True, 'aktif': True})
        return user is not None
        
    # Tutorial Management
    def tambah_tutorial(self, title, text_content, image_file_id):
        tutorial_data = {
            'title': title,
            'text_content': text_content,
            'image_file_id': image_file_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'command': f"tutorial_{title.lower().replace(' ', '_')}"
        }
        
        result = self.tutorials_collection.insert_one(tutorial_data)
        return str(result.inserted_id)
    
    def perbarui_tutorial(self, tutorial_id, update_data):
        try:
            update_data['updated_at'] = datetime.utcnow()
            
            # Update command if title is changed
            if 'title' in update_data:
                update_data['command'] = f"tutorial_{update_data['title'].lower().replace(' ', '_')}"
            
            self.tutorials_collection.update_one(
                {'_id': ObjectId(tutorial_id)}, 
                {'$set': update_data}
            )
            return True
        except Exception as e:
            print(f"Error updating tutorial: {e}")
            return False
    
    def hapus_tutorial(self, tutorial_id):
        try:
            self.tutorials_collection.delete_one({'_id': ObjectId(tutorial_id)})
            return True
        except Exception as e:
            print(f"Error deleting tutorial: {e}")
            return False
    
    def dapatkan_semua_tutorial(self):
        return list(self.tutorials_collection.find().sort('created_at', -1))
    
    def dapatkan_tutorial_berdasarkan_id(self, tutorial_id):
        try:
            return self.tutorials_collection.find_one({'_id': ObjectId(tutorial_id)})
        except:
            return None
    
    def dapatkan_tutorial_berdasarkan_command(self, command):
        return self.tutorials_collection.find_one({'command': command})