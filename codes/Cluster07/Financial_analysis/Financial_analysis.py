import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import LeaveOneOut
import os

def analysis(file_path, new_data_path,base_path):

    # Load the uploaded CSV file
    esg_data = pd.read_csv(file_path)

    columns_to_extract = ['CompanyName', 'Country', 'Year', 'Score', 'share_price', 'income', 'WACC', 'volatility'
                        , 'liquidity_ratio', 'beta_coefficient', 'GDP_growth','unemployment_rate']

    new_df = esg_data[columns_to_extract]
    data = new_df.dropna()

    # Define the columns for plotting
    columns = [
        'share_price', 'income', 'WACC', 'volatility',
        'liquidity_ratio', 'beta_coefficient', 'GDP_growth', 'unemployment_rate'
    ]

    # Copy data to keep the original intact
    cleaned_data = data.copy()

    # Removing outliers for each specified column
    for col in columns:
        Q1 = cleaned_data[col].quantile(0.25)
        Q3 = cleaned_data[col].quantile(0.75)
        IQR = Q3 - Q1
        # Filtering out outliers
        cleaned_data = cleaned_data[~((cleaned_data[col] < (Q1 - 1.5 * IQR)) | (cleaned_data[col] > (Q3 + 1.5 * IQR)))]

    # 初始化标准化工具
    scaler = StandardScaler()

    # 对指定的自变量进行标准化
    cleaned_data_standardized = cleaned_data.copy()
    cleaned_data_standardized[columns] = scaler.fit_transform(cleaned_data[columns])

    # 定义特征和目标变量
    X = cleaned_data_standardized[columns]
    y = cleaned_data_standardized['Score']

    # 初始化随机森林模型
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

    # 训练模型
    rf_model.fit(X, y)

    # 进行预测
    y_pred = rf_model.predict(X)

    # 评估模型表现
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    # 特征重要性
    feature_importance = rf_model.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': columns,
        'Importance': feature_importance
    }).sort_values(by='Importance', ascending=False)

    # 假设 cleaned_data_standardized 是标准化后的数据集，并且已经加载
    X = cleaned_data_standardized[columns]
    y = cleaned_data_standardized['Score']

    # 将数据分为训练集和测试集（80% 训练集，20% 测试集）
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 初始化随机森林模型
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Initializing Leave-One-Out Cross-Validation
    loo = LeaveOneOut()

    # List to store MSE for each fold
    mse_list = []

    # Loop over each fold in Leave-One-Out CV
    for train_index, test_index in loo.split(X):
        # Splitting the data
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        # Train the Random Forest model on the training data
        rf_model.fit(X_train, y_train)
        
        # Make prediction on the test data (single observation)
        y_pred = rf_model.predict(X_test)
        
        # Calculate MSE for this fold and append to the list
        mse_list.append(mean_squared_error(y_test, y_pred))

    # Calculate the mean of all MSE values
    loocv_mse = np.mean(mse_list)


    # Extracting feature importances from the trained Random Forest model
    feature_importance = rf_model.feature_importances_

    # Creating a DataFrame for feature importance
    importance_df = pd.DataFrame({
        'Feature': columns,
        'Importance': feature_importance
    }).sort_values(by='Importance', ascending=False)

    # Plotting feature importance
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.barh(importance_df['Feature'], importance_df['Importance'], color='orange')
    ax1.set_xlabel("Importance Score")
    ax1.set_ylabel("Features")
    ax1.set_title("Feature Importances in Random Forest Model")
    ax1.invert_yaxis() 
    fig1.savefig(os.path.join(base_path,"Feature_Importances_in_Random_Forest_Model.png"), dpi=300)

    feature_importance_figure = fig1

    new_data = pd.read_csv(new_data_path)
    X_new = new_data[columns]
    X_new_standardized = scaler.transform(X_new)

    y_pred = rf_model.predict(X_new_standardized)
    new_data['Predicted_Score'] = y_pred
    output_columns = ['CompanyName', 'Country', 'Year', 'Predicted_Score', 
                    'share_price', 'income', 'WACC', 'volatility', 
                    'liquidity_ratio', 'beta_coefficient', 'GDP_growth', 'unemployment_rate']

    output_data = new_data[output_columns]
    output_path = 'predictions.csv'
    output_data.to_csv(os.path.join(base_path,output_path), index=False)





    original_data = cleaned_data.copy()

    # 定义CAPM模型参数
    risk_free_rate = 0.03  # 无风险利率（示例值）
    market_return = 0.08   # 市场预期收益率（示例值）

    # 定义自变量和因变量
    columns = ['share_price', 'Score', 'WACC', 'volatility', 
            'liquidity_ratio', 'beta_coefficient', 'GDP_growth', 'unemployment_rate']

    # 计算CAPM的期望收益率
    original_data['CAPM_Expected_Return_Rate'] = risk_free_rate + original_data['beta_coefficient'] * (market_return - risk_free_rate)

    # 使用 share_price 计算CAPM的实际期望收益金额
    original_data['CAPM_Expected_Income'] = original_data['CAPM_Expected_Return_Rate'] * original_data['share_price']

    # 定义自变量（包含CAPM期望收益）和因变量
    X = original_data[columns + ['CAPM_Expected_Return_Rate']]
    y = original_data['income']  # 以 income 为因变量

    # 初始化LOOCV和存储MSE的列表
    loo = LeaveOneOut()
    mse_list = []

    # 创建一个 DataFrame 来存储每次迭代的预测结果和偏离度
    results = pd.DataFrame(columns=['Actual_Income', 'Predicted_Income', 'CAPM_Expected_Income', 'Return_Deviation'])

    # LOOCV 循环
    for train_index, test_index in loo.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        # 训练随机森林模型
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # 预测单个测试样本
        y_pred = rf_model.predict(X_test)[0]  # 预测结果是一个数组，取第一个值
        
        # 计算单个样本的MSE并添加到列表
        mse_list.append(mean_squared_error([y_test], [y_pred]))
        
        # 获取CAPM的期望收益金额
        capm_expected_income = original_data.iloc[test_index]['CAPM_Expected_Income'].values[0]
        
        # 计算偏离度
        return_deviation = y_pred - capm_expected_income
        
        # 将结果添加到DataFrame中
        results = pd.concat([results, pd.DataFrame({
            'Actual_Income': [y_test.values[0]],
            'Predicted_Income': [y_pred],
            'CAPM_Expected_Income': [capm_expected_income],
            'Return_Deviation': [return_deviation]
        })], ignore_index=True)

        # 计算LOOCV的平均MSE
    loocv_mse = np.mean(mse_list)

    # 风险分级函数
    def risk_level(deviation):
        if abs(deviation) < 5:
            return 'Low Risk'
        elif abs(deviation) < 10:
            return 'Medium Risk'
        else:
            return 'High Risk'

    # 将风险等级应用到每个样本
    results['Risk_Level'] = results['Return_Deviation'].apply(risk_level)

    # 输出每个样本的实际值、预测值、CAPM期望收益和偏离度
    print("\nLOOCV Results with CAPM Expected Income and Deviation:")
    print(results[['Actual_Income', 'Predicted_Income', 'CAPM_Expected_Income', 'Return_Deviation', 'Risk_Level']])

    # 计算平均偏离度和偏离度的标准差
    average_deviation = results['Return_Deviation'].mean()
    std_deviation = results['Return_Deviation'].std()

    print(f"\nAverage Return Deviation: {average_deviation:.4f}")
    print(f"Standard Deviation of Return Deviation: {std_deviation:.4f}")


    # 可视化：偏离度分布图
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.hist(results['Return_Deviation'], bins=15, color='orange', edgecolor='black')
    ax2.axvline(0, color='red', linestyle='--', label='Expected Income')
    ax2.set_xlabel('Return Deviation')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Return Deviations')
    ax2.legend()
    fig2.savefig(os.path.join(base_path,"Distribution_of_Return_Deviations.png"), dpi=300)

    Distribution_of_Return_Deviations = fig2

    # 风险等级计数
    risk_counts = results['Risk_Level'].value_counts()

    # 可视化：风险分布饼图
    fig3, ax3 = plt.subplots(figsize=(8, 8))
    ax3.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', colors=['green', 'orange', 'red'])
    ax3.set_title('Risk Level Distribution')
    fig3.savefig(os.path.join(base_path,"Risk_Level_Distribution.png"), dpi=300)

    Risk_Level_Distribution = fig3


    # 计算CAPM的期望收益率和实际期望收益金额
    output_data['CAPM_Expected_Return_Rate'] = risk_free_rate + output_data['beta_coefficient'] * (market_return - risk_free_rate)
   
    output_data['CAPM_Expected_Income'] = output_data['CAPM_Expected_Return_Rate'] * output_data['share_price']

    # 计算偏离度 (Predicted_Score 作为预测的收益，CAPM_Expected_Income 作为CAPM计算的期望收益)
    output_data['Return_Deviation'] = output_data['income'] - output_data['CAPM_Expected_Income']

    # 应用风险分级到 Return_Deviation 列
    output_data['Risk_Level'] = output_data['Return_Deviation'].apply(risk_level)

    # 保存结果至新的 CSV 文件中
    final_output_path = 'final_output_with_risk_levels.csv'
    output_data.to_csv(os.path.join(base_path,final_output_path), index=False)

    # return feature_importance_figure,Distribution_of_Return_Deviations,Risk_Level_Distribution



