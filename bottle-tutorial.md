# Bottleの使い方

Webアプリ開発に慣れていない方向けに、使い方を説明します。慣れている方は、公式のチュートリアルを試してください。

> Tutorial: Todo-List Application — Bottle 0.13-dev documentation
> 
> https://bottlepy.org/docs/dev/tutorial_app.html

このページではWebセキュリティの解説で必要になる最低限の機能を紹介します。https://bottlepy.org/docs/dev/tutorial.html からの抜粋です。

Windowsを利用することが前提です。

## Step0: 事前準備

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
(venv)> pip install bottle
```

## Step1: ルーティング

```hello.py```というファイルを作り、次のコードを記述します。

```python
from bottle import route, run

@route('/')
def hello():
    return 'Hello World'

run(host='localhost', port=8080, reloader=True)
```

次に、hello.py を起動します。

```console
(venv)> py hello.py
Bottle v0.12.19 server starting up (using WSGIRefServer())...
Listening on http://localhost:8080/
Hit Ctrl-C to quit.

```

Webブラウザーで次のURLにアクセスしてみましょう。Hello Worldと表示されます。

```
http://localhost:8080/
```

コンソールにはWebブラウザーからのアクセスがあるたびに、アクセスログが追記されます。

```console
127.0.0.1 - - [14/Jan/2021 22:38:59] "GET / HTTP/1.1" 200 11
```

ここで、```@route```のパラメーターを```'/'```から```'/hello'```に変更して、保存します。

```python
from bottle import route, run

@route('/hello')
def hello():
    return 'Hello World'

run(host='localhost', port=8080, reloader=True)
```

もう一度、Webブラウザーで次のURLにアクセスしてみましょう。404 Not Foundと表示されます。

```
http://localhost:8080/
```

次に、Webブラウザーで次のURLにアクセスしてみましょう。Hello Worldと表示されます。

```
http://localhost:8080/hello
```

この動作から分かる通り、```/hello```にアクセスがあると、```hello()```が実行されています。```@route```は、どのURLにアクセスがあると、どの関数を実行するのかを示しています。この機能をリクエストのルーティング（Routing）と呼びます。

なお、複数のURLと関数を関連付けることもできます。次のように記述すると、

```python
from bottle import route, run

@route('/')
@route('/hello')
def hello():
    return 'Hello World'

run(host='localhost', port=8080)
```

どちらのURLにアクセスしても同じくHello Worldと表示されるようになります。

```
http://localhost:8080
http://localhost:8080/hello
```

## Step2: ダイナミックルーティング

次にダイナミックルーティングを試します。```@route('/hello/<name>')```に変更します。これは、```/hello/```の後に入った文字列を、変数```name```に格納しつつ、関数hello()を実行します。この時、```def hello(name)```と、パラメーターに```name```を追加することで、関数の中で```name```を参照できるようになります。

```python
from bottle import route, run

@route('/hello/<name>')
def hello(name):
    # これは危険なコードです！
    return 'Hello ' + name

run(host='localhost', port=8080, reloader=True)
```

例えば、

```
http://localhost:8080/hello/世界
```

にアクセスすると、```Hello 世界```と表示されます。

しかし、URLの末尾にスラッシュを一つ追加した

```
http://localhost:8080/hello/世界/
```

にアクセスしても、404 Not Found になり、```@route('/hello/<name>')```にはマッチしないことに注意してください。

ちなみに、これは危険なコードです。後で説明するクロスサイトスクリプティング（XSS）という脆弱性があります。この場合、スクリプトが混入したURLを作ることができ、そのURLにアクセスした人がスクリプトを自動的に実行し被害を受けてしまいます。

具体的には、次のURLにアクセスすると、アラートで```1```と表示されます。

```
http://localhost:8080/hello/<img src="1" onerror="alert(1);">
```

```\<img\>```タグがsrc属性に指定さ入れたURLから画像を取得しようとして失敗し、onerror属性のスクリプトを実行した結果です。```name```変数に入った情報をそのままページに表示するとHTMLタグとして認識されてしまいます。ここは、HTMLタグではなく単なる文字列として認識させるよう変換処理（エスケープ）が必要です。```\<```と```\>```を、それぞれ```&lt;```と```&gt;```に変換すれば大丈夫です。

うっかりするとエスケープ漏れが発生してしまいます。そこで、エスケープ漏れをなくすためにテンプレートを導入します。

## Step3: テンプレート（Template）によるエスケープ

```hello.py```を次のように修正します。```import```に```template```を増やしていることと、```template()```のパラメーターに```name=name```を記述していることに注意してください。

```python
from bottle import route, run, template

