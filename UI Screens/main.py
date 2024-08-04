from flask import Flask
from login_page import login_blueprint
from home_page import home_blueprint
from logout_page import logout_blueprint
from client_details import client_details_blueprint 
from client_dashboard import client_dashboard_blueprint
from success_metrics import success_metrics_blueprint

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  

app.register_blueprint(login_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(client_details_blueprint, url_prefix='/details')
app.register_blueprint(client_dashboard_blueprint)
app.register_blueprint(success_metrics_blueprint, url_prefix='/success_metrics')

if __name__ == '__main__':
    app.run(debug=True)
