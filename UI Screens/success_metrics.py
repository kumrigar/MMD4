from flask import Blueprint, render_template_string
import pandas as pd
import os

try:
    filepath = os.getcwd() + "/final_data.xlsx"
    data = pd.read_excel(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

print(data.columns)

success_metrics_blueprint = Blueprint('success_metrics', __name__)

@success_metrics_blueprint.route('/clients/<int:client_id>/success-metrics', methods=['GET'])
def success_metrics(client_id):
    metrics_data = data[data['ClientID'] == client_id][['Increase in CSAT', 'New CSAT', 'Percentage Change in CSAT', 'Increase Product usage', 'New Product Usage']]
    if metrics_data.empty:
        return "No metrics found for this client", 404
    
    return render_template_string("""
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">               
            <title> Success Metrics </title>
        </head>
        <body>
            <header>
                <h2>Client Management System</h2>
                <nav>
                    <a href="{{ url_for('home.home') }}">Home</a>
                    <a href="{{ url_for('client_dashboard.dashboard') }}">Dashboard</a>
                    <a href="{{ url_for('logout.logout') }}">Logout</a>
                </nav>
            </header>
            
            <div class="container">
                <h2> Success Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    {% for col in metrics_data.columns %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ metrics_data.iloc[0][col] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <h3>Product Usage Increase</h3>
                <p>{{ metrics_data.iloc[0]['Increase Product usage'] }}</p>
            </div>
        </body>
    </html>
    """, metrics_data=metrics_data, client_id=client_id)
