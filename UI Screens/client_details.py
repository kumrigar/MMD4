from flask import Blueprint, render_template_string, session, redirect, url_for, request, flash
import pandas as pd
import os
import openai   
import SendEmail

try:
    filepath = os.getcwd() + "/client_recommendations.csv"
    recommendations_data = pd.read_csv(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

try:
    filepath = os.getcwd() + "/final_data.xlsx"
    data = pd.read_excel(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

try:
    prompt_file_path = os.getcwd() + "/prompts.xlsx"
    prompt_file_path_onboarding = os.getcwd() + "/onboarding_prompts.xlsx"
    prompt_data = pd.read_excel(prompt_file_path)
    prompt_data_onboarding = pd.read_excel(prompt_file_path_onboarding)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")
    
client_details_blueprint = Blueprint('client_details', __name__)

custom_headers = {
    'ClientID': 'Client ID',
    'AnnualSpending': 'Annual Spending (€)',
    'ProductUsed': 'Product Used',
    'LastInteractionDate': 'Last Interaction Date',
    'CustomerSatisfactionScore': 'Satisfaction Score',
    'RenewalRate': 'Renewal Rate',
    'OnboardingProgress': 'Onboarding Progress',
    'UpsellPotential': 'Upsell Potential',
    'TextualFeedback': 'Feedback'
}

prompt = SendEmail.get_random_prompt(prompt_data)
prompt_onboard = SendEmail.get_random_prompt_onboarding(prompt_data_onboarding)

@client_details_blueprint.route('/clients/<int:client_id>', methods=['GET', 'POST'])
def details(client_id):
    client_info = data[data['ClientID'] == client_id]
    if client_info.empty:
        return "Client not found", 404
    
    client_id_extract = data[data['ClientID'] == client_id]
    client_id = client_id_extract.iloc[0]['ClientID']
    
    receiver_email_extract = data[data['ClientID'] == client_id]
    receiver_email = receiver_email_extract.iloc[0]['custom_email']

    onboarding_progress = client_info.iloc[0]['OnboardingProgress']

    result = False
    if request.method == 'POST':
        if 'recommendation_email' in request.form:
            recommendation = request.form.get('recommendation')
            result = SendEmail.send_email_single_recommendation(client_id, prompt, receiver_email, recommendation)

        elif 'onboarding_email' in request.form:
            result = SendEmail.send_email_onboard(client_id, prompt_onboard, receiver_email)

        if result:
            flash('Email has been sent successfully!', 'success')
        else:
            flash('Failed to send email.', 'error')
    
    recommendation_columns = [col for col in recommendations_data.columns if col.startswith('Recommendation_')]
    client_recommendations = recommendations_data[recommendations_data['ClientID'] == client_id][recommendation_columns].dropna(axis=1, how='all')

    return render_template_string("""
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">               
            <title> Client Details </title>
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
                <h2> Details for {{ client_info.iloc[0]['CompanyName'] }} </h2>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message {{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <div class="btn-container">
                    <button id="successMetricsButton" style="display:none;" class="btn" onclick="window.location.href='{{ url_for('success_metrics.success_metrics', client_id=client_id) }}'">Success Metrics</button>
                    <button id="closeButton" style="display:none;" class="close-btn" onclick="hideSuccessMetricsButton()">X</button>
                </div>
                
                <table>
                    <tr>
                        <th>Information</th>
                        <th>Details</th>
                    </tr>
                    {% for col in custom_headers %}
                    <tr>
                        <td>{{ custom_headers[col] }}</td>
                        <td>{{ client_info.iloc[0][col] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                
                {% if onboarding_progress == 'Completed' %}
                    <div class="recommendations">
                        <h2>Recommendations</h2>
                        <table>
                            <tr>
                                <th>Recommendation</th>
                                <th>Action</th>
                            </tr>
                            {% for col in client_recommendations.columns %}
                            <tr>
                                <td>{{ client_recommendations.iloc[0][col] }}</td>
                                <td>
                                    <form method="post" style="display: inline;">
                                        <input type="hidden" name="recommendation" value="{{ client_recommendations.iloc[0][col] }}">
                                        <input type="submit" name="recommendation_email" value="Automate Email" class="btn">
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% else %}
                    <div class="onboarding">
                        <h3>Onboarding is in progress</h3>
                    </div>
                    <form method="post">
                        <input type="submit" name="onboarding_email" value="Automate Email" class="btn">
                    </form>
                {% endif %}
            </div>
            
            <script src="{{ url_for('static', filename='scripts.js') }}"></script>
        </body>
    </html>
    """, client_info=client_info, custom_headers=custom_headers, client_recommendations=client_recommendations, onboarding_progress=onboarding_progress, client_id=client_id)
