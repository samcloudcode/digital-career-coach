import streamlit as st
import pandas as pd

def initiate_states():

    # Create default session states
    if 'messages' not in ss:
        ss['messages'] = [
            {"role": "system", "content": ss.prompts.loc['system_message', 'prompt']},
        ]

    if 'state' not in ss:
        ss['state'] = "Intro"

    if 'model_reply' not in ss:
        ss['model_reply'] = ""

    if 'user_reply' not in ss:
        ss['user_reply'] = ""

    if 'current_topic' not in ss:
        ss['current_topic'] = {}

    if 'topics' not in ss:
        ss['topics'] = {}

    if 'counts' not in ss:
        ss['counts'] = 1

    if 'user_info' not in ss:
        ss['user_info'] = {}

    if 'load_questions' not in ss:
        ss['load_questions'] = False


def load_data():

    for table_name in ('pages', 'topic_prompts', 'prompts', 'functions', 'bands', 'aia_info'):

        if table_name not in ss:
            df = pd.read_excel('data.xlsx', sheet_name=table_name, engine='openpyxl', index_col=0)
            ss[table_name] = df


def load_questions():
    ss.load_questions = True




ss = st.session_state
