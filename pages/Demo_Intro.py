import streamlit as st

st.header('Demo Overview')

st.markdown('''
#### Introduction

The tool is designed to democratise access to a career coach at any time, across a range of topics. The demo uses best practices for career coaching, and can be highly tailored to AIA's internal polices and target paths.

#### :dart: Objective

Guide employees to identify specific actions they can take for personal and professional development to meet their short and long-term career aspirations, at AIA or elsewhere.

#### :arrows_counterclockwise: Process

Users are asked background questions before selecting which topic they would like to focus on. Topics include career planning, specific challenges they are facing in their roles, personal development, managing teams, or starting a new postion.

Topics can easily be added or removed, and guidance adapted based on AIA policies.

The tool guides users through a series of thought provoking questions to help them identify areas of development and meaningful next steps they can take.

At the end of the session, the employee is given a summary of the discussion, and suggested action steps identified. 

#### :busts_in_silhouette: Target Audience 

[all employees]

''')


st.markdown('#### :art: Design')

st.markdown('**Discussion Length** :speech_balloon:')
st.select_slider(
    'Length',
    options=['Brief', 'Short', 'Moderate', 'Long', 'Extended'],
    value=('Moderate'), label_visibility='collapsed')

st.markdown('**Coaching Style**  :pencil:')
st.select_slider(
    'Coaching Type',
    options=['Problem Solving', 'Mentoring', 'Consulting', 'Advising', 'Guiding'],
    value=('Advising'), label_visibility='collapsed')

st.markdown('**Time Horizon** :calendar:')
st.select_slider(
    'Horizon',
    options=['Short-term', 'Mid-term', 'Long-term', 'Very Long-term', 'Lifetime'],
    value=('Mid-term'), label_visibility='collapsed')

link = 'Check it out here: https://career-coach.streamlit.app/'
st.markdown(link, unsafe_allow_html=True)