@route('/hello/<name>')
def hello(name):
    return template('Hello {{ name }}', name=name)

run(host='localhost', port=8080, reloader=True)
```

このように修正すれば、先ほどのスクリプト込みのURLにアクセスしてもJavaScriptは実行されず（アラートは表示されず）、画面にスクリプトが表示されるだけになります。

```
http://localhost:8080/hello/<img src="1" onerror="alert(1);">
```

XSSは非常に危険な脆弱性なので、テンプレートを使ったエスケープを忘れないようにしてください。

なお、テンプレートを使っても、変数の前に```!```（エクスクラメーションマーク）を記述するとエスケープされなくなります。これはとても危険な使い方ですのでくれぐれも注意してください。

```python
from bottle import route, run, template

@route('/hello/<name>')
def hello(name):
    # これは危険なコードです！
    return template('Hello {{ !name }}', name=name)

run(host='localhost', port=8080, reloader=True)
```

## Step4: テンプレート記法（Template Syntax）

テンプレートを使ってPythonのロジックを実行することもできます。例えば、```name```を```count```回繰り返して表示する次のコードは、

```python
name='世界'
count=3
for i in range(count):
    print(name)
```

テンプレート記法を使うと次のように記述できます。

```
%for i in range(count)
    {{ name }}
%end
```

これをWebアプリとして実装し、URLでnameとcountを渡すようにすると、```hello.py```は次のようになります。URLの```count```は文字列なので```int(count)```で整数に変換しています。

```python
from bottle import route, run, template

@route('/hello/<name>/<count>')
def hello(name, count):
    return template('''
        %for i in range(int(count)):
          {{ name }}
        %end
    ''', name=name, count=count)

