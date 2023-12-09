const express = require('express')
const app = express()
const host = 'localhost'
const port = 8082
const ejs = require('ejs')
app.use(express.urlencoded({ extended: true }))
const cookieParser = require('cookie-parser')
const secureKey = process.env.SECRET_KEY
if (!secureKey) throw '環境変数 SECRET_KEY が設定されていません。'
app.use(cookieParser(secureKey))

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
