import matplotlib
matplotlib.use('Agg')  # Use the non-GUI backend 'Agg' for rendering plots

import matplotlib.pyplot as plt
from flask import Blueprint, render_template_string
import pandas as pd
import os

client_dashboard_blueprint = Blueprint('client_dashboard', __name__)

# Load the data
try:
    file_path = os.getcwd() + "/final_data.xlsx"
    data = pd.read_excel(file_path)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

def create_satisfaction_trend_plot(data):
    plt.figure(figsize=(10, 6))
    # Example plot: customer satisfaction by customer tier
    data.groupby('customer_tier')['CustomerSatisfactionScore'].mean().plot(kind='bar')
    plt.title('Average Customer Satisfaction Score by Customer Tier')
    plt.xlabel('Customer Tier')
    plt.ylabel('Average Satisfaction Score')
    plt.tight_layout()
    static_dir = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    plot_path = os.path.join(static_dir, 'satisfaction_trend.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@client_dashboard_blueprint.route('/dashboard')
def dashboard():
    # Generate the satisfaction trend plot
    plot_path = create_satisfaction_trend_plot(data)
    
    return render_template_string("""
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">               
            <title>Client Dashboard</title>
        </head>
        <body>
            <header>
                <h2>Client Management System</h2>
                <nav>
                    <a href="{{ url_for('home.home') }}">Home</a>
                    <a href="{{ url_for('logout.logout') }}">Logout</a>
                </nav>
            </header>
            <div class="container">
                <h1>Customer Satisfaction Trends</h1>
                <div class="trend-chart">
                    <img src="{{ url_for('static', filename='satisfaction_trend.png') }}" alt="Customer Satisfaction Trend">
                </div>
            </div>
        </body>
    </html>
    """)
