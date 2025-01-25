from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

class UserDatabase:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_DATABASE]
        self.users_collection = self.db['users']

    def tambah_pengguna(self, username, password, is_admin=False):
        if self.users_collection.find_one({'username': username}):
            return False
        
        hashed_password = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'password': hashed_password,
            'is_admin': is_admin,
            'aktif': True
        }
        
        self.users_collection.insert_one(user_data)
        return True

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
            if 'password' in update_data:
                update_data['password'] = generate_password_hash(update_data['password'])
            
            self.users_collection.update_one(
                {'_id': ObjectId(user_id), 'aktif': True}, 
                {'$set': update_data}
            )
            return True
        except:
            return False

    def hapus_pengguna(self, user_id):
        try:
            # Soft delete
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': {'aktif': False}}
            )
            return True
        except:
            return False

    def dapatkan_statistik_pengguna(self):
        return {
            'total_pengguna': self.users_collection.count_documents({'aktif': True}),
            'total_admin': self.users_collection.count_documents({'is_admin': True, 'aktif': True})
        }

    def cek_admin(self, username):
        user = self.users_collection.find_one({'username': username, 'is_admin': True, 'aktif': True})
        return user is not None