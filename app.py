import streamlit as st
import openai
import time
import pandas as pd
import os

# Import functions
from state_handling import initiate_states, load_data


def change_state(new_state):
    ss.state = new_state
    st.experimental_rerun()


def display_headers():

    if not pd.isna(ss.pages.loc[ss.state, 'title']):
        st.title(ss.pages.loc[ss.state, 'title'])

    if not pd.isna(ss.pages.loc[ss.state, 'subheader']):
        st.subheader(ss.pages.loc[ss.state, 'subheader'])

    if not pd.isna(ss.pages.loc[ss.state, 'markdown']):
        st.markdown(ss.pages.loc[ss.state, 'markdown'])


def render_logo():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100)


def next_coaching_question():
    """Updates the prompt messages and moves to next page"""
    if len(ss.chat_coach.user_reply) > 3:
        ss.chat_coach.add_user_reply()
        ss.counts = ss.counts + 1
        st.session_state["reply"] = ""
    else:
        st.error('To facilitate a more meaningful discussion, '
                 'please include more information in your response.')


def back_to_summary():
    ss.state = 'intro'
    summary_prompt = ss.prompts.loc['summary_prompt', 'prompt']\
        .format(topic=ss.user_session.active_topic,
                max_questions=ss.topics.loc[ss.user_session.active_topic, 'max_questions'])

    ss.chat_coach.add_prompt(summary_prompt)
    ss.user_session.active_topic_answered(True)
    ss.counts = 1


class UserSession:
    def __init__(self, topics, summaries):
        self.topics = {}
        self.summaries = {}
        self.active_topic = ""
        self.active_summary = ""
        self.total_messages = 1

        for topic in topics:
            self.topics[topic] = {'answered': False, 'summary': ""}

        for summary in summaries:
            self.summaries[summary] = {'summary': "", 'options': ""}

        self.change_to_active_topic()

    def change_to_active_topic(self):
        for topic, topic_data in self.topics.items():
            if not topic_data['answered']:
                self.active_topic = topic
                break

    def all_topics_answered(self):
        response = True
        for topic, topic_data in self.topics.items():
            if not topic_data['answered']:
                response = False
                break
        return response

    def active_topic_answered(self, answered):
        self.topics[self.active_topic]['answered'] = answered

    def active_summary_answered(self, answered):
        self.summaries[self.active_summary]['answered'] = answered


class ChatAssistant:
    def __init__(self, secret_key, system_message):
        self.messages = []
        self.model_reply = ""
        self.user_reply = ""
        self.secret_key = secret_key
        self.system_message = system_message
        self.messages.append({"role": "system", "content": self.system_message})

    def add_prompt(self, chat_prompt):
        """Updates the prompt messages"""
        self.messages.append({"role": "user", "content": chat_prompt})
        self.model_reply = ""

    def add_user_reply(self):
        """Updates the prompt messages"""
        self.messages.append({"role": "user", "content": self.user_reply})
        self.user_reply = ""
        self.model_reply = ""

    def update_response(self, response_display_object):
        """Calls the OpenAI API and updates model_response_display"""
        openai.api_key = self.secret_key
        qu_attempts = 1
        while qu_attempts <= 10:

            try:
                response = []
                for resp in openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=self.messages,
                        stream=True):
                    if 'content' in resp['choices'][0]['delta']:
                        response.append(resp['choices'][0]['delta']['content'])
                        result = "".join(response).strip()
                        response_display_object.markdown(f'{result}')

                self.model_reply = "".join(response).strip()

                qu_attempts = 11

            except:
                print(f"openai error, attempt {qu_attempts}")
                qu_attempts += 1
                time.sleep(1)

        self.messages.append({"role": "assistant", "content": self.model_reply})


def handle_intro():
    """
        Handles the 'Intro' section where welcome message is displayed.
    """
    global ss
    render_logo()
    # Load data into local session states
    load_data()
    display_headers()

    system_message = ""

    if 'chat_coach' not in ss:
        ss['chat_coach'] = ChatAssistant(secret_key=st.secrets['SECRET_KEY'], system_message=system_message)
        ss['user_session'] = UserSession(ss.topics.index.tolist(), ss.summaries.index.tolist())


    # Create expanders topics
    for topic, row in ss.topics.iterrows():
        handle_topic_expander(row, ss, topic)

    summary_option_name = st.selectbox("Let's work on your:", options=ss.summaries['name'].tolist())
    summary_option = ss.summaries.loc[ss.summaries['name'] == summary_option_name].index[0]

    complete = ss.user_session.all_topics_answered()
    button_type = 'primary' if complete else 'secondary'

    if st.button('Go', type=button_type):
        if complete:
            ss.user_session.active_summary = summary_option
            ss.chat_coach.add_prompt(ss.summaries.loc[summary_option, 'prompt'])
            change_state('summary')
        else:
            st.error('Please answer all sections first')


