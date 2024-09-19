import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, 
                             QPushButton, QVBoxLayout, QWidget, 
                             QComboBox, QHBoxLayout, QFormLayout)

class ESGVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ESG 报告可视化")
        self.setGeometry(100, 100, 800, 600)

        # 加载数据
        self.data = pd.read_csv("esg_data.csv", parse_dates=["date"])

        # 创建界面元素
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 用户身份切换
        self.user_combo = QComboBox()
        self.user_combo.addItems(["Investors", "Institutions","Companies"])
        layout.addWidget(QLabel("Indentity:"))
        layout.addWidget(self.user_combo)

        # 展示 ESG 评分
        self.score_label = QLabel(" ESG Score: {}".format(self.data['esg_score'].iloc[-1]))
        layout.addWidget(self.score_label)

        # 展示评分趋势
        self.plot_button = QPushButton("Trend Show")
        self.plot_button.clicked.connect(self.plot_trend)
        layout.addWidget(self.plot_button)

        # 风险评估
        self.risk_label = QLabel("Risk Exposure: {}".format(self.data['risk_assessment'].iloc[-1]))
        layout.addWidget(self.risk_label)

        # 建议
        self.recommendation_label = QLabel("Summar&Suggestions: {}".format(self.data['recommendation'].iloc[-1]))
        layout.addWidget(self.recommendation_label)

        # 设置布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def plot_trend(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.data['date'], self.data['esg_score'], marker='o')
        plt.title("Trend of ESG Score")
        plt.xlabel("Date")
        plt.ylabel("ESG Score")
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ESGVisualizer()
    window.show()
    sys.exit(app.exec_())