# Webセキュリティの基礎知識

## 情報セキュリティとは

情報セキュリティとは、情報の機密性、完全性、可用性を確保することです。

> 情報セキュリティって何？｜はじめに｜国民のための情報セキュリティサイト
> 
> https://www.soumu.go.jp/main_sosiki/joho_tsusin/security/intro/security/index.html

> 情報セキュリティの要素🍡機密性,完全性,可用性とは？／ITパスポート・基本情報技術者・高校情報 6:50
> https://www.youtube.com/watch?v=wmZtWlUEhkc
> 
> [![](http://img.youtube.com/vi/wmZtWlUEhkc/0.jpg)](http://www.youtube.com/watch?v=wmZtWlUEhkc "")

## 情報セキュリティへの脅威が与える社会的影響

情報技術の活用が進めば、それを狙った新たな脅威も生まれます。独立行政法人 情報処理推進機構（IPA）は毎年1月に前年の情報セキュリティ10大脅威を公開しています。

> 情報セキュリティ10大脅威 | IPA 独立行政法人 情報処理推進機構
> 
> https://www.ipa.go.jp/security/10threats/index.html

10大脅威は個人と組織でそれぞれ発表されます。2020年に個人で最も社会的影響が大きかったのは「スマホ決済の不正利用」です。

発端はスマホ決済サービス「7pay」です。2019年7月1日にサービスを開始したのち、多額の不正利用が発生したことで、わずか1カ月後にはサービス廃止を発表しました。

> 7payの不正利用についてまとめてみた - piyolog
> 
> https://piyolog.hatenadiary.jp/entry/2019/07/04/065925

また「ドコモ口座」の不正利用の被害も発生しています。

> ＜仕組みを解説＞ドコモ不正出金：ドコモユーザー以外でも被害の可能性【news23】9:19
>
> http://www.youtube.com/watch?v=bnBLXW21G7Y
>
> [![](http://img.youtube.com/vi/bnBLXW21G7Y/0.jpg)](http://www.youtube.com/watch?v=bnBLXW21G7Y "")

情報セキュリティの確保はビジネス上の最優先事項となりました。情報セキュリティの事案は複合的な要素が絡み合っていますが、ここから先は技術的脅威、特にWebアプリにまつわる情報セキュリティ（Webセキュリティ）について紹介します。

## 不正ログインの手法

不正ログインが防げないとWebアプリを守ることはできません。次の動画では、不正ログインの代表的な6つの手法を紹介しています。

> 不正ログイン手法入門（初級編）15:01
>
> http://www.youtube.com/watch?v=AwBAwHy5Qps
>
> [![](http://img.youtube.com/vi/AwBAwHy5Qps/0.jpg)](http://www.youtube.com/watch?v=AwBAwHy5Qps "")

- パスワード推測
- ブルートフォース攻撃
- 辞書攻撃
- リバースブルートフォース攻撃
- パスワードスプレイ攻撃
- パスワードリスト攻撃

## 脆弱性を狙った攻撃

技術的脅威の一つが脆弱性（および、その脆弱性を狙った攻撃）です。脆弱性とはプログラムの不具合や設計上のミスが原因となって発生した情報セキュリティ上の欠陥のことで、セキュリティホールとも呼ばれます。

> 脆弱性（ぜいじゃくせい）とは？｜どんな危険があるの？｜基礎知識｜国民のための情報セキュリティサイト
> 
> [https://www.soumu.go.jp/main_sosiki/joho_tsusin/security/basic/risk/11.html](https://www.soumu.go.jp/main_sosiki/joho_tsusin/security/basic/risk/11.html#:~:text=%E8%84%86%E5%BC%B1%E6%80%A7%EF%BC%88%E3%81%9C%E3%81%84%E3%81%98%E3%82%83%E3%81%8F%E3%81%9B%E3%81%84%EF%BC%89%E3%81%A8%E3%81%AF%E3%80%81%E3%82%B3%E3%83%B3%E3%83%94%E3%83%A5%E3%83%BC%E3%82%BF%E3%81%AEOS,%E3%81%AE%E3%81%93%E3%81%A8%E3%82%92%E8%A8%80%E3%81%84%E3%81%BE%E3%81%99%E3%80%82&text=%E8%84%86%E5%BC%B1%E6%80%A7%E3%81%8C%E6%AE%8B%E3%81%95%E3%82%8C,%E3%81%99%E3%82%8B%E5%8D%B1%E9%99%BA%E6%80%A7%E3%81%8C%E3%81%82%E3%82%8A%E3%81%BE%E3%81%99%E3%80%82)

Webアプリの代表的な脆弱性10種について、IPAが解説しています。

> 知っていますか？脆弱性 （ぜいじゃくせい）：IPA 独立行政法人 情報処理推進機構
> 
> https://www.ipa.go.jp/security/vuln/vuln_contents/index.html

- SQLインジェクション
- クロスサイト・スクリプティング (XSS)
- CSRF（クロスサイト・リクエスト・フォージェリ）
- パス名パラメータの未チェック / ディレクトリ・トラバーサル
- OSコマンド・インジェクション
- セッション管理の不備
- HTTPヘッダ・インジェクション
- HTTPSの不適切な利用
- サービス運用妨害（DoS）
- メール不正中継

この後、SQLインジェクション、XSS、CSRFと、さらに追加でクリックインジェクションについて実例を使って解説します。

解説は、ローカル環境に起動したサーバーに攻撃をすることで確認します。なお、他人のシステムに攻撃をすることは犯罪です。絶対にしないでください。

[戻る](/README.md) | [次へ](/web-application-framework.md)
