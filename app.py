from flask import Flask, render_template, request,jsonify,redirect,url_for
import os
import base64
import pandas as pd
import importlib
import numpy as np
import logging


app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # 将日志写入文件
        logging.StreamHandler()  # 同时显示在控制台
    ]
)

# 上传文件保存路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def upload_page():
    # 首页显示上传页面
    return render_template('upload1.html')


# 定义公共路径变量
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'uploads')
#导入模块
step1 = importlib.import_module("codes.PDFtoWORD01.PDFtoWORD01")
step1_path = os.path.join(os.path.dirname(__file__), 'codes', 'PDFtoWORD01')

step2 = importlib.import_module("codes.WORDtoTXT02.WORDtoTXT02")
step2_path = os.path.join(os.path.dirname(__file__), 'codes', 'WORDtoTXT02')

step3 = importlib.import_module("codes.ExtractData_RE03.ExtractData_RE03")
step3_path = os.path.join(os.path.dirname(__file__), 'codes', 'ExtractData_RE03')

# step4 = importlib.import_module("codes.ExtractData_LLM04.ExtractData_LLM04")
# step4_path = os.path.join(os.path.dirname(__file__), 'codes','ExtractData_LLM04')

step5 = importlib.import_module("codes.ExtractData_Combine05.ExtractData_Combine05")
step5_path = os.path.join(os.path.dirname(__file__), 'codes', 'ExtractData_Combine05')

# step6 = importlib.import_module("codes.Sentiment_Analysis06.Sentiment_Analysis06")
# step6_path = os.path.join(os.path.dirname(__file__), 'codes','Sentiment_Analysis06')

step7 = importlib.import_module("codes.Cluster07.Cluster.Cluster07")
step7_path = os.path.join(os.path.dirname(__file__), 'codes', 'Cluster07', 'Cluster')

step8 = importlib.import_module("codes.Cluster07.Financial_analysis.Financial_analysis")
step8_path = os.path.join(os.path.dirname(__file__), 'codes', 'Cluster07', 'Financial_analysis')

