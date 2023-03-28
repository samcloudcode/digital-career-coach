import streamlit as st

st.header('Digital Career Coach Demo')

st.markdown('''
**Introduction**


**Objective**


**Target Audience**


''')

st.markdown('**Design**')
st.select_slider(
    'Coaching Type',
    options=['Guide', 'Guiding', 'Balanced', 'More Solution', 'Provide Solution'],
    value=('Guiding'), label_visibility='collapsed')

st.markdown('**Length**')
st.select_slider(
    'Length',
    options=['Shorter', 'Short', 'Balanced', 'Long', 'Longer'],
    value=('Balanced'), label_visibility='collapsed')

st.markdown('**Horizon**')
st.select_slider(
    'Horizon',
    options=['Short Term', 'Short', 'Balanced', 'Long', 'Long Term'],
    value=('Short'), label_visibility='collapsed')

