import streamlit as st
import pandas as pd


def initiate_states():

    # Create default session states

    if 'state' not in ss:
        ss['state'] = "intro"

    if 'current_topic' not in ss:
        ss['current_topic'] = {}

    if 'counts' not in ss:
        ss['counts'] = 1


def load_data():

    # Load the Excel file
    excel_file = pd.ExcelFile('data.xlsx', engine='openpyxl')

    # Get the list of sheet names
    sheet_names = excel_file.sheet_names

    for table_name in sheet_names:
        if table_name not in ss:
            df = pd.read_excel(excel_file, sheet_name=table_name, index_col=0)
            ss[table_name] = df


def load_questions():
    ss.load_questions = True


ss = st.session_state