step9_path = os.path.join(os.path.dirname(__file__), 'codes', 'Score08')
def get_image_data(filename):
    # 读取图片并编码为Base64
    with open(filename, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def read_esg_data(file_path):
    """
    读取CSV文件并返回包含指定字的数据字典列表。
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, usecols=["CompanyName", "Year", "predicted_ESG_score"])

        # 将数据转换为字典列表
        data = df.to_dict(orient='records')

        return data
    except FileNotFoundError:
        print("文件未找到，请检查路径。")
        return None
    except ValueError:
        print("CSV文件缺少所需的字段，请检查文件内容。")
        return None





def get_company_data(df,company_name, year):
    """
    获取特定公司和年份的Comm1到Comm7数据。
    """
    # 根据指定的公司名称和年份过滤数据
    filtered_df = df[(df['CompanyName'] == company_name) & (df['Year'] == int(year))]

    # 检查是否找到匹配的数据行
    if not filtered_df.empty:
        # 提取Comm1到Comm7的值
        comm_data = filtered_df.iloc[0][['Comm1', 'Comm2', 'Comm3', 'Comm4', 'Comm5', 'Comm6', 'Comm7']]
        # 转换为字典并返回
        return comm_data.to_dict()
    else:
        # 如果未找到数据则返回空字典
        return {}


def get_esg_scores_by_company(df, company_name):
    """
    获取指定公司所有年份的ESG评分，包括2024年的预测数据
    """
    # 根据公司名称过滤数据
    filtered_df = df[df['CompanyName'] == company_name]
    
    try:
        # 读取2024年的预测数据
        prediction_df = pd.read_csv('codes/Score08/ESGData_rating.csv')
        prediction_2024 = prediction_df[
            (prediction_df['CompanyName'] == company_name) & 
            (prediction_df['Year'] == 2024)
        ]['ESG_score'].values[0]
        
        # 如果公司数据存在
        if not filtered_df.empty:
            # 提取2020-2023年的数据
            years = filtered_df['Year'].tolist()
            scores = filtered_df['ESG_score'].tolist()
            
            # 添加2024年的预测数据
            years.append(2024)
            scores.append(prediction_2024)
            
            # 按年份排序
            sorted_data = sorted(zip(years, scores))
            years = [item[0] for item in sorted_data]
            scores = [item[1] for item in sorted_data]
            
            return years, scores
    except Exception as e:
        print(f"Error getting 2024 prediction: {str(e)}")
        
    # 如果出错或没有找到对应的数据，返回原始数据
    if not filtered_df.empty:
        years = filtered_df['Year'].tolist()
        scores = filtered_df['ESG_score'].tolist()
        return years, scores
    return [], []

def get_radar_chart_data(df, company_name, year):
    """
    获取指定公司和年份的雷达图数据
    
    Args:
        df: 包含雷达图数据的DataFrame
        company_name: 公司名称
        year: 年份
    """
    # 获取所有维度，从第十列开始（索引从9开始）
    dimensions = df.columns[9:].tolist()  # 从第十列开始，忽略前面的CompanyName和Year

    # 根据公司名称和年份过滤数据
    filtered_df = df[(df['CompanyName'] == company_name) & (df['Year'] == int(year))]

    if not filtered_df.empty:
        # 获取该公司该年份的各项指标值
        values = filtered_df.iloc[0][dimensions].values.tolist()

        # 设置最大值（根据实际数据或需求调整）
        max_values = [max(df[dim].max() for dim in dimensions)] * len(dimensions)

        # 返回ECharts所需数据
        chart_data = {
            "indicator": [{"name": dim, "max": max_val} for dim, max_val in zip(dimensions, max_values)],
            "seriesData": [{
                "name": company_name,
                "value": values
            }]
        }
        return chart_data
    else:
        return {"indicator": [], "seriesData": []}  # 如果没有数据，返回空数据
@app.route('/test0')
def index():
    company = request.args.get('company','Lenovo')
    year = request.args.get('year','2022')

    base_path = os.path.join(os.path.dirname(__file__), 'codes', 'Result','Before')
    comments = os.path.join(base_path,'ESGData_comments_beforeupload.csv')
    ratings = os.path.join(base_path, 'ESGData_rating_beforeupload.csv')
    leida = os.path.join(base_path, 'ESGData_detailedscore_beforeupload_Business owner.csv')

    comment_df = pd.read_csv(comments)
    score_df = pd.read_csv(ratings)
    leida_df = pd.read_csv(leida)
    leida_data = get_radar_chart_data(leida_df,company,year)
    esg_x,esg_y = get_esg_scores_by_company(score_df,company)



    p1 = get_image_data(os.path.join(base_path, 'cluster_means_esg_bar_chart__beforeupload.png'))
    p2 = get_image_data(os.path.join(base_path, 'Distribution_of_Return_Deviations__beforeupload.png'))
    p3 = get_image_data(os.path.join(base_path,'Risk_Level_Distribution__beforeupload.png'))
    results = {
        'p1':p1,
        'p2':p2,
        'p3':p3,
        'text':get_company_data(comment_df,company,year),
        'esg_x':esg_x,
        'esg_y':esg_y,
        'tables':list(zip(esg_x,esg_y)),
        'leida':leida_data
    }
    print(leida_data)

    return render_template('test0.html',result=results)



@app.route('/proc')
def proc():
    company = request.args.get('company', 'Lenovo')
    year = request.args.get('year', '2022')

    base_path = os.path.join(os.path.dirname(__file__), 'codes', 'Result', 'After')
    comments = os.path.join(base_path, 'ESGData_comments_afterupload.csv')
    ratings = os.path.join(base_path, 'ESGData_rating_afterupload.csv')
    leida = os.path.join(base_path, 'ESGData_detailedscore_afterupload_Business owner.csv')

    comment_df = pd.read_csv(comments)
    score_df = pd.read_csv(ratings)
    leida_df = pd.read_csv(leida)
    leida_data = get_radar_chart_data(leida_df, company, year)
    esg_x, esg_y = get_esg_scores_by_company(score_df, company)

    p1 = get_image_data(os.path.join(base_path, 'cluster_means_esg_bar_chart__afterupload.png'))
    p2 = get_image_data(os.path.join(base_path, 'Distribution_of_Return_Deviations__afterupload.png'))
    p3 = get_image_data(os.path.join(base_path, 'Risk_Level_Distribution__afterupload.png'))
    results = {
        'p1': p1,
        'p2': p2,
        'p3': p3,
        'text': get_company_data(comment_df, company, year),
        'esg_x': esg_x,
        'esg_y': esg_y,
        'tables': list(zip(esg_x, esg_y)),
        'leida': leida_data
    }

    return render_template('test3.html',result=results)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        # 这里可以添加分析报告的代码
        result = "Report uploaded successfully!"  # 进行分析并返回结果
        return redirect(url_for('proc'))
    return "NIF"


@app.route('/get_company_score')
def get_company_score():
    company_name = request.args.get("company")
    df = pd.read_csv(os.path.join(step9_path, 'ESGData_rating.csv'), usecols=["CompanyName", "Year", "ESG_score"])
    data = {}
    for name, group in df.groupby("CompanyName"):
        data[name] = {
            "years": group["Year"].tolist(),
            "scores": group["ESG_score"].tolist()
        }
    # 检查公司是否存在于数据中
    if company_name in data:
        return jsonify(data[company_name])
    else:
        return jsonify({"years": [], "scores": []})

@app.route('/process', methods=['get'])
def process():

    # step1
    # upload_path = os.path.join(UPLOAD_PATH,'Lenovo-2020-CN.pdf')
    # word_path = os.path.join(step1_path,'Lenovo-2020-CN.docx')
    # step1.pdf_to_word(upload_path,word_path)

    # step2
    # input_path =  os.path.join(step2_path,'Lenovo-2020-CN.docx')
    # step2.docx_to_txt(input_path,step2_path)

    # step3
    # value_csv_file_path = os.path.join(step3_path,'ESGValueKeywordsDic.csv')
    # unit_csv_file_path = os.path.join(step3_path,'ESGUnitKeywordsDic.csv')
    # step3.init_keyword_dic(value_csv_file_path, unit_csv_file_path)
    # step3.table_to_xlsx(os.path.join(step2_path,'Lenovo-2020-CN_table'), os.path.join(step3_path,'ESGDataOverall_RE.txt'),step3_path)

    #step4(!)
    # value_keywords = step4.load_value_keywords("ESGValueKeywordsDic.csv")
    # unit_keywords = step4.load_unit_keywords("ESGUnitKeywordsDic.csv")
    # report_info = step4.load_esg_report_list("ESGReportList.csv")
    # step4.process_txt_file(os.path.join(step4_path,"Lenovo-2020-CN.txt"), value_keywords, unit_keywords, report_info, os.path.join(step4_path,"ESGDataOverall_LLM.txt"))

    #step5
    #step5.combine_and_format_esg_data(os.path.join(step5_path,'ESGDataOverall_LLM.xlsx'), os.path.join(step5_path,'ESGDataOverall_RE.xlsx'),os.path.join(step5_path,'ESGDataOverall_Combine.xlsx'))

    #新闻分析(!)
    # source_folder = os.path.join(step6_path,'data','new_scrape')
    # destination_folder = os.path.join(step6_path,'data','sentiment')
    # step6.Sentiment_Analysis(source_folder, destination_folder)

    #聚类
    # file_path_data = os.path.join(step7_path,'ESGData_rating.csv')
    # step7.Cluster(file_path_data,step7_path)

    #风险评估(中断)
    # file_path =  os.path.join(step8_path,'ESGData_rating.csv')
    # new_data_path = os.path.join(step8_path,'new_data.csv')
    # step8.analysis(file_path, new_data_path,step8_path)

    #评分
    scores = read_esg_data(os.path.join(step9_path,'future_esg_predictions_2024.csv'))
    # print(os.path.join(step9_path,'future_esg_predictions_2024.csv'))

    #趋势图
    df = pd.read_csv(os.path.join(step9_path, 'ESGData_rating.csv'), usecols=["CompanyName"])
    companies = df['CompanyName'].drop_duplicates().tolist()  # 去重并转换为列表

    result = {
        'cluster1':get_image_data(os.path.join(step7_path,'cluster_means_esg_bar_chart.png')),
        'cluster2': get_image_data(os.path.join(step7_path, 'radar_chart.png')),
        'risk1':get_image_data(os.path.join(step8_path, 'Distribution_of_Return_Deviations.png')),
        'risk2': get_image_data(os.path.join(step8_path, 'Risk_Level_Distribution.png')),
        'scores':scores,
        'companies':companies

    }
    return render_template('test0.html',result=result)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    file = request.files.get('file')
    if file and file.filename:  # Ensure a file was selected
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        # Redirect after successful upload
        return f"File '{file.filename}' uploaded successfully!"
    else:
        # Redirect back to the upload page if no file was selected
        return redirect(url_for('upload_page'))
if __name__ == '__main__':
    app.run(debug=True)

@app.route('/get_radar_data', methods=['GET'])
def get_radar_data():
    company = request.args.get('company')  # 获取前端传递的公司
    year = request.args.get('year')        # 取端传递的年份
    if not company or not year:
        return jsonify({"error": "Invalid parameters"}), 400  # 参数校验

    # 调用获取雷达图数据的函数
    radar_data = get_radar_chart_data(company, year)
    return jsonify(radar_data)  # 返回 JSON 数据供前端绘制

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    try:
        data = request.get_json()
        role = data.get('role')
        print(f"1. Received role: {role}")
        
        file_path = os.path.join('codes', 'suggestion', 'ESG_suggestions.xlsx')
        print(f"2. Looking for file at: {file_path}")
        print(f"3. File exists: {os.path.exists(file_path)}")
        
        # 读取所有工作表名称
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        print(f"4. Available sheets: {sheets}")
        
        # 查找匹配的工作表名称（不区分大小写）
        sheet_name = None
        for sheet in sheets:
            if sheet.lower() == role.lower():
                sheet_name = sheet
                break
        
        if not sheet_name:
            return jsonify({"error": f"Sheet not found for role: {role}"}), 404
            
        print(f"5. Using sheet name: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"6. Successfully read sheet with shape: {df.shape}")
        
        suggestions = []
        for dimension in ['Environment', 'Social', 'Governance']:
            print(f"7. Processing dimension: {dimension}")
            # 使用模糊匹配查找维度
            dimension_rows = df[df['Dimension'].str.contains(dimension, case=False, na=False)]
            print(f"8. Found {len(dimension_rows)} rows for {dimension}")
            
            if not dimension_rows.empty:
                random_row = dimension_rows.sample(n=1).iloc[0]
                suggestion_cols = ['Suggestions', 'Suggestions.1', 'Suggestions.2']
                random_col = np.random.choice(suggestion_cols)
                suggestion = random_row[random_col]
                
                suggestions.append({
                    'index': dimension,
                    'text': str(suggestion)
                })
                print(f"9. Added suggestion for {dimension}: {suggestion}")
        
        print(f"10. Returning {len(suggestions)} suggestions")
        return jsonify({"suggestions": suggestions})
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
