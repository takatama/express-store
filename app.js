const express = require('express')
const ejs = require('ejs')
const cookieParser = require('cookie-parser')
const sqlite3 = require('sqlite3')
const bcrypt = require('bcrypt')

const HOST = '0.0.0.0'
const PORT = 8080
const SECRET_KEY = process.env.SECRET_KEY
if (!SECRET_KEY) throw '環境変数 SECRET_KEY が設定されていません。'
const DATABASE_FILE = 'app.db'
const db = new sqlite3.Database(DATABASE_FILE)
sqlite3.verbose()

const app = express()
app.use(express.urlencoded({ extended: true }))
app.use(cookieParser(SECRET_KEY))
app.use((req, res, next) => {
    // Step5: Clickjacking対策
    res.header('X-Frame-Options', 'DENY')
    next()
})

app.get('/', (req, res) => {
    res.redirect('/products')
})

app.get('/login', (req, res) => {
    res.send(ejs.render(`
<h1>ログイン</h1>
<!-- Step2: XSS対策 -->
<p style="color:red;"><%= message %></p>
<form action="/login" method="post">
<p>メールアドレス <input name="email" type="text" placeholder="user1@example.com" value="user1@example.com" /></p>
<p>パスワード <input name="password" type="password" placeholder="password1" value="password1" /></p>
<p><input value="ログイン" type="submit" /></p>
</form>`, { message: req.query.message }))
})

function isValidPassword(userPassword, hashedPassword) {
    return bcrypt.compareSync(userPassword, hashedPassword)
}

app.post('/login', (req, res) => {
    const email = req.body.email
    const password = req.body.password
    db.get('SELECT hashed_password, id, nickname FROM users WHERE email = ?;', email, (err, row) => {
        if (isValidPassword(password, row.hashed_password)) {            
            // Step3: CSRF対策
            res.cookie('userId', row.id, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'lax' })
            res.cookie('nickname', row.nickname, { signed: true, path: '/', httpOnly: true, secure: true, sameSite: 'lax' })
            return res.redirect('/products')
        }
        console.log('Login failed: Invalid password for email ' + email);
        return res.redirect('/login?message=ログインに失敗しました。')
    })
})
 
app.get('/logout', (req, res) => {
    res.clearCookie('userId', { path: '/' })
    res.clearCookie('nickname', { path: '/' })
    res.redirect('/login?message=ログアウトしました。')
})

function productsHtml(nickname, products, query) {
    return ejs.render(`
<p>ようこそ、<%= nickname %>さん（<a href="/logout">ログアウト</a>）</p>
<h1>商品一覧</h1>
<form action="/products" method="get">
  <p>商品名で検索 <input type="text" name="q" value="<%= query %>" /><input type="submit" value="検索" />
</form>
<table border="1">
  <tr>
    <th>商品名</th><th>説明</th><th>画像</th><th>価格</th><th>評価</th><th>操作</th>
  </tr>
  <% for (let p of products) { %>
  <tr>
    <td><%= p.name %></td><td><%= p.description %></td><td><img src="<%= p.image_url %>"</td><td><%= p.price_yen %>円</td><td><%= p.description %></td><td><p><a href="/products/<%= p.id %>">詳細</a></p><p><a href="#" onclick="alert('<%= p.name %>を購入しました')">購入</a></p></td>
  </tr>
  <% } %>
</table>
    `, { nickname, products, query })
}

app.get('/products', (req, res) => {
    const nickname = req.signedCookies.nickname
    if (!nickname) {
        return res.redirect('/login?message=ログインしてください。')
    }
    const query = req.query.q
    if (query) {
        // Step1: SQLインジェクション対策
        db.all("SELECT * FROM rated_products WHERE name LIKE ?;", "%" + query + "%", (err, rows) => {
            return res.send(productsHtml(nickname, rows, query))
        })
    } else {
        db.all('SELECT * FROM rated_products;', (err, rows) => {
            return res.send(productsHtml(nickname, rows))
        })
    }
})

