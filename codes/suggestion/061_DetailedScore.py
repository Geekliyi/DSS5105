import pandas as pd

rating_data = pd.read_csv("ESGData_rating_afterupload.csv")
framework = pd.read_excel("ESG_disclosure_framework_refined.xlsx")

role_type = input("Input role:（Investor, Government agency, Business Owner）：")

weight_column = {"Investor": "Investor", "Government agency": "Government agency", "Business Owner": "Business Owner"}[role_type]

weights = framework[[weight_column, "2rd indicators"]].set_index("2rd indicators")

detailed_scores = rating_data[["Company_ID", "CompanyName", "ESG_score", "Country", "Sector", "Industrygroup", "Industry", "Language", "Year"]].copy()

for indicator, row in weights.iterrows():
    weight = row[weight_column]
    if weight > 0:
        detailed_scores[indicator] = detailed_scores["ESG_score"] * weight

detailed_scores.to_csv("ESGData_detailedscore_afterupload.csv", index=False)