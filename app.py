from flask import Flask, render_template, request
import os

app = Flask(__name__)

# 上传文件保存路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        # 这里可以添加分析报告的代码
        result = "报告上传成功！"  # 进行分析并返回结果
        return result
    return "没有文件"

if __name__ == '__main__':
    app.run(debug=True)