function productHtml(nickname, product, rate, comments, myRate, myComment) {
    return ejs.render(`
<p>ようこそ、<%= nickname %>さん（<a href="/logout">ログアウト</a>）</p>
<h1><a href="/products">商品一覧</a> > <%= product.name %></h1>
<table border="1">
<tr><th>項目</th><th>内容</th></tr>
<tr><td>商品名</td><td><%= product.name %></td></tr>
<tr><td>説明</td><td><%= product.description %></td></tr>
<tr><td>画像</td><td><img src="<%= product.image_url %>"></td></tr>
<tr><td>価格</td><td><%= product.price_yen %>円</td></tr>
<tr><td>評価</td><td><%= rate %></td></tr>
<tr>
<td>コメント</td>
<td>
    <ul style="list-style: none; padding-left: 0; margin-bottom: 0;">
    <% for (let comment of comments) { %>
    <!-- Step4: XSS対策 -->
    <li><%= comment %></li>
    <% } %>
    </ul>
</td>
</tr>
</table>
<p><button onclick="alert('<%= product.name %> を購入しました。')">購入</button></p>
<form action="/reviews" method="post">
<p>あなたの評価
<select name="rate">
<% for (let i = 5; i >= 1; i--) { %>
    <% if ( i == myRate ) { %>
        <option value="<%= i %>" selected><%= i %></option>
    <% } else { %>
        <option value="<%= i %>"><%= i %></option>
    <% } %>
<% } %>
</select>
</p>
<% if (myComment) { %>
  <p>あなたのコメント<input type="text" name="comment" value="<%= myComment %>" /></p>
<% } else { %>
  <p>あなたのコメント<input type="text" name="comment" /></p>
<% } %>
<p><input type="submit" value="投稿" /></p>
<input type="hidden" name="product_id" value="<%= product.id %>" />
</form>
<% if (myComment !== undefined) { %>
<form action="/reviews" method="post">
<input type="hidden" name="_method" value="delete" />
<input type="hidden" name="product_id" value="<%= product.id %>" />
<input type="submit" value="削除" />
</form>
<% } %>`, { nickname, product, rate, comments, myRate, myComment })
}

app.get('/products/:productId', (req, res) => {
    const productId = req.params.productId
    const nickname = req.signedCookies.nickname
    if (!nickname) {
        return res.redirect('/login?message=ログインしてください。')
    }
    const userId = req.signedCookies.userId
    db.get('SELECT * FROM products WHERE id = ?;', productId, (err, product) => {
        if (!product) {
            return res.status(400).send('該当する商品がありません。')
        }
        db.all('SELECT r.rate, r.comment, u.id, u.nickname FROM reviews r JOIN users u ON r.product_id = ? AND r.user_id = u.id;', productId, (req, reviews) => {
            let rate = 0
            const comments = []
            let myComment, myRate
            for (let review of reviews) {
                rate += review.rate
                comments.push('【★' + review.rate + '】' + review.comment + ' (' + review.nickname + ')')
                if (review.id === Number(userId)) {
                    myRate = review.rate
                    myComment = review.comment
                }
            }
            if (rate > 0) {
                rate = Math.round(rate / reviews.length, 1)
            } else {
                rate = '無し'
            }
            res.send(productHtml(nickname, product, rate, comments, myRate, myComment))
        })    
    })
})

app.post('/reviews', (req, res) => {
    const userId = req.signedCookies.userId
    if (!userId) {
        return res.redirect('/login?message=ログインしてください。')
    }
    const productId = req.body.product_id
    if (!productId) {
        return res.status(400).send('該当する商品がありません。')
    }
    if (req.body._method === 'delete') {
        return db.run('DELETE FROM reviews WHERE product_id = ? AND user_id = ?;', productId, userId, (err, row) => {
            return res.redirect('/products/' + productId)
        })
    }
    const rate = req.body.rate
    if (rate < 1 || rate > 5) {
        return res.status(400).send('評価の値が不正です。')
    }
    const comment = req.body.comment || ''
    db.get('SELECT * FROM reviews r WHERE r.product_id = ? AND r.user_id = ?', productId, userId, (err, review) => {
        if (!review) {
            return db.run('INSERT INTO reviews(product_id, user_id, rate, comment) VALUES (?, ?, ?, ?)', productId, userId, rate, comment, (err, row) => {
                return res.redirect('/products')
            })
        }
        db.run('UPDATE reviews SET rate = ?, comment = ? WHERE product_id = ? AND user_id = ?', rate, comment, productId, userId, (err, row) => {
            return res.redirect('/products')
        })
    })    
})

app.listen(PORT, HOST, () => {
    console.log(`Server ready at http://${HOST}:${PORT}`)
})
