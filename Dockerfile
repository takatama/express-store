# Node.jsのイメージをベースにする
FROM node:22

# nodemonをグローバルにインストール
RUN npm install -g nodemon

# アプリケーションディレクトリを作成
WORKDIR /usr/src/app

# アプリケーションの依存関係をインストール
COPY package*.json ./
RUN npm install

# アプリケーションのソースをコピー
COPY . .

# 各スクリプトのためのポートを開放
EXPOSE 8080
EXPOSE 8081

# app.db, evil.db を初期化
RUN node setup.js

# コンテナ起動時にapp.jsを実行
CMD ["nodemon", "app.js"]
