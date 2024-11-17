import os
import re
import csv
import time
from transformers import pipeline
from statistics import mean
import pandas as pd
from openpyxl import Workbook

year_error_list = [2019, 2020, 2021, 2022, 2023, 2024, 2025,
                   201920, 202021, 202122, 202223, 202324, 202425,
                   19, 20, 21, 22, 23, 24, 25]

# Step 0: Read the filename
def parse_filename(file_name):
    parts = file_name.split('-')
    company = parts[0]
    year = re.findall(r'\d+', parts[1])
    lang = parts[2][:2]  # 'EN' or 'CN'
    return company, year[0], lang

# Step 1: Read value keywords from CSV document
def load_value_keywords(file_path):
    value_keywords = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        next(reader)
        for row in reader:
            index = row[0]
            keywords = [kw.strip() for kw in row[1:] if kw.strip()]
            if keywords:
                value_keywords[index] = keywords
    return value_keywords

# Step 1.1: Read unit keywords from CSV document
def load_unit_keywords(file_path):
    unit_keywords = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        next(reader)
        for row in reader:
            index = row[0]
            keywords = [kw.strip() for kw in row[1:] if kw.strip()]
            if keywords:
                unit_keywords[index] = keywords
    return unit_keywords

# Step 2: Read ESG report list to get country, sector, industry info
def load_esg_report_list(file_path):
    report_info = {}
    with open(file_path, mode='r', encoding='gb18030') as file:
        reader = csv.DictReader(file)
        for row in reader:
            company = row['CompanyName']
            report_info[company] = {
                'Country': row['Country'],
                'Sector': row['Sector'],
                'Industrygroup': row['Industrygroup'],
                'Industry': row['Industry']
            }
    return report_info

# Step 3: Set LLM questions
def setup_questions(year, keywords, lang):
    if lang == 'EN':
        return [f"{year} {keyword}" for keyword in keywords if re.match(r'[a-zA-Z]', keyword)]
    elif lang == 'CN':
        return [f"{year} {keyword}" for keyword in keywords if re.match(r'[\u4e00-\u9fff]', keyword)]

# Step 4: Process a single txt file and write results to file
def process_txt_file(file_path, value_keywords, unit_keywords, report_info, output_file):
    report_no = 1
    start_time = time.time()
    qualitative_indices = ['G-04', 'G-05', 'G-06', 'G-08']
    rows = []

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header line
        header = "ReportNo;CompanyName;Country;Sector;Industrygroup;Industry;Language;Year;" \
                 + ";".join([f"{index}_value;{index}_unit" for index in value_keywords.keys()])
        f.write(header + "\n")

        try:
            company, year, lang = parse_filename(os.path.basename(file_path))
        except ValueError as e:
            print(f"Error parsing filename {file_path}: {e}")
            return

        # Get ESG report information
        report_data = report_info.get(company, {'Country': 'NA', 'Sector': 'NA', 'Industrygroup': 'NA',
                                                'Industry': 'NA'})

        if lang == 'EN':
            qa_model = pipeline("question-answering",
                                model="bert-large-uncased-whole-word-masking-finetuned-squad")
        elif lang == 'CN':
            qa_model = pipeline("question-answering", model="uer/roberta-base-chinese-extractive-qa")
        else:
            print(f"Unrecognized language suffix for {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as txt_file:
            txt_content = txt_file.read()

        row_data = [str(report_no), company, report_data['Country'], report_data['Sector'],
                    report_data['Industrygroup'], report_data['Industry'], lang, year]

        total_indicators = len(value_keywords)
        processed_indicators = 0

        for index, keywords in value_keywords.items():
            if index in qualitative_indices:
                found = any(keyword in txt_content for keyword in keywords)
                if found:
                    processed_value = 1
                else:
                    processed_value = "0"
                matched_unit = "TF"
            else:
                questions = setup_questions(year, keywords, lang)
                results = []
                for question in questions:
                    result = qa_model(question=question, context=txt_content)
                    numeric_value = extract_numeric_value(result['answer'], year, year_error_list)
                    if numeric_value is not None:
                        results.append(numeric_value)

                if results:
                    processed_value = process_results(results)
                else:
                    processed_value = "NA"

                unit_questions = setup_questions(year, unit_keywords.get(index, []), lang)
                if unit_questions:
                    unit_result = []
                    for question in unit_questions:
                        result = qa_model(question=question, context=txt_content)
                        unit_result.append(result['answer'])

                    if unit_result:
                        matched_unit = match_unit(unit_result[0], unit_keywords.get(index, []))
                    else:
                        matched_unit = "NA"
                else:
                    matched_unit = "NA"

                if processed_value == "NA":
                    matched_unit = "NA"

            row_data.extend([str(processed_value), matched_unit])

            processed_indicators += 1
            print(f"{file_path} has been analyzed: {processed_indicators}/{total_indicators} indicators processed", end='\r')

        f.write(";".join(row_data) + "\n")
        rows.append(row_data)

        report_no += 1

        file_duration = (time.time() - start_time) / 60
        print(f"\n{file_path} has been analyzed in {file_duration:.2f} minutes.")

    save_to_excel(output_file.replace(".txt", ".xlsx"), header.split(";"), rows)

    total_duration = (time.time() - start_time) / 60
    print(f"Document has been analyzed in {total_duration:.2f} minutes.")

# Step 5: Extract numeric values
def extract_numeric_value(answer, year, error_years):
    answer = re.sub(rf'{year}', '', answer)
    answer = re.sub(r'[^\d\s|]', '', answer)

    if '|' in answer:
        parts = answer.split('|')
        numeric_values = [float(part.strip().replace(',', '')) for part in parts if
                          part.strip().replace(',', '').isdigit()]
        if len(numeric_values) >= 2:
            answer = min(numeric_values[0], numeric_values[-1])
        elif len(numeric_values) == 1:
            answer = numeric_values[0]
        else:
            answer = None

    elif ' ' in answer:
        parts = answer.split()
        numeric_values = [float(part.strip().replace(',', '')) for part in parts if
                          part.strip().replace(',', '').isdigit()]
        if len(numeric_values) >= 2:
            answer = min(numeric_values[0], numeric_values[-1])
        elif len(numeric_values) == 1:
            answer = numeric_values[0]
        else:
            answer = None

    else:
        stripped_answer = answer.strip().replace(',', '')
        if stripped_answer.isdigit():
            answer = float(stripped_answer)
        else:
            answer = None

    if answer in error_years:
        return None

    if answer is None or answer <= 1:
        return None

    return answer

# Step 6: Match the unit
def match_unit(answer, unit_keywords):
    if not unit_keywords:
        return "NA"

    best_match = None
    for unit in unit_keywords:
        if unit in answer:
            best_match = unit
            break

    return best_match if best_match else unit_keywords[0]

# Step 7: Process results
def process_results(results):
    if len(results) < 2:
        return results[0] if results else None
    avg_value = mean(results)
    return round(avg_value)

# Step 8: Save to Excel
def save_to_excel(file_name, headers, data):
    df = pd.DataFrame(data, columns=headers)
    df.to_excel(file_name, index=False)

# value_keywords = load_value_keywords("ESGValueKeywordsDic.csv")
# unit_keywords = load_unit_keywords("ESGUnitKeywordsDic.csv")
# report_info = load_esg_report_list("ESGReportList.csv")
#
# # Change this to the specific txt file you want to process
# process_txt_file("Lenovo-2020-CN.txt", value_keywords, unit_keywords, report_info, "ESGDataOverall_LLM.txt")