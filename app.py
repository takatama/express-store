from bottle import route, run, template, request, redirect, response
import sqlite3
import uuid
import hashlib

SECRET_KEY = 'MY_HIDDEN_SECRET_KEY'
DATABASE_FILE = 'store.db'
conn = sqlite3.connect(DATABASE_FILE)

@route('/login')
def show_login():
    return template('''
<h1>ログイン</h1>
<p style="color:red;"> {{ !message }} </p>
<form action="/login" method="post">
<p>メールアドレス <input name="email" type="text" placeholder="user1@example.com" value="user1@example.com" /></p>
<p>パスワード <input name="password" type="password" placeholder="password1" value="password1" /></p>
<p><input value="ログイン" type="submit" /></p>
</form>''', message=request.query.message)

# https://www.pythoncentral.io/hashing-strings-with-python/ より引用
def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
def is_valid_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def query_nickname(email, password):
    cur = conn.cursor()
    result = cur.execute('SELECT hashed_password, nickname FROM users WHERE email = ?;', (email,)).fetchone()
    if result is not None and is_valid_password(result[0], password):
        return result[1]
    return None

@route('/login', method="post")
def do_login():
    email = request.forms.get('email')
    password = request.forms.get('password')
    nickname = query_nickname(email, password)
    if nickname is None:
        return redirect('/login?message=ログインに失敗しました。')
    response.set_cookie("nickname", nickname, secret=SECRET_KEY)
    redirect('/products')

@route('/logout')
def do_logout():
    response.set_cookie("nickname", None, secret=SECRET_KEY)
    redirect('/login?message=ログアウトしました。')

@route('/products')
def list_products():
    nickname = request.get_cookie("nickname", secret=SECRET_KEY)
    if nickname is None:
        redirect('/login?message=ログインしてください。')
    cur = conn.cursor()
    results = cur.execute('SELECT p.name, p.description, p.image_url, p.price_yen, IFNULL(ROUND(AVG(r.rate), 1), "無し") FROM products AS p LEFT OUTER JOIN reviews AS r ON p.id = r.product_id GROUP BY p.id;')
    return template('''
<p>ようこそ、{{ nickname }}さん（<a href="/logout">ログアウト</a>）</p>
<h1>商品一覧</h1>
<table border="1">
  <tr>
    <th>商品名</th><th>説明</th><th>画像</th><th>価格</th><th>評価</th>
  </tr>
  %for p in products:
  <tr>
    <td>{{ p[0] }}</td><td>{{ p[1] }}</td><td><img src="{{ p[2] }}"</td><td>{{ p[3] }}円</td><td>{{ p[4] }}</td>
  </tr>
  %end
</table>''', nickname=nickname, products=results)

run(host='localhost', port=8080)