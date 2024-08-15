import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import modules
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

sendgrid_api_key = "Your API Key" 

if not sendgrid_api_key:
    print("API key not found. Please ensure it is set in the .env file.")
    exit(1)
else:
    print(f"API key found: {sendgrid_api_key[:4]}...")  # Print first few characters for verification

# Load the dataset
try:
    filepath = os.getcwd() + "/final_data.xlsx"
    data = pd.read_excel(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

# Reading dynamic prompts from the prompt engine
try:
    prompt_file_path = os.getcwd() + "/prompts.xlsx"
    prompt_file_path_onboarding = os.getcwd() + "/onboarding_prompts.xlsx"
    prompt_data = pd.read_excel(prompt_file_path)
    prompt_data_onboarding = pd.read_excel(prompt_file_path_onboarding)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

# Selecting relevant numerical columns from the dataset
selected_columns = ['AnnualSpending', 'ProductUsage', 'FeatureUsage', 'EngagementScore', 'User Management',  'Data Analytics', 'Customer Reports', 'Chatbot', 'Security Alerts',
                    'Performance Monitoring', 'Mobile Access', 'Automated Backups', 'Single Sign On (SSO)',
                    'API Access']

# Filter the dataset to include only selected numerical columns and ensure no missing values
numerical_data = data[['ClientID'] + selected_columns].fillna(0)

# Creating a user-feature interaction matrix using selected numerical columns
interaction_matrix = numerical_data.set_index('ClientID')

# Calculate the cosine similarity between users with the numerical interaction matrix
similarity_matrix = cosine_similarity(interaction_matrix)

# Convert the similarity matrix to a DataFrame for better readability
similarity_df = pd.DataFrame(similarity_matrix, index=interaction_matrix.index, columns=interaction_matrix.index)

# Function to get top N similar users using the numerical similarity matrix
def get_top_n_similar_users(user_id, n=4):
    similar_users = similarity_df[user_id].sort_values(ascending=False).index[1:n+1]
    return similar_users

# Generate recommendations for a specific user using numerical data
def recommend_features(user_id, top_n_similar=4):
    # Get top N similar users
    similar_users = get_top_n_similar_users(user_id, top_n_similar)
    # Aggregate features used by similar users
    similar_users_features = interaction_matrix.loc[similar_users].sum(axis=0)
    
    # Filter out features already used by the target user
    user_features = interaction_matrix.loc[user_id]
    recommendations = similar_users_features[user_features == 0].sort_values(ascending=False)
    
    return recommendations.index.tolist()

# Generate recommendations for all clients
def generate_recommendations_for_all_clients():
    all_recommendations = {}
    for user_id in interaction_matrix.index:
        recommendations = recommend_features(user_id, top_n_similar=4)
        all_recommendations[user_id] = recommendations
    return all_recommendations

# Generate recommendations for all clients
all_client_recommendations = generate_recommendations_for_all_clients()

# Convert the recommendations dictionary to a dataframe
recommendations_df = pd.DataFrame.from_dict(all_client_recommendations, orient='index')
recommendations_df.reset_index(inplace=True)
recommendations_df.columns = ['ClientID'] + [f'Recommendation_{i+1}' for i in range(recommendations_df.shape[1] - 1)]
# Merge Recommendations with the original data
final_df = data.merge(recommendations_df, on='ClientID', how='left')
# Save the final dataframe to a csv file
final_df.to_csv('client_recommendations.csv', index=False)

# Write a function that takes client ID from the client_recommendations file and returns its recommendations
def get_recommendations(client_id):
    # Load the recommendations from the CSV file
    recommendations_df = pd.read_csv('client_recommendations.csv')
    
    # Find the row corresponding to the client ID
    client_recommendations = recommendations_df[recommendations_df['ClientID'] == client_id]
    
    # Check if client ID exists in the DataFrame
    if client_recommendations.empty:
        return f"No recommendations found for ClientID: {client_id}"
    
    # Get only the recommendation columns (assumes they start with 'Recommendation_')
    recommendation_columns = [col for col in recommendations_df.columns if col.startswith('Recommendation_')]
    recommendations = client_recommendations[recommendation_columns].values.flatten().tolist()
    
    # Filter out any NaN values from the recommendations
    recommendations = [rec for rec in recommendations if pd.notna(rec)]
    
    return recommendations

# Randomly pick a prompt for email generation from the prompt dataframe and save it in a variable. 
def get_random_prompt(prompt_data):
    # Randomly select one row from the prompt_data DataFrame
    prompt_row = prompt_data.sample(n=1).iloc[0]
    # Extract the prompt text from the selected row
    random_prompt = prompt_row['prompt_content']
    return random_prompt

prompt = get_random_prompt(prompt_data)

def get_random_prompt_onboarding(prompt_data_onboarding):
    # Randomly select one prompt
    prompt_row_onboard = prompt_data_onboarding.sample(n=1).iloc[0]
    # Extract the actual prompt text 
    random_prompt = prompt_row_onboard['prompt_content']
    return random_prompt

prompt = get_random_prompt(prompt_data)
prompt_onboard = get_random_prompt_onboarding(prompt_data_onboarding)

# Function to create personalized email
def get_personalized_email(client_id, prompt):
    recomm = get_recommendations(client_id)
    recomm_as_string = ', '.join(map(str, recomm))
    
    # Retrieve the client name for the given client ID. Could also retrieve more information as required.
    client_name = data[data['ClientID'] == client_id]['CompanyName'].values[0]
    first_name = data[data['ClientID'] == client_id]['FirstName'].values[0]
    last_name = data[data['ClientID'] == client_id]['LastName'].values[0]
    contact_person = f"{first_name} {last_name}"
    sender_name = "Kunaal Umrigar"
    print(client_name)
    
    # Construct final prompt
    personalized_prompt = f"""{prompt}. Use "Dear {contact_person}" to start the email response.
    Don't add 'Subject' in the email response that is generated as we already have it covered. Consider adequaate spacing between paragraphs. 
    Refer {client_name} in the email as well whenever you refer to your client and use recommendations of {recomm_as_string} as feature recommendations to achieve objectives. 
    Our company name will be ARKTech Limited so use that as our company name. Use {sender_name} in the email signature. Make the entire email hyperpersonalized and engaging"""

    # Get the response
    response = modules.get_openai_response(personalized_prompt)
    print(response)
    return response

def send_email(client_id, prompt, receiver_email):
    
    email_content = get_personalized_email(client_id, prompt)

    # Email configuration
    sender_email = "kunaal.umrigar@ucdconnect.ie"
    #receiver_email = "raameshkandalgaonkar5@gmail.com"

    # Create the email message
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=f"Personalized Recommendations for {data[data['ClientID'] == client_id]['CompanyName'].values[0]}",
        plain_text_content = email_content
    )
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if response.status_code == 202:
            print(f"Email sent successfully to {receiver_email}, status code: {response.status_code}")
            return True
        else:
            print(f"Failed to send email, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function to create personalized email for customers newly onboarded.
def get_personalized_email_onboard(client_id, prompt_onboard):
    #recomm = get_recommendations(client_id)
    #recomm_as_string = ', '.join(map(str, recomm))
    
    # Retrieve the client name for the given client ID. Could also retrieve more information as required.
    client_name = data[data['ClientID'] == client_id]['CompanyName'].values[0]
    first_name = data[data['ClientID'] == client_id]['FirstName'].values[0]
    last_name = data[data['ClientID'] == client_id]['LastName'].values[0]
    contact_person = f"{first_name} {last_name}"
    sender_name = "Kunaal Umrigar"
    #print(client_name)
    
    # Construct final prompt
    personalized_prompt_onboard = f"""{prompt_onboard}. Use "Dear {contact_person}" to start the email response.
    Don't add 'Subject' in the email response that is generated as we already have it covered. Consider adequaate spacing between paragraphs. 
    Refer {client_name} in the email as well whenever you refer to your client. Use objectives. 
    Our company name will be ARKTech Limited so use that as our company name. Use {sender_name} in the email signature. Make the entire email hyperpersonalized and welcoming."""

    # Get the response
    response = modules.get_openai_response(personalized_prompt_onboard)
    #print(response)
    return response

# Function to send email for new clients being onboarded.
def send_email_onboard(client_id, prompt_onboard, receiver_email):
    # Generate the email content
    email_content_onboard = get_personalized_email_onboard(client_id, prompt_onboard)

    # Email configuration
    sender_email = "kunaal.umrigar@ucdconnect.ie"
    #receiver_email = "raameshkandalgaonkar5@gmail.com"

    # Create the email message
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=f"Welcome {data[data['ClientID'] == client_id]['CompanyName'].values[0]}",
        plain_text_content = email_content_onboard
    )
    # Send the email
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if response.status_code == 202:
            print(f"Email sent successfully to {receiver_email}, status code: {response.status_code}")
            return True
        else:
            print(f"Failed to send email, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_email_single_recommendation(client_id, prompt, receiver_email, recommendation):
    # Generate the email content
    email_content = single_recommendation_email(client_id, prompt, recommendation)

    # Email configuration
    sender_email = "kunaal.umrigar@ucdconnect.ie"
    #receiver_email = "raameshkandalgaonkar5@gmail.com"

    # Create the email message
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=f"Personalized Recommendation for {data[data['ClientID'] == client_id]['CompanyName'].values[0]}",
        plain_text_content = email_content
    )
    # Send the email
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if response.status_code == 202:
            print(f"Email sent successfully to {receiver_email} for {recommendation}, status code: {response.status_code}")
            return True
        else:
            print(f"Failed to send email, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def single_recommendation_email(client_id, prompt, recommendation):

    reco_as_str = str(recommendation)
    
    # Retrieve the client name for the given client ID
    client_name = data[data['ClientID'] == client_id]['CompanyName'].values[0]
    first_name = data[data['ClientID'] == client_id]['FirstName'].values[0]
    last_name = data[data['ClientID'] == client_id]['LastName'].values[0]
    contact_person = f"{first_name} {last_name}"
    sender_name = "Kunaal Umrigar"
    
    #Retrieve the primary 3 business objectives of the client
    interest_priorities = data.loc[data['ClientID'] == client_id, 
                                   ['Interest Priority_1', 'Interest Priority_2', 'Interest Priority_3']].values[0]
    interest_priorities_str = ', '.join(interest_priorities)

    # Construct final prompt
    personalized_prompt = f"""{prompt}. Use "Dear {contact_person}" to start the email response.
    Don't add 'Subject' in the email response.
    Refer {client_name} in the email as well whenever you refer to client/customer and use {reco_as_str} as feature recommendation to achieve the business objectives which are {interest_priorities_str}. 
    Our company name will be ARKTech Limited so use it whenever required. Use {sender_name} in the email signature. Make the entire email hyperpersonalized and engaging. Word limit is 200 words strictly. Simplify the content."""

    response = modules.get_openai_response(personalized_prompt)
    return response