import pandas as pd
import random

# Load the ESG data and suggestions
esg_data = pd.read_csv('ESGData_detailedscore_afterupload.csv')
esg_suggestions = pd.read_excel('ESG_suggestions.xlsx', sheet_name=None)

# Check the shape of the 'Investor' dataframe to debug index issues
print(esg_suggestions['Investor'].shape)

# Define dimension ranges outside of functions so they can be accessed globally
dimension_ranges = {
    'E': range(0, 8),  # Adjust to fit actual data
    'S': range(8, 16),
    'G': range(16, 24),
    'O': range(24, 33)  # Adjust these ranges if necessary
}


# Function to get company scores for a given year
def get_company_scores(company_name, year):
    company_name = company_name.strip().lower()
    company_data = esg_data[
        (esg_data['CompanyName'].str.strip().str.lower() == company_name) & (esg_data['Year'] == year)]

    if company_data.empty:
        raise ValueError(f"No data found for company '{company_name}' in year {year}")

    # Return the scores for the selected company and year
    return company_data.iloc[:, 9:].values.flatten(), company_data.columns[9:]


# Function to get industry average scores for a given year
def get_industry_average(year):
    industry_avg = esg_data[esg_data['Year'] == year].iloc[:, 9:].mean()
    return industry_avg


# Function to get suggestions based on role, indicator, and dimension
def get_suggestions(role, indicator, dimension):
    suggestions_df = esg_suggestions[role]

    # Find the corresponding suggestion for the indicator within the dimension range
    try:
        dimension_indicators = suggestions_df.iloc[dimension_ranges[dimension], 0].values
        if indicator in dimension_indicators:
            indicator_row = suggestions_df[
                suggestions_df.iloc[:, 0].str.strip().str.lower() == indicator.strip().lower()]
            if not indicator_row.empty:
                # Randomly select a suggestion for the indicator
                return random.choice(indicator_row.iloc[:, 1:4].values.flatten())
    except KeyError:
        return f"No suggestions available for the indicator '{indicator}'"

    return f"No suggestions available for the indicator '{indicator}'"


# Function to get the dimension of the indicator
def get_indicator_dimension(indicator):
    if indicator in esg_suggestions['Investor'].iloc[0:8, 0].values:
        return 'E'
    elif indicator in esg_suggestions['Investor'].iloc[8:16, 0].values:
        return 'S'
    elif indicator in esg_suggestions['Investor'].iloc[16:24, 0].values:
        return 'G'
    elif indicator in esg_suggestions['Investor'].iloc[24:32, 0].values:
        return 'O'
    return 'Unknown'


# Main function to compare company scores with industry average and provide suggestions
def compare_performance(company_name, year, role):
    # Get the company scores and column names (indicators)
    company_scores, indicators = get_company_scores(company_name, year)

    # Get the industry average scores
    industry_avg = get_industry_average(year)

    # Compare company scores to industry averages and filter out the bottom 5 indicators
    comparison = [(indicator, company_score, industry_avg[indicator])
                  for indicator, company_score in zip(indicators, company_scores)
                  if company_score < industry_avg[indicator]]

    comparison_sorted = sorted(comparison, key=lambda x: x[1])  # Sort by company score (lowest first)

    if not comparison_sorted:
        print(f"The company '{company_name}' is performing excellently in {year}. Keep up the great work!")

        # Check if the company is performing well in all indicators of each dimension
        for dimension in ['E', 'S', 'G', 'O']:
            dimension_indicators = esg_suggestions['Investor'].iloc[dimension_ranges[dimension], 0].values
            dimension_scores = []

            for indicator in dimension_indicators:
                try:
                    index = indicators.tolist().index(indicator)
                    dimension_scores.append((indicator, company_scores[index]))
                except ValueError:
                    print(f"Warning: Indicator '{indicator}' not found in the indicators list.")
                    continue

            # Check if all indicators in the dimension are above the industry average
            if all(company_score >= industry_avg[indicator] for indicator, company_score in dimension_scores):
                print(f"Great job in the {dimension} dimension! Keep up the excellent work in {dimension}.")

                # Randomly provide suggestions for that dimension
                dimension_suggestions = random.sample(dimension_indicators.tolist(), 3)  # Select 3 random suggestions
                for indicator in dimension_suggestions:
                    suggestion = get_suggestions(role, indicator, dimension)
                    print(f"Indicator: {indicator} - Suggestion: {suggestion}")

        return

    # Display the 5 indicators with the worst performance
    print(f"Top 5 underperforming indicators for '{company_name}' in {year}:")
    for indicator, company_score, avg_score in comparison_sorted[:5]:
        print(f"Indicator: {indicator}, Company Score: {company_score}, Industry Average: {avg_score}")

        # Determine the dimension of the indicator
        dimension = get_indicator_dimension(indicator)

        # Get suggestions for improvement based on the role and dimension
        suggestion = get_suggestions(role, indicator, dimension)
        print(f"Suggestion: {suggestion}\n")


# User input
company_name = input("Enter the company name: ")
year = int(input("Enter the year: "))
role = input("Enter your role (Investor, Government Agency, Business Owner): ")

# Call the main function with the user's input
compare_performance(company_name, year, role)