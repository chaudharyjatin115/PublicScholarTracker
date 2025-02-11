import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_education_distribution_chart(df):
    if df.empty:
        return px.pie(title='No data available')
    location_counts = df['education_location'].value_counts()
    fig = px.pie(
        values=location_counts.values,
        names=location_counts.index,
        title='Distribution of Education Locations',
        hole=0.3
    )
    return fig

def create_yearly_trends(df):
    if df.empty:
        return px.line(title='No data available')
    yearly_data = df.groupby(['joining_year', 'education_location']).size().unstack(fill_value=0)
    fig = px.line(
        yearly_data,
        title='Yearly Trends in Educational Background',
    )
    return fig

def create_department_education_heatmap(df):
    if df.empty:
        return px.imshow(title='No data available')
    dept_edu = pd.crosstab(df['department'], df['education_location'])
    fig = px.imshow(
        dept_edu,
        title='Department vs Education Location Distribution',
        aspect='auto',
        color_continuous_scale='viridis'
    )
    return fig

def get_western_education_stats(df):
    """Calculate western education statistics with error handling"""
    western_countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France']
    western_educated = df[df['education_location'].isin(western_countries)]

    total_officers = len(df)
    total_western = len(western_educated)

    stats = {
        'Total Officers': total_officers,
        'Western Educated': total_western,
        'Percentage Western Educated': f"{(total_western / total_officers * 100):.1f}%" if total_officers > 0 else "0.0%",
        'Top Western Country': western_educated['education_location'].mode().iloc[0] if not western_educated.empty else 'N/A',
        'Most Common Degree': western_educated['degree_level'].mode().iloc[0] if not western_educated.empty else 'N/A'
    }
    return stats