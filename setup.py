import sqlite3
from random import randrange

database_file = 'store.db'
# append mode。もしファイルが存在していなければ作成する。
open(database_file, 'a').close()

conn = sqlite3.connect(database_file)
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS products;')
cur.execute('CREATE TABLE products(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, description STRING, image_url STRING, price_yen INTEGER);')
insert_sql = 'INSERT INTO products(name, description, image_url, price_yen) values (?, ?, ?, ?);'
insert_data = []
for i in range(1, 10):
    insert_data.append(('商品' + str(i), '商品' + str(i) + 'の説明', 'https://via.placeholder.com/150', randrange(1, 100) * 100))
cur.executemany(insert_sql, insert_data)
conn.commit()
for row in cur.execute('SELECT * FROM products;').fetchall():
    print(row)
conn.close()