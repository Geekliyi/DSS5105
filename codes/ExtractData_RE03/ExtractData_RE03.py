import re
import os
import csv
import time
import difflib
import pandas as pd

value_keyword_dic = {}
unit_keyword_dic = {}
expanded_keyword_list = {}


ShouldOutPutFirstValue = 0

def read_csv_to_dict(csv_file_path, max_rows=28):
    result_dict = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row_count, row in enumerate(reader):
            if row_count >= max_rows:
                break
            if row:
                key = row[0]
                values = [value for value in row[1:] if value.strip()]
                result_dict[key] = values
    return result_dict

def init_keyword_dic(value_csv_file_path, unit_csv_file_path):
    global value_keyword_dic
    global unit_keyword_dic

    value_keyword_dic = read_csv_to_dict(value_csv_file_path)
    print('ESG value keywords dictionary is initialized.')
    print(value_keyword_dic)

    unit_keyword_dic = read_csv_to_dict(unit_csv_file_path)
    print('ESG unit keywords dictionary is initialized.')
    print(unit_keyword_dic)

def find_most_similar_unit(surrounding_text, unitwords_list, similarity_threshold=0.01):
    most_similar_unit = None
    highest_similarity = 0.0

    for unit in unitwords_list:
        similarity = difflib.SequenceMatcher(None, unit, surrounding_text).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_unit = unit

    if highest_similarity >= similarity_threshold:
        return most_similar_unit

def expand_keyword(text, keyword):
    pattern = fr'{re.escape(keyword)}(.*?)\|'
    match = re.search(pattern, text)
    if match:
        return keyword + match.group(1)
    else:
        return keyword

def get_years_order(text, keywordsdic=value_keyword_dic):
    global ShouldOutPutFirstValue
    ShouldOutPutFirstValue = -1  # Avoid invalid output
    year_keywords_list = keywordsdic['Year']

    for year in year_keywords_list:
        if re.search(re.escape(year), text, re.IGNORECASE):
            year_pattern = re.compile(fr'^{re.escape(year)}\s*\|\s*(.*?)$', re.MULTILINE)
            year_match = year_pattern.search(text)

            if year_match:
                years = year_match.group(1).split('|')
                years = [year.strip() for year in years]
                cleaned_years = [re.sub(r'\D', '', year) for year in years]
                try:
                    int_years = list(map(int, cleaned_years))
                    if int_years == sorted(int_years):
                        ShouldOutPutFirstValue = -1
                    else:
                        ShouldOutPutFirstValue = 1
                except ValueError:
                    ShouldOutPutFirstValue = 1
                break
    return ShouldOutPutFirstValue

def remove_newlines_from_list(lst):
    return [item.replace('\n', '') for item in lst]

def extract_info_basedon_keyword(text, key_name, valuewords_list, unitwords_list, ShouldOutPutFirstValue):
    value = 0
    unit = ''
    expanded_text_list = []
    found_value = False
    found_unit = False

    for keyword in valuewords_list:
        expanded_text = expand_keyword(text, keyword)
        expanded_text_list.append(expanded_text)

    for expanded_text in expanded_text_list:
        if found_value:
            break
        pattern = fr'{re.escape(expanded_text)}[,. $|0-9\n]*'
        match = re.search(pattern, text)

        if match:
            orign_text = match.group(0)
            parts_text = orign_text.split('|')
            parts_text = remove_newlines_from_list(parts_text)

            if len(parts_text) > 1:
                match_start = match.start()
                match_end = match.end()
                surrounding_text = text[max(0, match_start - 30): min(len(text), match_end + 30)]
                pattern_doublecheck = re.compile(r'[^0-9A-Za-z\s\.,\$]')

                if not found_value:
                    value = parts_text[ShouldOutPutFirstValue].strip()
                    if value != expanded_text:
                        found_value = True
                    else:
                        value = '\\'

                if not found_unit and found_value:
                    most_similar_unit = find_most_similar_unit(surrounding_text, unitwords_list)

                    if most_similar_unit:
                        unit = most_similar_unit
                        found_unit = True

    if not found_value:
        value = "\\"
    if not found_unit:
        unit = "\\"
    return value, unit

