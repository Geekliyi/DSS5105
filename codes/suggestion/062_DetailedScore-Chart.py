import pandas as pd
import plotly.graph_objects as go

framework = pd.read_excel("ESG_disclosure_framework_refined.xlsx")

def plot_radar_chart(company_name, year, framework, dimension="All"):
    data = pd.read_csv("ESGData_detailedscore_beforeupload.csv")

    selected_data = data[(data["CompanyName"] == company_name) & (data["Year"] == year)]

    dimensions = {
        "E": framework.iloc[1:8]["2rd indicators"].dropna().values,
        "S": framework.iloc[8:17]["2rd indicators"].dropna().values,
        "G": framework.iloc[17:25]["2rd indicators"].dropna().values,
        "O": framework.iloc[25:33]["2rd indicators"].dropna().values
    }

    if dimension == "All":
        indicators = [item for sublist in dimensions.values() for item in sublist]
    else:
        indicators = dimensions[dimension]

    indicators = [ind for ind in indicators if ind in selected_data.columns]

    scores = selected_data[indicators].values.flatten().tolist()

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=indicators,
        fill='toself',
        name=f'{company_name} - {year} {dimension} Score',
        line=dict(color='lightblue'),
        hovertemplate="<b>%{theta}</b><br>Score: %{r}<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(
                tickmode='array',
                tickvals=[i for i in range(len(indicators))],
                ticktext=indicators,
                rotation=90,
                dtick=1
            )
        ),
        showlegend=True,
        title=f"{company_name} - {year} {dimension} Radar Chart",
        updatemenus=[{
            'buttons': [
                {'label': 'All', 'method': 'relayout', 'args': ['polar.angularaxis.tickvals', [i for i in range(len(indicators))]]},
                {'label': 'E', 'method': 'relayout', 'args': ['polar.angularaxis.tickvals', [i for i in range(len(dimensions["E"]))]]},
                {'label': 'S', 'method': 'relayout', 'args': ['polar.angularaxis.tickvals', [i for i in range(len(dimensions["S"]))]]},
                {'label': 'G', 'method': 'relayout', 'args': ['polar.angularaxis.tickvals', [i for i in range(len(dimensions["G"]))]]},
                {'label': 'O', 'method': 'relayout', 'args': ['polar.angularaxis.tickvals', [i for i in range(len(dimensions["O"]))]]}
            ],
            'direction': 'down',
            'showactive': True,
            'active': 0,
            'x': 0.17,
            'xanchor': 'left',
            'y': 1.15,
            'yanchor': 'top'
        }]
    )

    fig.show()

company_name = input("Company name：")
year = int(input("Year："))
dimension = "All"
plot_radar_chart(company_name, year, framework, dimension)
