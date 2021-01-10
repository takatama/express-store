import sqlite3
from random import randrange
import uuid
import hashlib


DATABASE_FILE = 'store.db'

# https://www.pythoncentral.io/hashing-strings-with-python/ より引用
def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

# append mode。もしファイルが存在していなければ作成する。
open(DATABASE_FILE, 'a').close()

conn = sqlite3.connect(DATABASE_FILE)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS products;')
cur.execute('CREATE TABLE products(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, description STRING, image_url STRING, price_yen INTEGER);')
# 9つの商品を登録する。
products = []
for i in range(1, 10):
    products.append(('商品' + str(i), '商品' + str(i) + 'の説明', 'https://via.placeholder.com/150', randrange(1, 100) * 100))
cur.executemany('INSERT INTO products(name, description, image_url, price_yen) values (?, ?, ?, ?);', products)

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, email STRING, hashed_password STRING, nickname STRING);')
# 9人のユーザーを登録する。
users = []
for i in range(1, 10):
    users.append(('user' + str(i) + '@example.com', hash_password('password' + str(i)), 'ユーザー' + str(i)))
cur.executemany('INSERT INTO users(email, hashed_password, nickname) values(?, ?, ?)', users)

conn.commit()

for row in cur.execute('SELECT * FROM products;').fetchall():
    print(row)

for row in cur.execute('SELECT * FROM users;').fetchall():
    print(row)

conn.close()