def get_company_info(folder_name,base_dir):
    esg_report_list = pd.read_csv(os.path.join(base_dir,'ESGReportList.csv'), encoding='ISO-8859-1')
    company_name = folder_name.split('-')[0]
    company_info = esg_report_list[esg_report_list['CompanyName'] == company_name]
    if not company_info.empty:
        return company_info.iloc[0][['Country', 'Sector', 'Industrygroup', 'Industry']].tolist()
    return ['N/A', 'N/A', 'N/A', 'N/A']

def table_to_xlsx(source_folder, destination_txt,base_dir):
    global ShouldOutPutFirstValue
    successful_transfer_times = 0
    combined_data = []

    with open(destination_txt, 'a', encoding='utf-8', newline='') as output_file:
        csv_writer = csv.writer(output_file)
        header = ['ReportNo', 'CompanyName', 'Country', 'Sector', 'Industrygroup', 'Industry', 'Language', 'Year']
        for key in value_keyword_dic.keys():
            if key != 'Year':
                header.append(f"{key}_value")
                header.append(f"{key}_unit")
        output_file.write(';'.join(header) + '\n')

        country, sector, industrygroup, industry = get_company_info(os.path.basename(source_folder),base_dir)

        for filename in os.listdir(source_folder):
            if filename.endswith('.txt'):
                txt_path = os.path.join(source_folder, filename)
                data_row = [''] * (8 + (len(value_keyword_dic) - 1) * 2)
                data_row[0] = successful_transfer_times + 1
                data_row[1] = os.path.basename(source_folder).split('-')[0]
                data_row[2] = country
                data_row[3] = sector
                data_row[4] = industrygroup
                data_row[5] = industry

                with open(txt_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    if ShouldOutPutFirstValue == 0:
                        ShouldOutPutFirstValue = get_years_order(text, value_keyword_dic)

                    col_index = 8
                    for key in value_keyword_dic:
                        if key != 'Year':
                            valuewords_list = value_keyword_dic[key]
                            unitwords_list = unit_keyword_dic[key]
                            value, unit = extract_info_basedon_keyword(text, key, valuewords_list, unitwords_list,
                                                                       ShouldOutPutFirstValue)

                            if (data_row[col_index] == '' or data_row[col_index] == '\\') and value != '\\':
                                data_row[col_index] = value
                            if (data_row[col_index + 1] == '' or data_row[col_index + 1] == '\\') and unit != '\\':
                                data_row[col_index + 1] = unit
                            col_index += 2

                combined_data.append(data_row)
                successful_transfer_times += 1
                ShouldOutPutFirstValue = 0

    final_data_row = [''] * (8 + (len(value_keyword_dic) - 1) * 2)
    for row in combined_data:
        for i in range(len(row)):
            if row[i] and (final_data_row[i] == '' or final_data_row[i] == '\\'):
                final_data_row[i] = row[i]

    with open(destination_txt, 'a', encoding='utf-8', newline='') as output_file:
        csv_writer = csv.writer(output_file)
        header = ['ReportNo', 'CompanyName', 'Country', 'Sector', 'Industrygroup', 'Industry', 'Language', 'Year']
        for key in value_keyword_dic.keys():
            if key != 'Year':
                header.append(f"{key}_value")
                header.append(f"{key}_unit")
        output_file.write(';'.join(header) + '\n')

        output_file.write(';'.join(map(str, final_data_row)) + '\n')

    df = pd.read_csv(destination_txt, sep=';', header=0, skiprows=1)
    df.to_excel(destination_txt.replace(".txt", ".xlsx"), index=False)

# start_time = time.time()
#
# value_csv_file_path = 'ESGValueKeywordsDic.csv'
# unit_csv_file_path = 'ESGUnitKeywordsDic.csv'
# init_keyword_dic(value_csv_file_path, unit_csv_file_path)
