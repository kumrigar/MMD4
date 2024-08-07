from flask import Flask, Blueprint, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

login_blueprint = Blueprint('login', __name__)

users = {
    "admin": "password"
}

LOGIN_FORM = """
<!doctype html>
<html>
<head>
  <title>Login - Autoark.ai</title>
  <style>
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      font-family: 'Arial', sans-serif;
      background: linear-gradient(to top, #09203f 0%, #537895 100%);
    }
    .login-container {
      display: flex;
      width: 800px;
      height: 400px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      border-radius: 8px;
      overflow: hidden;
    }
    .login-info {
    background: #fff;
    width: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center; /* Vertically center the content */
    align-items: center; /* Horizontally center the content */
    padding: 20px;
    box-sizing: border-box;
}
    .login-form {
      width: 50%;
      background: #eee;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 20px;
      box-sizing: border-box;
    }
    input[type="text"], input[type="password"] {
      width: 90%;
      padding: 10px;
      margin-bottom: 10px;
      border: none;
      background: #fff;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    input[type="submit"] {
      width: 96%;
      padding: 10px;
      border: none;
      background-color: #0F2143;
      color: white;
      font-size: 16px;
      cursor: pointer;
      border-radius: 5px;
    }
    input[type="submit"]:hover {
      background-color: #0c1a36;
    }
    .error {
      color: red;
      text-align: center;
    }
    .nav-logo {
    width: 70px;
    height: 70px;
    vertical-align: middle;
    margin-right: 5px;
}
  </style>
</head>
<body>
  <div class="login-container">
    <div class="login-info">
      <img src="{{ url_for('static', filename='marketing-automation.png') }}" class="nav-logo" alt="Logo">
      <h2>Welcome to Autoark.ai</h2>
      <p>Login to manage your clients efficiently.</p>
    </div>
    <div class="login-form">
      {% if error %}
        <p class="error">{{ error }}</p>
      {% endif %}
      <form method="post">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <input type="submit" value="Log In">
      </form>
    </div>
  </div>
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

