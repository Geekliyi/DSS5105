import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import matplotlib.pyplot as plt

#1.读取数据
def load_csv_file(filepath):
    df = pd.read_csv(filepath)
    return df

#2.清洗数据
def clean_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalpha() and t not in stopwords.words('english')]
    return ' '.join(tokens)

#3.bert模型
def bert_sentiment(model,data):
    data_list = data.tolist()
    ans = model(data_list)
    return ans

#4.创建label列表
def label_list(ans):
    label_list = []
    # 摘取label
    for i in ans:
        label_list.append(int(i['label'][0]))
    return label_list

#5.sentiment分布图制作
def sentiment_distribution(dataframe, column_name, plt_path):
    # 得到label信息并排序
    sentiment_counts = dataframe[column_name].value_counts()
    sentiment_counts_sorted = sentiment_counts.sort_index()

    # 绘制情感分布图
    plt.figure(figsize=(8, 6))
    colors = [(0, 1, 0, alpha) for alpha in np.linspace(0.2, 1, 5)]
    plt.bar(sentiment_counts_sorted.index, sentiment_counts_sorted.values, color=colors)
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.savefig(plt_path)
    plt.show()
    plt.close()

#6.计算数据集的总分数
def calculate_dataset_score(dataframe, column_name):
    label_counts = dataframe[column_name].value_counts()
    #总分数
    overall_score = sum(label * count for label, count in label_counts.items()) / len(dataframe)
    #归一化
    dataset_score = overall_score / 5
    return dataset_score

def Sentiment_Analysis(source_folder, destination_folder):
    specific_model = pipeline(model="nlptown/bert-base-multilingual-uncased-sentiment")
    news_score = pd.DataFrame(columns=['Company', 'Sentiment_Score'])
    for subfolder in os.listdir(source_folder): #subfolder:new_scrape; source_folder:data
        source_subfolder_path = os.path.join(source_folder, subfolder) #data/news_scrape

        if os.path.isdir(source_subfolder_path):
            destination_subfolder_path = os.path.join(destination_folder, 'news_score') #sentiment/news_score
            os.makedirs(destination_subfolder_path, exist_ok=True)
            sd_path = os.path.join(destination_folder, 'sentiment_distribution')
            os.makedirs(sd_path, exist_ok=True)


            for filename in os.listdir(source_subfolder_path):
                if filename.endswith('.csv'):
                    # Step 1:导入数据
                    csv_path = os.path.join(source_subfolder_path, filename)
                    csv_input = load_csv_file(csv_path)


                    # Step 2: 清洗新闻数据
                    csv_description = csv_input['Description']
                    csv_input['ProcessedDescription'] = csv_description.apply(clean_text)

                    # Step 3: 用bert贴标签
                    sentiment_data = bert_sentiment(specific_model,csv_input['ProcessedDescription'])

                    # Step 4: 创建label列表
                    sentiment_label = label_list(sentiment_data)
                    csv_input['label'] = sentiment_label

                    # Step 5: sentiment分布图制作
                    plt_filename = filename.replace('.csv', '_sentiment_distribution.jpg')
                    plt_path = os.path.join(sd_path, plt_filename)
                    sentiment_distribution(csv_input, 'label', plt_path)


                    # Step 6: 计算数据集的总分数
                    csv_score = calculate_dataset_score(csv_input,'label')
                    print(f"{filename} 的分数: {csv_score}")

                    # Step 7: 写入news_score里
                    company_name = filename.replace('.csv', '')
                    new_data = pd.DataFrame({'Company': [company_name], 'Sentiment_Score': [csv_score]})
                    news_score = pd.concat([news_score, new_data], ignore_index=True)
                    news_score.sort_values(by='Sentiment_Score', ascending=False, inplace=True)
                    print(news_score)

            news_score.to_csv(os.path.join(destination_subfolder_path, 'news_score.csv'), index=False)



Sentiment_Analysis('data', 'sentiment')