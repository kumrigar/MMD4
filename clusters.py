import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the data
file_path = 'D:\College\MSc BA 2023-2024\Capstone\Code\data.xlsx'
data = pd.read_excel(file_path)

# Selecting relevant columns for clustering
columns_of_interest = ['RenewalRate', 'ContractValue']
df = data[columns_of_interest].dropna()

# Standardizing the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)

# Determine the optimal number of clusters using the elbow method
inertia = []
for n in range(1, 11):
    kmeans = KMeans(n_clusters=n, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

# Applying KMeans clustering
optimal_clusters = 4  # This should be determined from the elbow plot
kmeans = KMeans(n_clusters = optimal_clusters, random_state = 42)
df['Cluster'] = kmeans.fit_predict(scaled_data)

# Plotting the clusters
plt.figure(figsize=(10, 8))
plt.scatter(df['ContractValue'], df['RenewalRate'], c=df['Cluster'], cmap='viridis', marker='o')
plt.title('Clusters of Clients')
plt.xlabel('Contract Value')
plt.ylabel('Renewal Rate')
plt.colorbar(label='Cluster')
plt.show()

# Display the first few rows with cluster labels
df.head()

# Save the clustered data to a new Excel file
df.to_excel('D:\College\MSc BA 2023-2024\Capstone\Code\clustered_data.xlsx', index=False)
