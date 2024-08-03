from flask import Blueprint, render_template_string, session, redirect, url_for, request
import pandas as pd
import os

home_blueprint = Blueprint('home', __name__)

try:
    file_path = os.getcwd() + "/final_data.xlsx"
    data = pd.read_excel(file_path)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

custom_headers = {
    'ClientID': 'Client ID',
    'CompanyName': 'Company Name',
    'Industry': 'Sector',
    'CompanySize': 'Size',
    'AnnualSpending': 'Annual Spending (€)',
    'CustomerSatisfactionScore': 'Satisfaction Score',
    'RenewalRate': 'Renewal Rate',
    'CLV': 'CLV'
}

@home_blueprint.route('/home')
def home():
    if 'username' in session:
        display_columns = list(custom_headers.keys())
        filtered_data = data[display_columns + ['customer_tier']]

        # Get the selected customer tier from the request arguments
        selected_tier = request.args.get('tier', None)

        # Filter data based on the selected customer tier
        if selected_tier:
            filtered_data = filtered_data[filtered_data['customer_tier'] == selected_tier]

        # Get unique customer tiers for dropdown options
        customer_tiers = data['customer_tier'].unique()

        return render_template_string("""
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">               
                <title>Client List</title>
            </head>
            <body>
                <header>
                    <h2>Client Management System</h2>
                    <nav>
                        <a href="{{ url_for('client_dashboard.dashboard') }}">Dashboard</a>
                        <a href="{{ url_for('logout.logout') }}">Logout</a>
                    </nav>
                </header>
                <div class="container">
                    <h1>Client List</h1>
                    <form method="get" action="{{ url_for('home.home') }}">
                        <label for="tier-select">Filter by Customer Tier:</label>
                        <select name="tier" id="tier-select" onchange="this.form.submit()">
                            <option value="">All Customers</option>
                            {% for tier in customer_tiers %}
                                <option value="{{ tier }}" {% if selected_tier == tier %}selected{% endif %}>{{ tier }} Customers</option>
                            {% endfor %}
                        </select>
                    </form>
                    <table>
                        <tr>
                            {% for col in display_columns %}
                            <th>{{ custom_headers[col] }}</th>
                            {% endfor %}
                            <th>Actions</th>
                        </tr>
                        {% for _, row in filtered_data.iterrows() %}
                        <tr>
                            {% for col in display_columns %}
                            <td>{{ row[col] }}</td>
                            {% endfor %}
                            <td><a href="{{ url_for('client_details.details', client_id=row['ClientID']) }}" class="btn">View More</a></td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </body>
        </html>
        """, filtered_data=filtered_data, custom_headers=custom_headers, display_columns=display_columns, customer_tiers=customer_tiers, selected_tier=selected_tier)
    else:
        return redirect(url_for('login.login'))
