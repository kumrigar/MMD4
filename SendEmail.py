import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import modules
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances

sendgrid_api_key = "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"

if not sendgrid_api_key:
    print("API key not found. Please ensure it is set in the .env file.")
    exit(1)
else:
    print(f"API key found: {sendgrid_api_key[:4]}...")  # Print first few characters for verification

'''Loading the dataset. Here, we can either load it from the folder from which you download the application, or from a databse like SQL, 
 or from any open/public dataset available'''
try:
    filepath = os.getcwd() + "\\final_data.xlsx"
    data = pd.read_excel(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

# Reading dynamic prompts from the prompt engine
try:
    prompt_file_path = os.getcwd() + "\\prompts.xlsx"
    prompt_data = pd.read_excel(prompt_file_path)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

# Selecting relevant columns for generating recommendations for clients.
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

# Function to get top similar users using the numerical similarity matrix
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

# Saving the recommendations for further use as required
all_client_recommendations = generate_recommendations_for_all_clients()

# Convert the recommendations dictionary to a dataframe for easy data retrieval and usage
recommendations_df = pd.DataFrame.from_dict(all_client_recommendations, orient = 'index')
recommendations_df.reset_index(inplace = True)
recommendations_df.columns = ['ClientID'] + [f'Recommendation_{i+1}' for i in range(recommendations_df.shape[1] - 1)]
# Merge Recommendations with the original data file
final_df = data.merge(recommendations_df, on = 'ClientID', how = 'left')
# Save the final dataframe to a csv file
final_df.to_csv('client_recommendations.csv', index = False)

# A function that takes client ID from the client_recommendations file and returns its feature recommendations
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

# Randomly pick a prompt for email generation from the prompt dataframe and return it 
def get_random_prompt(prompt_data):
    # Randomly select one prompt
    prompt_row = prompt_data.sample(n=1).iloc[0]
    # Extract the actual prompt text 
    random_prompt = prompt_row['prompt_content']
    return random_prompt

prompt = get_random_prompt(prompt_data)

# Function to create personalized email
def get_personalized_email(client_id, prompt):
    recomm = get_recommendations(client_id)
    recomm_as_string = ', '.join(map(str, recomm))
    
    # Retrieve the client name for the given client ID. Could also retrieve more information as required.
    client_name = data[data['ClientID'] == client_id]['CompanyName'].values[0]
    first_name = data[data['ClientID'] == client_id]['FirstName'].values[0]
    last_name = data[data['ClientID'] == client_id]['LastName'].values[0]
    contact_person = f"{first_name} {last_name}"
    sender_name = "Raamesh P Kandalgaonkar"
    print(client_name)
    
    # Construct final prompt
    personalized_prompt = f"""{prompt}. Use "Dear {contact_person}" to start the email response.
    Don't add 'Subject' in the email response that is generated as we already have it covered. Consider adequaate spacing between paragraphs. 
    Refer {client_name} in the email as well whenever you refer to your client and use recommendations of {recomm_as_string} as feature recommendations to achieve objectives. 
    Our company name will be ARKTech Limited so use that as our company name. Use {sender_name} in the email signature. Make the entire email hyperpersonalized and engaging"""

    # Get the response
    response = modules.get_openai_response(personalized_prompt)
    #print(response)
    return response

# Function to send the email 
def send_email(client_id, prompt):
    # Generate the email content
    email_content = get_personalized_email(client_id, prompt)

    # Email configuration
    sender_email = "kunaal.umrigar@ucdconnect.ie"
    receiver_email = "raameshkandalgaonkar5@gmail.com"

    # Create the email message
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=f"Personalized Recommendations for {data[data['ClientID'] == client_id]['CompanyName'].values[0]}",
        plain_text_content = email_content
    )
    # Send the email
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent successfully to {receiver_email}, status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to get the top 4 peers within the same industry for a specific client. 
def benchmark_peers(client_id):
    # Extract the industry of the given ClientID
    client_industry = data.loc[data['ClientID'] == client_id, 'Industry'].values[0]
    
    # Filter the companies in the same industry
    same_industry_df = data[data['Industry'] == client_industry]
    
    # Define the features for benchmarking
    features = ['User Management', 'Data Analytics', 'API Access', 'Single Sign On (SSO)', 
                'Automated Backups', 'Performance Monitoring', 'Security Alerts', 
                'Chatbot', 'Customer Reports', 'Mobile Access', 'CustomerSatisfactionScore', 'ProductUsage']
    
    # Extract feature data for the same industry
    feature_data = same_industry_df[features]

    # Handle missing values by filling them with the mean of the column
    feature_data = feature_data.fillna(feature_data.mean())
    
    # Standardize the feature data
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(feature_data)
    
    # Get the index of the client company
    client_index = same_industry_df.index[same_industry_df['ClientID'] == client_id].tolist()[0]
    
    # Compute the Euclidean distances from the client company to all other companies 
    distances = euclidean_distances([standardized_data[client_index]], standardized_data)[0]
    
    # Create a DataFrame with distances
    distance_df = pd.DataFrame({'ClientID': same_industry_df['ClientID'], 'Distance': distances})
    
      # Sort by distance and select the top 2 peers
    top_peers_ids = distance_df.nsmallest(4, 'Distance')['ClientID']
    
    # Select the feature columns and additional columns for the top peers
    top_peers_details = data.loc[data['ClientID'].isin(top_peers_ids), ['ClientID', 'CompanyName', 'Industry', 'SupportTickets', 'ContractValue'] + features]
    
    # Select the feature columns for the client itself
    client_details = data.loc[data['ClientID'] == client_id, ['ClientID', 'CompanyName', 'Industry', 'SupportTickets', 'ContractValue'] + features]
    
    # Combine the client's details with the top peers' details
    combined_details = pd.concat([client_details, top_peers_details], ignore_index=True)
    

    # Merge with the original DataFrame to get full details
    #top_peers_details = pd.merge(top_peers, df, on='ClientID')
    
    return combined_details


# Example usage
#send_email(7, prompt)
#print(get_personalized_email(7, prompt))
