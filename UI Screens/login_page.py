from flask import Blueprint, request, render_template_string, session, redirect, url_for

login_blueprint = Blueprint('login', __name__)

users = {
    "admin": "password"
}

LOGIN_FORM = """
<!doctype html>
<html>
<head>
  <title>Login</title>
  <style>
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      font-family: Arial, sans-serif;
      width: 100vw;
      height: 100vh;
    }
    form {
      border: 1px solid #ccc;
      padding: 20px;
      box-shadow: 0 0 10px #ccc;
      background: white;
    }
    input[type="text"], input[type="password"] {
      margin: 10px 0;
      width: 95%;
      padding: 10px;
    }
    input[type="submit"] {
      background-color: #4CAF50;
      color: white;
      border: none;
      padding: 10px 20px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 16px;
      margin: 4px 2px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="post">
    <div>
      Username: <input type="text" name="username"><br>
      Password: <input type="password" name="password"><br>
    </div>
    <input type="submit" value="Login">
  </form>
</body>
</html>
"""

@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home.home'))
        else:
            return render_template_string(LOGIN_FORM, error="Invalid credentials")
    return render_template_string(LOGIN_FORM, error=None)