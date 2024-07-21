import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import modules
import os


# Load the dataset
#file_path = 'd:/College/MSc BA 2023-2024/Capstone/Sample Data/Data Draft - 1.0.xlsx'
#data = pd.read_excel(file_path)

try:
    filepath = os.getcwd() + "\\final_data.xlsx"
    data = pd.read_excel(filepath)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

#Read the prompt file
try:
    prompt_file_path = os.getcwd() + "\\prompts.xlsx"
    prompt_data = pd.read_excel(prompt_file_path)
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

#prompt_file_path = 'D:\College\MSc BA 2023-2024\Capstone\Code/prompts.xlsx'
#prompt_data = pd.read_excel(prompt_file_path)

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
def get_top_n_similar_users(user_id, n = 4):
    similar_users = similarity_df[user_id].sort_values(ascending=False).index[1:n+1]
    return similar_users

# Generate recommendations for a specific user using numerical data
def recommend_features(user_id, top_n_similar = 4):
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
        recommendations = recommend_features(user_id, top_n_similar = 4)
        all_recommendations[user_id] = recommendations
    return all_recommendations

# Generate recommendations for all clients
all_client_recommendations = generate_recommendations_for_all_clients()

#Write the recommendations in a csv file. Ensure all columns of the original data file is available as well in the recommendation file and in the end we have the recommendations as additional columns
'''client_names = data[['ClientID', 'CompanyName']]
recommendations_df = pd.DataFrame.from_dict(all_client_recommendations, orient='index')
recommendations_df.reset_index(inplace=True)
recommendations_df.columns = ['ClientID'] + [f'Recommendation_{i+1}' for i in range(recommendations_df.shape[1] - 1)]
recommendations_df = recommendations_df.merge(client_names, on = 'ClientID', how = 'left')
# Reorder columns to have ClientID, ClientName, and then recommendations
cols = ['ClientID', 'CompanyName'] + [col for col in recommendations_df.columns if col not in ['ClientID', 'CompanyName']]
recommendations_df = recommendations_df[cols]
recommendations_df.to_csv('client_recommendations.csv', index=False)'''

#Convert the recommendations dictionary to a dataframe
recommendations_df = pd.DataFrame.from_dict(all_client_recommendations, orient = 'index')
recommendations_df.reset_index(inplace=True)
recommendations_df.columns = ['ClientID'] + [f'Recommendation_{i+1}' for i in range(recommendations_df.shape[1] - 1)]
#Merge Recommendations with the original data
final_df = data.merge(recommendations_df, on = 'ClientID', how = 'left')
#Save the final datafdrame to a csv file
final_df.to_csv('client_recommendations.csv', index = False)

#Write a function that takes client ID from the client_recommendations file and returns it's recommendations
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

#Randomly pick a prompt for email generation from the prompt dataframe and save it in a variable. 
def get_random_prompt(prompt_data):
    # Randomly select one row from the prompt_data DataFrame
    prompt_row = prompt_data.sample(n=1).iloc[0]
    # Extract the prompt text from the selected row
    random_prompt = prompt_row['prompt_content']
    return random_prompt

prompt = get_random_prompt(prompt_data) 
#print(prompt) 
#complete_prompt = prompt + f"""Use {client_names} as client name/ Company name in the response and {recommendations_df} as feature recommendations. Our company name will be ARKTech Limited so use that as our
 #company name"""
#response = modules.get_openai_response(complete_prompt)
#print(response)

'''Write a function that takes client id and the prompt as input. This function will use the prompt to create dynamic email for this client and 
use the recommendations as well for drafting hyperpersonalized content. The output will be stored and returned in a response variable using openai_response '''
def get_personalized_email(client_id, prompt):
    recomm = get_recommendations(client_id)
    recomm_as_string = ', '.join(map(str, recomm))
    
    #Retrieve the client name for the given client ID. Could also retrieve more information as required.
    client_name = data[data['ClientID'] == client_id]['CompanyName'].values[0]
    first_name = data[data['ClientID'] == client_id]['FirstName'].values[0]
    last_name = data[data['ClientID'] == client_id]['LastName'].values[0]
    contact_person = f"{first_name} {last_name}"
    sender_name = "Raamesh P Kandalgaonkar"
    print(client_name)
    #construct final prompt
    personalized_prompt = f"""{prompt}. Use "Dear {contact_person}" to start the email response. Refer {client_name} in the email as well whenevr you refer to the your client and use recommendations of {recomm_as_string} as feature recommendations to achive objectives. Our company name will be ARKTech Limited so use that as our
 company name. Use {sender_name} in the email signature. Make the entire email hyperpersonalized and engaging"""

    #Get the response
    response = modules.get_openai_response(personalized_prompt)
    #print(response)
    return response

# Create prompts and get OpenAI API responses
#'''for client_id, recommendations in all_client_recommendations.items():
 #   prompt = f"ClientID: {client_id}\nRecommendations: {recommendations}. Use the {recommendations} and create a very engaging email to the admin working for client {client_id}."
  #  response = modules.get_openai_response(prompt)
   # print(f"ClientID: {client_id}\nRecommendations: {recommendations}\nResponse: {response}\n")'''

email = get_personalized_email(7,prompt)

print(email)