def handle_topic_expander(row, ss, topic):
    expander = st.expander(f"**{row['title']}**", expanded=(ss.user_session.active_topic == topic))
    with expander:
        st.markdown(row['intro'])

        if ss.user_session.topics[topic]['answered']:
            if ss.user_session.topics[topic]['summary'] == "":
                local_model_response_display = st.empty()
                ss.chat_coach.update_response(local_model_response_display)
                ss.user_session.topics[topic]['summary'] = ss.chat_coach.model_reply
            else:
                st.markdown(ss.user_session.topics[topic]['summary'])

            if st.button("Start again", key=f"Refresh {topic}"):
                topic_prompt = ss.prompts.at['interview_prompt', 'prompt'] \
                    .format(topic=topic, guidance_questions=row['guidance_questions'],
                            max_questions=row['max_questions'])
                ss.user_session.active_topic = topic
                ss.chat_coach.add_prompt(topic_prompt)
                change_state('questions')

            if st.button("Next", key=f"Next {topic}", type='primary'):
                ss.user_session.change_to_active_topic()
                st.experimental_rerun()

        else:
            if st.button("Start", key=f"Start {topic}", type='primary'):
                topic_prompt = ss.prompts.at['interview_prompt', 'prompt'] \
                    .format(topic=topic, guidance_questions=row['guidance_questions'],
                            max_questions=row['max_questions'])
                ss.chat_coach.add_prompt(topic_prompt)
                change_state('questions')


def handle_topic_questions():
    """
        Handles the 'Chat-like' section where user is asked a series of questions generated via prompt.
    """
    global model_response_display, ss
    display_headers()
    if ss.chat_coach.model_reply == "":
        model_response_display = st.empty()
        ss.chat_coach.update_response(model_response_display)
    else:
        model_response_display = st.markdown(ss.chat_coach.model_reply)

    if ss.counts <= ss.topics.loc[ss.user_session.active_topic, 'max_questions']:
        ss.chat_coach.user_reply = st.text_area("Response:", label_visibility='collapsed',
                                     placeholder="Take your time to think about your reply.",
                                     key='reply')

        st.button("Next", on_click=next_coaching_question, type='primary')
    else:
        st.button("Back to summary", on_click=back_to_summary, type='primary')


def get_text_area_height(text, min_height=25, max_height=1000, padding=20, chars_per_line=75):
    """Estimate the height of the textarea based on the number of characters in the text."""
    lines = len(text) // chars_per_line + 1
    height = min(max(lines * padding, min_height), max_height)
    return height


def handle_summary():
    """
        Handles the 'Summary' section where user is shown a structured summary of the conversation.
    """
    global model_response_display, ss
    render_logo()
    st.header(ss.summaries.loc[ss.user_session.active_summary, 'name'])

    if ss.user_session.summaries[ss.user_session.active_summary]['summary'] == "":
        local_model_response_display = st.empty()
        ss.chat_coach.update_response(local_model_response_display)
        ss.user_session.summaries[ss.user_session.active_summary]['summary'] = ss.chat_coach.model_reply
        st.experimental_rerun()
    else:
        default_text = ss.user_session.summaries[ss.user_session.active_summary]['summary']

        ss.user_session.summaries[ss.user_session.active_summary]['summary'] \
            = st.text_area('Edit:', value=default_text,
                           height=get_text_area_height(default_text))

    if st.button("Back to Summary"):
        change_state('intro')


LOGO_PATH = ''
st.set_page_config(page_title=f"IMAGINE", page_icon=":star2:", layout="centered",
                   initial_sidebar_state="collapsed", menu_items=None)

# Initiate streamlit states
ss = st.session_state
initiate_states()

state_functions = {
    "intro": handle_intro,
    "questions": handle_topic_questions,
    "summary": handle_summary,
}

state_functions[ss.state]()
