import openai
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances

def get_openai_response(prompt):
    openai.api_key = 'sk-proj-f8bL6T3zc8airViV5XzcT3BlbkFJWOKimruuQDk3UPOu3zfy'  # Replace with your OpenAI API key
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Using a chat-based model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 500  # Adjust the token count as needed
    )
    return response.choices[0].message.content

#Randomly pick a prompt for email generation from the prompt dataframe and save it in a variable. 
def get_random_prompt(prompt_data):
    # Randomly select one row from the prompt_data DataFrame
    prompt_row = prompt_data.sample(n=1).iloc[0]
    # Extract the prompt text from the selected row
    random_prompt = prompt_row['Prompt']
    return random_prompt

# Function to give industry specific insights of the clients managed by the CSM
def industry_analysis(data):
    industry_group = data.groupby('Industry')[['AnnualSpending', 'CustomerSatisfactionScore', 'RenewalRate', 'NPS', 'ContractValue', 'EngagementScore']].mean().reset_index()
    #print("\nIndustry Segmentation Analysis:")
    return(industry_group)

# Function to plot trendlines for a set of factors that go as 'pairs'
def plot_trendlines(data, pairs, title='Trendline Analysis'):
    num_pairs = len(pairs)
    fig, axes = plt.subplots(1, num_pairs, figsize=(15, 6))
    
    for i, (x, y) in enumerate(pairs):
        sns.regplot(data=data, x=x, y=y, ax=axes[i])
        axes[i].set_title(f'Relationship between {x} and {y}')
        axes[i].set_xlabel(x)
        axes[i].set_ylabel(y)
    
    plt.suptitle(title)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

#Function to plot a correlation matrix for a specific industry
def plot_correlation_matrix(data, industry):
    industry_df = data[data['Industry'] == industry]
    print(f"\nInsights for Industry: {industry}")
    print(industry_df.describe())
    columns = ['User Management', 'Data Analytics', 'API Access', 'Single Sign On (SSO)', 
                    'Automated Backups', 'Performance Monitoring', 'Security Alerts', 
                    'Chatbot', 'Customer Reports', 'Mobile Access', 'CustomerSatisfactionScore', 'ProductUsage']
    plt.figure(figsize = (12, 8))
    sns.heatmap(industry_df[columns].corr(), annot = True, cmap = 'viridis')
    plt.title(f'Correlation Matrix for {industry}')
    plt.show()

# Function to check the benchmark a client with peers operating in the same industry
def benchmark_peers(data, client_id):
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
    combined_details.to_csv('peers.csv', index = False)
    return combined_details




