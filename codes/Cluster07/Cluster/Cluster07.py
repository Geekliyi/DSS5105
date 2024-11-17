import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.decomposition import PCA

def Cluster(file_path_data,base_path):
    # Load the uploaded CSV file
    
    esg_data = pd.read_csv(file_path_data)

    esg_data['revenue'] = esg_data['F-01_value'] * esg_data['F-02_value']


    columns_to_extract = ['CompanyName', 'Country', 'Year', 'revenue', 'E-01_value', 'E-02_value', 'E-03_value', 'E-04_value', 'E-05_value', 'E-06_value', 'E-07_value'
                        , 'S-01_value', 'S-02_value', 'S-03_value', 'S-04_value', 'S-05_value', 'S-06_value', 'S-07_value', 'S-08_value', 'S-09_value', 'G-01_value', 'G-02_value'
                        , 'G-03_value', 'G-04_value', 'G-05_value', 'G-06_value', 'G-08_value']

    new_df = esg_data[columns_to_extract]

    value_columns = [col for col in new_df.columns if 'value' in col]

    for col in value_columns:
        if (new_df[col] > 1000).any():  # 如果该列中有任意值超过 1000
            new_df[col] = new_df[col] / new_df['revenue']  # 将该列所有值除以 'revenue' 列

    data = new_df.dropna()

    initial_features = data.loc[:, 'E-01_value':'G-08_value']

    # Step 1: 数据中心化和标准化
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(initial_features)

    # Step 2: 使用肘部法和轮廓系数确定聚类中心
    inertia = []
    silhouette_scores = []
    range_n_clusters = range(2, 11)

    for n_clusters in range_n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        inertia.append(kmeans.inertia_)
        silhouette_avg = silhouette_score(features_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)

    # Setting the number of clusters to 3 based on the previous analysis
    optimal_clusters = 3
    kmeans_optimal = KMeans(n_clusters=optimal_clusters, random_state=42).fit(features_scaled)

    # Extract the cluster centers
    cluster_centers_3 = pd.DataFrame(kmeans_optimal.cluster_centers_, columns=initial_features.columns)
    cluster_centers_3.to_csv("cluster_centers.csv", index=False)

    # First, we need to calculate the mean values for each cluster on the ESG dimensions
    # Environmental (E-01 to E-07), Social (S-01 to S-09), and Governance (G-01 to G-08)

    env_columns = initial_features.columns[0:7]
    soc_columns = initial_features.columns[7:16]
    gov_columns = initial_features.columns[16:23]

    # Get mean values for each cluster in each ESG dimension
    cluster_means_esg = pd.DataFrame({
        'Environmental': cluster_centers_3[env_columns].mean(axis=1),
        'Social': cluster_centers_3[soc_columns].mean(axis=1),
        'Governance': cluster_centers_3[gov_columns].mean(axis=1)
    })

    # Set up radar chart data


    labels = ['Environmental', 'Social', 'Governance']
    num_vars = len(labels)

    # Adjust the angles and labels to ensure they match
    # Re-define angles and labels with the first value repeated to close the loop
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    labels = labels + [labels[0]]  # Repeat the first label at the end

    # Radar plot for each cluster with corrected labels and angles
    fig1, ax1 = plt.subplots(figsize=(10, 6), subplot_kw=dict(polar=True))

    for i in range(optimal_clusters):
        values = cluster_means_esg.iloc[i].tolist()
        values += values[:1]  # Close the loop
        ax1.plot(angles, values, linewidth=1, linestyle='solid', label=f'Cluster {i}')
        ax1.fill(angles, values, alpha=0.25)

    # Set up chart labels and title
    ax1.set_yticklabels([])
    ax1.set_xticks(angles)
    ax1.set_xticklabels(labels)
    plt.title('Cluster Mean Values Radar Chart')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    fig1.savefig(os.path.join(base_path,"radar_chart.png"), dpi=300)

    radar_chart = fig1

    # Bar chart for Environmental, Social, and Governance mean values
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    cluster_means_esg.plot(kind='bar', ax=ax2)
    ax2.set_title('Mean Environmental, Social, and Governance Values for Each Cluster')
    ax2.set_xlabel('Cluster')
    ax2.set_ylabel('Mean Value')
    plt.xticks(rotation=0)
    fig2.savefig(os.path.join(base_path,"cluster_means_esg_bar_chart.png"), dpi=300)
    cluster_means_esg_bar_chart = fig2

    return radar_chart,cluster_means_esg_bar_chart

