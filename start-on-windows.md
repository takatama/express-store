## デモのはじめかた（Docker）

まずWSL2にnvm、node.js、npmをインストールし、Visual Studio Codeの拡張機能を設定します。

WSL 2 上で Node.js を設定する | Microsoft Learn
https://learn.microsoft.com/ja-jp/windows/dev-environment/javascript/nodejs-on-wsl

ソースコードを clone します。

```console
$ git clone https://github.com/takatama/express-store.git
$ cd express-store
```

必要なモジュールをインストールします。

```console
$ npm install
```

データベースを初期化します。データベースのファイル```app.db```と```evil.db```が作成されます。

```console
$ node setup.js
```

署名付きcookieのための鍵を環境変数```SECRET_KEY```に設定します。適当な文字列で構いません。

```console
$ export SECRET_KEY=<署名付きcookieのための鍵（文字列）>
```

ECサイトを起動します。localhost:8080で立ち上がります。環境変数を設定し忘れていると、例外が発生して起動できないのでご注意ください。nodemonを使い、ソースコードを修正すると自動で再起動させています。

```console
$ npx nodemon app.js
```