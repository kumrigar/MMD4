from flask import Flask, Blueprint, request, render_template_string, session, redirect, url_for
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client_dashboard_blueprint = Blueprint('client_dashboard', __name__)

@client_dashboard_blueprint.route('/dashboard')
def dashboard():
    # Assume data loading and plot generation are handled elsewhere
    plot_path = 'combined_plot.png'  # This should be the path to the saved plot image in static folder
    cluster_image_path = 'Cluster.png'  # Ensure this is in your static folder
    
    return render_template_string("""
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
            <title>Client Dashboard</title>
        </head>
        <body>
            <header>
                <div class="header-logo">
                    <img src="{{ url_for('static', filename='marketing-automation.png') }}" class="nav-logo" alt="Logo">
                    <h2>Autoark.ai</h2>
                </div>
                <nav>
                    <a href="{{ url_for('home.home') }}">Home</a>
                    <a href="{{ url_for('logout.logout') }}">Logout</a>
                </nav>
            </header>
            
            <div class="container">
                <h1>Customer Trends</h1>
                <div class="trend-chart">
                    <img src="{{ url_for('static', filename=plot_path) }}" alt="Combined Plots">
                    <img src="{{ url_for('static', filename=cluster_image_path) }}" alt="Cluster Analysis">
                </div>
            </div>
        </body>
    </html>
    """, plot_path=plot_path, cluster_image_path=cluster_image_path)

app.register_blueprint(client_dashboard_blueprint, url_prefix='/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
