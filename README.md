This guide will walk you through setting up the **Automated ESG Data Extraction and Performance Analysis** project on your system.
## System Requirements
* **Operating System:** Windows, macOS, or Linux
* **Python Version:** 3.8 or higher
* **Additional Tools:**\
Git (for cloning the repository)\
Virtual environment manager (e.g., venv or virtualenv) recommended.\
Cloud host (with high-performance GPU): Because it takes too long to run the NLP model in `huggingface` and `transformers` locally, our team set up a server to run it using cloud host, so it is recommended to use it.\
Flask-compatible Server: If deploying to production, use a WSGI server like Gunicorn for a production environment.\

## Dependencies
The project relies on various Python libraries for PDF parsing, NLP, and data processing. Key dependencies include:
* `pdfplumber`
* `pandas`
* `scikit-learn`
* `transformers`
* `nltk`
* `docx`
* `PyPDF2`
* `flask`All dependencies are specified in the `requirements.txt` file. 

## Installation Steps
### Clone the Repository
First, clone the project repository to your local machine using Git:\
`git clone https://github.com/Geekliyi/DSS5105.git`\
`cd app`

### Install Dependencies
Once the virtual environment is active, install the required packages using the `requirements.txt` file:\
`pip install -r requirements.txt`

### Run Initial Setup Script
\
Our projects may include a setup script to initialize databases or download additional resources.\
Check the repository for any setup scripts and run them as needed:\
`python setup.py`

### Troubleshooting
If you encounter dependency issues, try updating pip and reinstalling:\
`pip install --upgrade pip`\
`pip install -r requirements.txt`

This quick-start guide will help you get the **Automated ESG Data Extraction and Performance Analysis project** up and running with minimal setup. Follow these steps to start using the main functionalities right away.
## Run the Program
Navigate to the project directory and run the main program:
`python app.py`

## Main Interface Overview
The main interface offers the following key functionalities:

* **Upload ESG Reports**: Users can upload a PDF file of an ESG report for analysis.
* **Start Analysis**: After uploading a report, users can initiate the analysis and view the results in the following sections:
1. Score Display
2. Trend Chart
3. Risk Assessment
4. Summary & Suggestions
* **Get Industry Insights**: Users can explore insights for specific companies based on their role (e.g., investor, government agency, business owner).

## Upload and New Analysis
Uploading a PDF File
* **Select a File:**
1. Click on the "Drag and Drop or Click Here to Upload" area.
2. Select a local ESG report in PDF format.
3. Once selected, the file name will appear in the upload area.
* **Start Analysis:**
1. Click the Start Analysis button to upload the file.
2. The system will process the report, extracting data and performing analysis.

## Get Industry Insights
* **Select Stakeholder Role:**
Users can select a role from the dropdown menu:
1. Investor
2. Government Agency
3. Business Owner
* **Choose Company and Year:**
1. Users can query ESG data for specific companies and years.
2. Tailored insights and recommendations are generated based on the selected role.

## Viewing Analysis Results
After uploading and analyzing the ESG report, the updated results are displayed in the respective sections:

* **Score Display:**
1.  The updated ESG score, along with a comparison to the industry average.
2.  ESG dimensions are visualized in a bar chart.
* **Trend Chart :**
1. The trend chart reflects the latest data points.
2. Changes in ESG scores over recent years are plotted.
* **Risk Assessment:**
1. The risk level and associated score are updated based on the analysis.
2. Additional visualizations (histogram and pie chart) reflect the latest data.
* **Summary & Suggestions:**
1. Actionable ESG improvement recommendations are displayed.
2. Suggestions are tailored to the user’s stakeholder role.
## Export Analysis Report
1. Click the Export Report button at the bottom of the page.
2. The system generates a PDF report containing:
* ESG score information.
* Trend charts and risk assessments.
* Recommendations for improving ESG performance.
3. Save or share the generated report for external use.
