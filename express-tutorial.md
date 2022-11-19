# Expressの使い方

Webアプリ開発に慣れていない方向けに、使い方を説明します。慣れている方は、Linux Professional Institute (LPI) の課題に取り組んでみてください。

> 課題 035: NodeJSサーバープログラミング
> 
> https://learning.lpi.org/ja/learning-materials/030-100/035/

このページではWebセキュリティの解説で必要になる最低限の機能を紹介します。LPIの課題をベースにしています。

Windows上でWSL2を利用することが前提です。

## Step0: 事前準備

まずWSL2にnvm、node.js、npmをインストールし、Visual Studio Codeの拡張機能を設定します。

WSL 2 上で Node.js を設定する | Microsoft Learn
https://learn.microsoft.com/ja-jp/windows/dev-environment/javascript/nodejs-on-wsl

作業用のディレクトリ（ここでは express-tutorial とします）を作成し、必要なモジュールをインストールします。

```console
$ mkdir express-tutorial
$ cd express-tutorial
$ npm init --yes
$ npm install express
```

## Step1: ルーティング

```hello.js```というファイルを作り、次のコードを記述します。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080

app.get('/', (req, res) => {
  res.send('Hello World')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

次に、hello.js を起動します。

```console
$ node hello.js
Server ready at http://localhost:8080
```

Webブラウザーで次のURLにアクセスしてみましょう。Hello Worldと表示されます。

```
http://localhost:8080/
```

ここで、```app.get()```の最初のパラメーターを```'/'```から```'/hello'```に変更して、保存します。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080

app.get('/hello', (req, res) => {
  res.send('Hello World')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

もう一度、Webブラウザーで次のURLにアクセスしてみましょう。`Cannot GET /`と表示されます。

```
http://localhost:8080/
```

次に、Webブラウザーで次のURLにアクセスしてみましょう。Hello Worldと表示されます。

```
http://localhost:8080/hello
```

この動作から分かる通り、```/hello```にアクセスがあると、```app.get()```の2つ目の引数で設定された関数が実行されています。```app.get()```は、どのURLにHTTP GETでアクセスされると、どの関数を実行するのかを示しています。この機能をリクエストのルーティング（Routing）と呼びます。

なお、複数のURLと関数を関連付けることもできます。次のように記述すると、

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080

app.get(['/', '/hello'], (req, res) => {
  res.send('Hello World')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

どちらのURLにアクセスしても同じくHello Worldと表示されるようになります。

```
http://localhost:8080
http://localhost:8080/hello
```

## Step2: ダイナミックルーティング

次にダイナミックルーティングを試します。```app.get('/hello/:name', ...)```に変更します。これは、```/hello/```の後に入った文字列を、その次の関数に渡す変数```req.params.name```に格納しつつ、実行します。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080

app.get('/hello/:name', (req, res) => {
  // これは危険なコードです！ 
  res.send('Hello ' + req.params.name)
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

例えば、

```
http://localhost:8080/hello/世界
```

にアクセスすると、```Hello 世界```と表示されます。

なお、URLの末尾にスラッシュを一つ追加した

```
http://localhost:8080/hello/世界/
```

にアクセスしても、同じ結果になります。

ちなみに、これは危険なコードです。後で説明するクロスサイトスクリプティング（XSS）という脆弱性があります。この場合、スクリプトが混入したURLを作ることができ、そのURLにアクセスした人がスクリプトを自動的に実行し被害を受けてしまいます。

具体的には、次のURLにアクセスすると、アラートで```1```と表示されます。

```
http://localhost:8080/hello/<img src="1" onerror="alert(1);">
```

```\<img\>```タグがsrc属性に指定さ入れたURLから画像を取得しようとして失敗し、onerror属性のスクリプトを実行した結果です。```name```変数に入った情報をそのままページに表示するとHTMLタグとして認識されてしまいます。ここは、HTMLタグではなく単なる文字列として認識させるよう変換処理（エスケープ）が必要です。```\<```と```\>```を、それぞれ```&lt;```と```&gt;```に変換すれば大丈夫です。

うっかりするとエスケープ漏れが発生してしまいます。そこで、エスケープ漏れをなくすためにテンプレートを導入します。

## Step3: テンプレートエンジン（EJS）によるエスケープ

まず、新しいモジュール`EJS`をインストールします。

```console
$ npm i ejs
```

そして、```hello.js```を次のように修正します。```ejs```をrequireし、```ejs.render()```の第2パラメーターに```{ name: req.params.name }```を記述していることに注意してください。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')

app.get('/hello/:name', (req, res) => {
  res.send(ejs.render('Hello <%= name %>', { name: req.params.name }))
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

このように修正すれば、先ほどのスクリプト込みのURLにアクセスしてもJavaScriptは実行されず（アラートは表示されず）、画面にスクリプトが表示されるだけになります。

```
http://localhost:8080/hello/<img src="1" onerror="alert(1);">
```

XSSは非常に危険な脆弱性なので、テンプレートを使ったエスケープを忘れないようにしてください。

なお、テンプレートを使っても、`<%=`ではなく`<%-`を使うとエスケープされなくなります。これはとても危険な使い方ですのでくれぐれも注意してください。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')

app.get('/hello/:name', (req, res) => {
  // これは危険なコードです！ 
  res.send(ejs.render('Hello <%- name %>', { name: req.params.name }))
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

## Step4: テンプレート記法（Template Syntax）

テンプレートを使ってJavaScriptのロジックを実行することもできます。例えば、```name```を```count```回繰り返して表示する次のコードは、

```javascript
const name = '世界'
const count = 3
for(let i = 0; i < count; i++) {
    console.log(name)
}
```

テンプレート記法を使うと次のように記述できます。

```
<% for (let i = 0; i < count; i++) { %>
    <%= name %>
<% } %>
```

これをWebアプリとして実装し、URLでnameとcountを渡すようにすると、```hello.js```は次のようになります。URLの```count```は文字列なので```int(count)```で整数に変換しています。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')

app.get('/hello/:name/:count', (req, res) => {
  res.send(ejs.render(`
<% for (let i = 0; i < count; i++) { %>
    <%= name %>
<% } %>`,
  {
    name: req.params.name,
    count: req.params.count
  }))
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

## Step5: クエリー変数（Query variables）

ルーティングとは別の方法で、URLで指定した値をWebアプリに渡す方法があります。それがクエリー変数（クエリーパラメーター）です。

例えば、このURLでは、クエリー変数として```name```と```count```を使っています。

```
http://localhost:8080/hello?name=世界&count=3
```

Webアプリでこれを参照するには、```req.query```を使います。GETリクエストを受け付けるURLを`/hello`に戻し、`req.params`を`req.query`にすべて変換します。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')

app.get('/hello', (req, res) => {
  res.send(ejs.render(`
<% for (let i = 0; i < count; i++) { %>
    <%= name %>
<% } %>`,
  {
    name: req.query.name,
    count: req.query.count
  }))
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

## Step6: フォーム（Form）

HTMLのフォーム経由でWebアプリに値を渡す方法です。フォームではHTTPのGETメソッド、POSTメソッドが使えます。GETメソッドを使う場合はクエリー変数と同じになるので割愛し、POSTメソッドを使う場合を紹介します。

フォームを使うときの定石は、RESTでいうリソースのURLにGETメソッド・POSTメソッドでそれぞれアクセスがあった場合の動作を変えておくことです。

- GETでアクセス
  - WebアプリはフォームのHTMLを返却する
- POSTでアクセス
  - Webアプリは値を使って処理をして、処理結果を返却する

POSTメソッドで受け取ったデータは、`req.body`で取得できます。ただし、```app.use(express.urlencoded({ extended: true }))```を宣言しておく必要があります。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')

app.use(express.urlencoded({ extended: true }))

app.get('/hello', (req, res) => {
  res.send(`
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" /></p>
  <p>回数 <input type="text" name="count" /></p>
  <p><input type="submit"/>
 </form>`)
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  const count = req.body.count
  res.send(ejs.render(`
<% for (let i = 0; i < count; i++) { %>
    <%= name %>
<% } %>`,
  { name, count }))
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

## Step7: クッキー（Cookie）

クライアント側に情報を保持させるのに使うのがクッキーです。とても便利な機能なのですが、暗号化せずに扱うと情報が漏れてしまうので取り扱いに注意が必要です。

クッキーにはkeyとvalueのペアを保存できます。
Expressでクッキーを扱うには、新しいモジュール`cookie-parser`をインストールして、
```javascript
const cookieParser = require('cookie-parser')
app.use(cookieParser())
```
を実行します。

Webアプリでクッキーの値を参照するには、```req.cookies.<key名>```を使います。
一方、クッキーに値を保存するには、```res.cookie('<key名>', '<value値>')```を使います。参照には```req```で複数形の```cookies```を、保存には```res```で単数形の```cookie```を使っていることに注意してください。

...とここまで書いて、日本語をクッキーに保存する場合は注意が必要のようです。

参照には```request.cookies.decode().get('<key名>')```を使う必要があります。

> Python + Bottleで、フォームやCookieに日本語を設定したら文字化けした
> 
> https://thinkami.hatenablog.com/entry/2017/04/09/180835

POSTでフォームから受け取った値を処理した後は```res.redirect('/hello')```でURL```/hello```にリダイレクトさせます（GETメソッドでアクセスさせます）。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
app.use(cookieParser())

app.get('/hello', (req, res) => {
  const name = req.cookies.name
  res.send(ejs.render(`
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" value="<%= name %>"/></p>
  <p><input type="submit"/>
 </form>`, { name }))
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  res.cookie('name', name)
  res.redirect('/hello')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

Webブラウザーの開発者ツールDevToolsのApplicationタブから、保存したCookieの値を確認できます。

さて、```res.cookie()```で何のオプションも指定しないと、クライアントで実行するJavaScriptからクッキーの値が丸見えになります。

例えば、クエリー変数で渡したメッセージを画面に表示する機能を追加した時、うっかりメッセージをエスケープし忘れてXSSの脆弱性が埋め込まれてしまったとします。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
app.use(cookieParser())

app.get('/hello', (req, res) => {
  const name = req.cookies.name
  const message = req.query.message
  // これは危険なコードです！
  res.send(ejs.render(`
<p><%- message %></p>
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" value="<%= name %>"/></p>
  <p><input type="submit"/>
 </form>`, { name, message }))
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  res.cookie('name', name)
  res.redirect('/hello')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

この時、

```
http://localhost:8080/hello?message=こんにちは
```

であれば画面に、こんにちは、と表示されるだけですが、次のURLの場合はCookieのkeyとvalueがアラートに表示されてしまいます。

```
http://localhost:8080/hello?message=<script>alert(document.cookie)</script>
```

このスクリプトではアラートに表示するだけですが、JavaScriptを工夫して別のサイトに送信してしまえば、クライアントのWebブラウザーで管理していた情報が外部に漏れてしまいます。

JavaScriptからクッキーにアクセスできないようにするには、httponly属性を設定します。```res.cookie('<key名>', '<value値>', { httpOnly: true })```で使えます。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
app.use(cookieParser())

app.get('/hello', (req, res) => {
  const name = req.cookies.name
  const message = req.query.message
  // これは危険なコードです！
  res.send(ejs.render(`
<p><%- message %></p>
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" value="<%= name %>"/></p>
  <p><input type="submit"/>
 </form>`, { name, message }))
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  res.cookie('name', name, { httpOnly: true })
  res.redirect('/hello')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

一度ブラウザーで`http://localhost:8080/hello`にアクセスしてクッキーに保存しなおします。その上で、

```
http://localhost:8080/hello?message=<script>alert(document.cookie)</script>
```

にアクセスすると（XSSの脆弱性は修正していないのでアラートは表示されますが）クッキーの内容は表示されなくなりました。JavaScriptからクッキーにアクセスできなくなったためです。

他のクッキー属性についてもぜひ確認してみてください。

> https://www.npmjs.com/package/cookie

## Step8: 署名付きクッキー（Signed cookie）

クッキーを保存するときに電子署名をつけることで、クッキーの改ざんを防ぐことができます。もし改ざんされると、そのクッキーは不正な値となり、読み取りに失敗します（falseになります）。

署名付きクッキーを使うのには少し手間がかかります。

1. ミドルウェアを設定するときに```app.use(cookieParser(<署名の鍵となる文字列>))```とする。
2. クッキーを保存するときにオプションで`{ signed: true }`を与える。
3. クッキーを読むときに、`req.cookies`ではなく`req.signedCookies`を利用する。

Step7のコードを書き換えて、ミドルウェアで署名の鍵となる文字列を設定します。
DevToolsを使うと、クッキーの値の前後に、電子署名の文字列が付加されていることが分かります。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
// 署名の鍵を直接コーディングするのは危険です！
app.use(cookieParser('himitu_no_mojiretsu'))

app.get('/hello', (req, res) => {
  const name = req.signedCookies.name
  const message = req.query.message
  // これは危険なコードです！
  res.send(ejs.render(`
<p><%- message %></p>
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" value="<%= name %>"/></p>
  <p><input type="submit"/>
 </form>`, { name, message }))
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  res.cookie('name', name, { httpOnly: true, signed: true })
  res.redirect('/hello')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

署名の鍵となる文字列は秘密にしておく必要があります。直接ソースコードに書くのではなく、環境変数として設定をしてそれを読み込んで使うようにしてください。

Windowsのコマンドプロンプトで環境変数を設定するには、

```console
> set 環境変数名=環境変数の値
```

Ubuntuの場合は、

```console
$ export 環境変数名=環境変数の値
```

を使います。

node.jsで環境変数を読み込むには```process.env.<環境変数名>```で参照します。
環境変数名を```SECURE_KEY```にした時のコードは次の通りです。

```javascript
const express = require('express')
const app = express()
const host = 'localhost'
const port = 8080
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
const SECURE_KEY = process.env.SECURE_KEY
if (!SECURE_KEY) throw '環境変数SECURE_KEYが設定されていません。'
app.use(cookieParser(SECURE_KEY))

app.get('/hello', (req, res) => {
  const name = req.signedCookies.name
  const message = req.query.message
  // これは危険なコードです！
  res.send(ejs.render(`
<p><%- message %></p>
<form action="/hello" method="post">
  <p>名前 <input type="text" name="name" value="<%= name %>"/></p>
  <p><input type="submit"/>
 </form>`, { name, message }))
})

app.post('/hello', (req, res) => {
  const name = req.body.name
  res.cookie('name', name, { httpOnly: true, signed: true })
  res.redirect('/hello')
})

app.listen(port, host, () => {
  console.log(`Server ready at http://${host}:${port}`)
})
```

## Step9: データベース

npmで`sqlite3`モジュールをインストールすると、sqlite3が使えます。ただし CLI はインストールされていません。SQLをREPLで入力しながら確かめるにはCLIを別途インストールする必要があるので注意してください。

> sqlite3 --- SQLite データベースに対する DB-API 2.0 インタフェース
> 
> https://docs.python.org/ja/3/library/sqlite3.html

特に、プレイスホルダー（placeholder）の使い方は必読です。使わないととても危険なコードになってしまいます。

データベースの使い方はLPIの課題で練習してみてください。

> 課題 035: NodeJSサーバープログラミング > 035.3 SQLの基本 > 035.3 レッスン 1
> 
> https://learning.lpi.org/ja/learning-materials/030-100/035/035.3/035.3_01/

[戻る](web-application-framework.md) | [次へ](/README.md)
