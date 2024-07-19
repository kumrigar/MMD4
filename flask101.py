from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Required for session management

# Simple login form template
LOGIN_FORM = """
<!doctype html>
<html>
<head>
  <title>Login</title>
</head>
<body>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="post">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Login">
  </form>
</body>
</html>
"""

# User credentials (normally you would use a database)
users = {
    "admin": "secret"
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate credentials
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template_string(LOGIN_FORM, error="Invalid credentials")
    return render_template_string(LOGIN_FORM, error=None)

@app.route('/home')
def home():
    if 'username' in session:
        return f'Welcome {session["username"]}! <br><a href="{url_for("logout")}">Logout</a>'
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
