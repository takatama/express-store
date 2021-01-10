from bottle import route, run, template
import sqlite3


database_file = 'store.db'

@route('/products')
def list_products():
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    results = cur.execute('SELECT * FROM products;').fetchall()
    conn.close()
    return template('''
<h1>商品一覧</h1>
<table border="1">
  <tr>
    <th>商品名</th><th>説明</th><th>画像</th><th>価格</th>
  </tr>
  %for product in products:
  <tr>
    <td>{{ product[1] }}</td><td>{{ product[2] }}</td><td><img src="{{ product[3] }}"</td><td>{{ product[4] }}円</td>
  </tr>
  %end
</table>''', products=results)

run(host='localhost', port=8080)