from bottle import route, run, template, request, redirect, response, abort
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

def query_user(email, password):
    cur = conn.cursor()
    result = cur.execute('SELECT hashed_password, id, nickname FROM users WHERE email = ?;', (email,)).fetchone()
    if result is not None and is_valid_password(result[0], password):
        return result[1], result[2]
    return None

@route('/login', method="post")
def do_login():
    email = request.forms.get('email')
    password = request.forms.get('password')
    user_id, nickname = query_user(email, password)
    if user_id is None:
        return redirect('/login?message=ログインに失敗しました。')
    response.set_cookie("user_id", user_id, secret=SECRET_KEY)
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
    results = cur.execute('SELECT p.id, p.name, p.description, p.image_url, p.price_yen, IFNULL(ROUND(AVG(r.rate), 1), "無し") FROM products AS p LEFT OUTER JOIN reviews AS r ON p.id = r.product_id GROUP BY p.id;')
    return template('''
<p>ようこそ、{{ nickname }}さん（<a href="/logout">ログアウト</a>）</p>
<h1>商品一覧</h1>
<table border="1">
  <tr>
    <th>商品名</th><th>説明</th><th>画像</th><th>価格</th><th>評価</th><th>操作</th>
  </tr>
  %for p in products:
  <tr>
    <td>{{ p[1] }}</td><td>{{ p[2] }}</td><td><img src="{{ p[3] }}"</td><td>{{ p[4] }}円</td><td>{{ p[5] }}</td><td><a href="/products/{{ p[0] }}">詳細</a></td>
  </tr>
  %end
</table>''', nickname=nickname, products=results)

def selected_option(rate):
    html = []
    for i in range(5, 0, -1):
        if i == rate:
            html.append('<option value="' + str(i) + '" selected>' + str(i) + '</option>')
        else:
            html.append('<option value="' + str(i) + '">' + str(i) + '</option>')
    return ''.join(html)

@route('/products/<product_id>')
def show_product(product_id):
    nickname = request.get_cookie("nickname", secret=SECRET_KEY)
    if nickname is None:
        redirect('/login?message=ログインしてください。')
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    cur = conn.cursor()
    product = cur.execute('SELECT * FROM products WHERE id = ?;', (product_id,)).fetchone()
    if product is None:
        abort(400, '該当する商品がありません。')
    reviews = cur.execute('SELECT r.rate, r.comment, u.id, u.nickname FROM reviews r JOIN users u ON r.product_id = ? AND r.user_id = u.id;', (product_id,)).fetchall()
    rate = 0
    comments = []
    my_comment = None
    my_rate = None
    for review in reviews:
        rate += review[0]
        comments.append('【★' + str(review[0]) + '】' + review[1] + ' (' + review[3] + ')')
        if review[2] == user_id:
            my_rate = review[0]
            my_comment = review[1]
    if rate > 0:
        rate = round(rate / len(reviews), 1)
    else:
        rate = '無し'
    options = selected_option(my_rate)
    return template('''
<p>ようこそ、{{ nickname }}さん（<a href="/logout">ログアウト</a>）</p>
<h1>詳細</h1>
<table border="1">
  <tr><th>項目</th><th>内容</th></tr>
  <tr><td>商品名</td><td>{{ product[1] }}</td></tr>
  <tr><td>説明</td><td>{{ product[2] }}</td></tr>
  <tr><td>画像</td><td><img src="{{ product[3] }}"></td></tr>
  <tr><td>価格</td><td>{{ product[4] }}</td></tr>
  <tr><td>評価</td><td>{{ rate }}</td></tr>
  <tr>
    <td>コメント</td>
    <td>
      <ul style="list-style: none; padding-left: 0; margin-bottom: 0;">
      %for comment in comments:
        <li>{{ comment }}</li>
      %end
      </ul>
    </td>
  </tr>
</table>
<form action="/reviews" method="post">
  <p>あなたの評価<select name="rate">{{ !options }}</select></p>
%if my_comment is None:
  <p>あなたのコメント<input type="text" name="comment" /></p>
%else:
  <p>あなたのコメント<input type="text" name="comment" value="{{ my_comment }}" /></p>
%end
  <p><input type="submit" value="投稿" /></p>
  <input type="hidden" name="product_id" value="{{ product[0] }}" />
</form>
%if my_comment is not None:
<form action="/reviews" method="post">
  <input type="hidden" name="_method" value="delete" />
  <input type="hidden" name="product_id" value="{{ product[0] }}" />
  <input type="submit" value="削除" />
</form>
%end
''', nickname=nickname, product=product, rate=rate, comments=comments, my_comment=my_comment, options=options)

@route('/reviews', method='post')
def add_review():
    user_id = request.get_cookie("user_id", secret=SECRET_KEY)
    if user_id is None:
        redirect('/login?message=ログインしてください。')
    product_id = request.forms.product_id
    if product_id is None:
        abort(400, '該当する商品がありません。')
    if request.forms._method == 'delete':
        cur = conn.cursor()
        cur.execute('DELETE FROM reviews WHERE product_id = ? AND user_id = ?;', (product_id, user_id))
        conn.commit()
        return redirect('/products/' + product_id)
    rate = request.forms.rate
    if int(rate) < 1 or int(rate) > 5:
        abort(400, '評価の値が不正です。')
    comment = request.forms.comment
    if comment is None:
        comment = ''
    cur = conn.cursor()
    review = cur.execute('SELECT * FROM reviews r WHERE r.product_id = ? AND r.user_id = ?', (product_id, user_id)).fetchone()
    print(review)
    if review is None:
        cur.execute('INSERT INTO reviews(product_id, user_id, rate, comment) VALUES (?, ?, ?, ?)', (product_id, user_id, rate, comment))
        conn.commit()
    else:
        cur.execute('UPDATE reviews SET rate = ?, comment = ? WHERE product_id = ? AND user_id = ?', (rate, comment, product_id, user_id))
        conn.commit()
    redirect('/products/' + product_id)

run(host='localhost', port=8080, debug=True, reloader=True)