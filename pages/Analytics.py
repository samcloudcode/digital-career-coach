import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Create dummy data
np.random.seed(42)
num_entries = 1000
functions = ['Actuarial', 'Agency', 'Human Resources', 'Risk and Compliance', 'Finance', 'Technology']
markets = ['Hong Kong', 'Singapore', 'Thailand', 'Australia']
date_range = pd.date_range(start='2020-01-01', end='2023-01-01', freq='M')
topics = ['interviews', 'stress', 'promotions', 'work-life balance', 'career growth', 'workload']

data = pd.DataFrame({
    'date': np.random.choice(date_range, size=num_entries),
    'function': np.random.choice(functions, size=num_entries),
    'market': np.random.choice(markets, size=num_entries),
    'active_users': np.random.randint(1, 500, size=num_entries),
    'retention_risk': np.random.random(size=num_entries),
    'job_satisfaction': np.random.randint(1, 11, size=num_entries),
    'company_satisfaction': np.random.randint(1, 11, size=num_entries),
    'sentiment': np.random.choice(['positive', 'neutral', 'negative'], size=num_entries),
    'key_theme': np.random.choice(topics, size=num_entries),
    'employee_concern': np.random.choice(topics, size=num_entries),
    'goals_set': np.random.randint(1, 11, size=num_entries),
    'goals_achieved': np.random.randint(0, 11, size=num_entries),
    'professional_development': np.random.randint(1, 11, size=num_entries),
    'feedback_interactions': np.random.randint(1, 11, size=num_entries)
})

# Streamlit app
st.title("HR Admin Dashboard")

# Select functions and markets
selected_functions = st.multiselect("Select Functions:", options=functions, default=functions)
selected_markets = st.multiselect("Select Markets:", options=markets, default=markets)
filtered_data = data[(data['function'].isin(selected_functions)) & (data['market'].isin(selected_markets))]

# Create columns
left_column, right_column = st.beta_columns(2)

# Usage Over Time
left_column.subheader("Users")
usage_over_time = filtered_data.groupby(['date', 'function', 'market'])['active_users'].sum().reset_index()
fig1 = px.line(usage_over_time, x='date', y='active_users', color='function', facet_col='market', title='Usage Over Time')
left_column.plotly_chart(fig1)

# Retention Risk
right_column.subheader("Retention Risk")
fig2 = px.box(filtered_data, x='function', y='retention_risk', color='function', facet_col='market', title='Retention Risk')
right_column.plotly_chart(fig2)

# Job Satisfaction
left_column.subheader("Job Satisfaction")
fig3 = px.histogram(filtered_data, x='job_satisfaction', color='function', facet_col='market', title='Job Satisfaction')
left_column.plotly_chart(fig3)

# Company Satisfaction
right_column.subheader("Company Satisfaction")
fig4 = px.histogram(filtered_data, x='company_satisfaction', color='function', facet_col='market', title='Company Satisfaction')
right_column.plotly_chart(fig4)

# Sentiment Analysis
left_column.subheader("Sentiment Analysis")
sentiment_counts = filtered_data.groupby(['function', 'market', 'sentiment']).size().reset_index(name='count')
fig5 = px.sunburst(sentiment_counts, path=['market', 'function', 'sentiment'], values='count', title='Sentiment Analysis')
left_column.plotly_chart(fig5)

# Key Themes Discussed
right_column.subheader("Key Themes Discussed")
theme_counts = filtered_data['key_theme'].value_counts().to_dict()
wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis')
wordcloud = wc.generate_from_frequencies(theme_counts)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
right_column.pyplot(plt)

# Employee Concerns
left_column.subheader("Employee Concerns")
concern_counts = filtered_data.groupby(['function', 'market', 'employee_concern']).size().reset_index(name='count')
fig7 = px.bar(concern_counts, x='employee_concern', y='count', color='employee_concern', barmode='group', facet_col='market', facet_row='function', title='Employee Concerns')
left_column.plotly_chart(fig7)

# Goals and Achievements
right_column.subheader("Goals and Achievements")
fig8 = px.scatter(filtered_data, x='goals_set', y='goals_achieved', color='function', facet_col='market', title='Goals and Achievements')
right_column.plotly_chart(fig8)

# Chart 9 - Professional Development
st.subheader("Professional Development")
prof_dev_counts = filtered_data['professional_development'].value_counts().reset_index()
prof_dev_counts.columns = ['development_level', 'count']
fig9 = px.bar(prof_dev_counts, x='development_level', y='count', title='Professional Development', color='count', color_continuous_scale='viridis')
st.plotly_chart(fig9)

# Chart 10 - Feedback and Coaching Interactions
st.subheader("Feedback and Coaching Interactions")
fig10 = px.scatter(filtered_data, x='feedback_interactions', y='sentiment', color='function', title='Feedback and Coaching Interactions')
st.plotly_chart(fig10)
