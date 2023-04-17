import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# Create dummy data
data = pd.DataFrame({
    'region': ['North', 'South', 'East', 'West'] * 250,
    'function': ['HR', 'Finance', 'Sales', 'Engineering'] * 250,
    'satisfaction': [round(x, 1) for x in np.random.uniform(1, 5, 1000)],
    'risk_of_leaving': [round(x, 1) for x in np.random.uniform(0, 1, 1000)],
    'key_interventions': [np.random.choice(['Mentorship', 'Training', 'Promotion', 'Flexible Hours']) for _ in range(1000)],
    'topic': [np.random.choice(['Work-life balance', 'Career growth', 'Salary', 'Benefits']) for _ in range(1000)],
    'sentiment': [round(x, 1) for x in np.random.uniform(-1, 1, 1000)],
    'goals': [np.random.choice(['Management role', 'Become a specialist', 'Industry switch', 'Entrepreneurship']) for _ in range(1000)],
})

# Streamlit dashboard
st.title("Career Coaching Conversations Analytics Dashboard")

# Employee satisfaction by region
st.header("Employee Satisfaction by Region")
satisfaction_by_region = data.groupby("region").mean().reset_index()
fig1 = px.bar(satisfaction_by_region, x='region', y='satisfaction', title='Employee Satisfaction by Region')
st.plotly_chart(fig1)

# Risk of leaving by function
st.header("Risk of Leaving by Function")
risk_by_function = data.groupby("function").mean().reset_index()
fig2 = px.bar(risk_by_function, x='function', y='risk_of_leaving', title='Risk of Leaving by Function')
st.plotly_chart(fig2)

# Key interventions that company could make
st.header("Key Interventions")
interventions_count = data["key_interventions"].value_counts().reset_index()
fig3 = px.pie(interventions_count, values='key_interventions', names='index', title='Key Interventions')
st.plotly_chart(fig3)

# Most popular topics discussed
st.header("Most Popular Topics Discussed")
topics_count = data["topic"].value_counts().reset_index()
fig4 = px.bar(topics_count, x='index', y='topic', title='Most Popular Topics Discussed')
st.plotly_chart(fig4)

# Sentiment analysis
st.header("Sentiment Analysis")
fig5 = px.histogram(data, x="sentiment", nbins=20, title='Sentiment Analysis')
st.plotly_chart(fig5)

# Employee goals and aspirations
st.header("Employee Goals and Aspirations")
goals_count = data["goals"].value_counts().reset_index()
fig6 = px.bar(goals_count, x='index', y='goals', title='Employee Goals and Aspirations')
st.plotly_chart(fig6)