run(host='localhost', port=8080, reloader=True)
```

## Step5: クエリー変数（Query variables）

ルーティングとは別の方法で、URLで指定した値をWebアプリに渡す方法があります。それがクエリー変数（クエリーパラメーター）です。

例えば、このURLでは、クエリー変数として```name```と```count```を使っています。

```
http://localhost:8080/hello?name=世界&count=3
```

Webアプリでこれを参照するには、```request.query```を使います。```import```に```request```を追加しています。```def hello()```は引数を削除しています。

なお```'''```はPythonのヒアドキュメントです。

```python
from bottle import route, run, template, request

@route('/hello')
def hello():
    name = request.query.name
    count = request.query.count
    return template('''
        %for i in range(int(count)):
          {{ name }}
        %end
    ''', name=name, count=count)

run(host='localhost', port=8080, reloader=True)
```

## Step6: フォーム（Form）

HTMLのフォーム経由でWebアプリに値を渡す方法です。フォームではHTTPのGETメソッド、POSTメソッドが使えます。GETメソッドを使う場合はクエリー変数と同じになるので割愛し、POSTメソッドを使う場合を紹介します。

フォームを使うときの定石は、RESTでいうリソースのURLにGETメソッド・POSTメソッドでそれぞれアクセスがあった場合の動作を変えておきます。

- GETでアクセス
  - WebアプリはフォームのHTMLを返却する
- POSTでアクセス
  - Webアプリは値を使って処理をして、処理結果を返却する

フォームの値には、クエリー変数にアクセスするときに使った```request```を利用します。

```python
from bottle import route, run, template, request

@route('/hello', method='get')
def show_form():
    return '''
        <form action="/hello" method="post">
            <p>名前 <input type="text" name="name" /></p>
            <p>回数 <input type="text" name="count" /></p>
            <p><input type="submit"/>
        </form>'''

@route('/hello', method='post')
def hello():
    name = request.forms.name
    count = request.forms.count
    return template('''
        %for i in range(int(count)):
          {{ name }}
        %end
    ''', name=name, count=count)

run(host='localhost', port=8080, reloader=True)
```

## Step7: クッキー（Cookie）

クライアント側に情報を保持させるのに使うのがクッキーです。とても便利な機能なのですが、暗号化せずに扱うと情報が漏れてしまうので取り扱いに注意が必要です。

クッキーにはkeyとvalueのペアを保存できます。

Webアプリでクッキーの値を参照するには、```request.get_cookie('<key名>')```を使います。
一方、クッキーに値を保存するには、```response.set_cookie('<key名>', '<value値>')```を使います。参照には```request```を、保存には```response```を使っていることに注意してください。

...とここまで書いて、日本語をクッキーに保存する場合は注意が必要のようです。

参照には```request.cookies.decode().get('<key名>')```を使う必要があります。

> Python + Bottleで、フォームやCookieに日本語を設定したら文字化けした
> 
> https://thinkami.hatenablog.com/entry/2017/04/09/180835

変更したコードでは```import```に```response```を追加しています。また```redirect```も追加しています。POSTでフォームから受け取った値を処理した後は```redirect()```で```/hello```にGETでアクセスさせます。

```python
from bottle import route, run, template, request, response, redirect

@route('/hello', method='get')
def show_form():
    name = request.cookies.decode().get('name')
    return template('''
        <form action="/hello" method="post">
            <p>名前 <input type="text" name="name" value="{{ name }}"/></p>
            <p><input type="submit" value="保存"/>
        </form>''', name=name)

@route('/hello', method='post')
def hello():
    name = request.forms.decode().get('name')
    response.set_cookie('name', name)
    redirect('/hello')

run(host='localhost', port=8080, reloader=True)
```

Webブラウザーの開発者ツールDevToolsのApplicationタブから、保存したCookieの値を確認できます。

さて、```set_cookie()```で何のオプションも指定しないと、クライアントで実行するJavaScriptからクッキーの値が丸見えになります。

例えば、クエリー変数で渡したメッセージを画面に表示する機能を追加した時、うっかりメッセージをエスケープし忘れてXSSの脆弱性が埋め込まれてしまったとします。

```python
from bottle import route, run, template, request, response, redirect

@route('/hello', method='get')
def show_form():
    name = request.cookies.decode().get('name')
    message = request.query.message
    # これは危険なコードです！
    return template('''
        <p>{{ !message }}</p>
        <form action="/hello" method="post">
            <p>名前 <input type="text" name="name" value="{{ name }}"/></p>
            <p><input type="submit" value="保存"/>
        </form>''', name=name, message=message)

@route('/hello', method='post')
def hello():
    name = request.forms.decode().get('name')
    response.set_cookie('name', name)
    redirect('/hello')

run(host='localhost', port=8080, reloader=True)
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

JavaScriptからクッキーにアクセスできないようにするには、httponly属性を設定します。```request.set_cookie('<key名>', '<value値>', httponly=True)```として使います。

```python
from bottle import route, run, template, request, response, redirect

@route('/hello', method='get')
def show_form():
    name = request.cookies.decode().get('name')
    message = request.query.message
    # これは危険なコードです！
    return template('''
        <p>{{ !message }}</p>
        <form action="/hello" method="post">
            <p>名前 <input type="text" name="name" value="{{ name }}"/></p>
            <p><input type="submit" value="保存"/>
        </form>''', name=name, message=message)

@route('/hello', method='post')
def hello():
    name = request.forms.decode().get('name')
    response.set_cookie('name', name, httponly=True)
    redirect('/hello')

run(host='localhost', port=8080, reloader=True)
```

XSSの脆弱性は修正していないので、いまだに

```
http://localhost:8080/hello?message=<script>alert(document.cookie)</script>
```

でアクセスするとアラートは表示されますが、その中身（クッキーの内容）は表示されなくなりました。JavaScriptからクッキーにアクセスできなくなったためです。

他のクッキー属性についてもぜひ確認してみてください。

> https://bottlepy.org/docs/dev/tutorial.html#cookies

## Step8: 署名付きクッキー（Signed cookie）

クッキーを保存するときに電子署名をつけることで、クッキーの改ざんを防ぐことができます。
```response.set_cookie('<key名>', '<value値>', secure='<署名の鍵となる文字列>')```で使うことができます。署名の鍵となる文字列は秘密にしておく必要があります。直接ソースコードに書くのではなく、環境変数として設定をしてそれを読み込んで使うようにしてください。

Windowsのコマンドプロンプトで環境変数を設定するには、

```console
> set 環境変数名=環境変数の値
```

Pythonで環境変数を読み込むには```from os import environ```をして、```environ.get('<環境変数名>')```で参照します。

DevToolsを使うと、クッキーの値がそのままでは判別できなくなっていることが分かります。

## Step9: データベース

Pythonをインストールすると、sqlite3が使えます。ただし CLI はインストールされていません。SQLをREPLで入力しながら確かめるにはCLIを別途インストールする必要があるので注意してください。

> sqlite3 --- SQLite データベースに対する DB-API 2.0 インタフェース
> 
> https://docs.python.org/ja/3/library/sqlite3.html

ここまで理解できれば、公式のチュートリアルを試すことができると思います。ぜひ挑戦してみてください。

> Tutorial: Todo-List Application — Bottle 0.13-dev documentation
> 
> https://bottlepy.org/docs/dev/tutorial_app.html

[次へ](/README.md) | [戻る](web-application-framework.md)
