import streamlit as st
import openai
import time
import pandas as pd
from emailing import send_email, add_html_blocks, github_markup_to_html

# Import functions
from helper_functions import contains_pattern, get_company_info, get_action_bullets
from state_handling import initiate_states, load_data, load_questions


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
    st.image(LOGO_PATH, width=100)


def next_coaching_question():
    """Updates the prompt messages and moves to next page"""
    if ss.counts <= ss.topic_prompts.loc[ss.current_topic['name'], 'max_questions']:
        if len(ss.user_reply) > 3:
            local_prompt = ss.user_reply
            update_messages(local_prompt)
            ss.counts = ss.counts + 1
            ss.user_reply = ""
            st.session_state["reply"] = ""
        else:
            st.error('To facilitate a more meaningful discussion, '
                     'please include more information in your response.')

    else:
        ss.state = 'Summary'
        local_prompt = ss.prompts.loc['summary_prompt', 'prompt']
        update_messages(local_prompt)


def update_messages(local_prompt):
    """Updates the prompt messages"""
    ss.messages.append({"role": "assistant", "content": ss.model_reply})
    ss.messages.append({"role": "user", "content": local_prompt})
    ss.model_reply = ""
    ss.user_reply = ""


def update_model_response():
    """Calls the OpenAI API and updates model_response_display"""
    openai.api_key = st.secrets['SECRET_KEY']

    qu_attempts = 1
    while qu_attempts <= 10:

        try:
            response = []
            for resp in openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=ss.messages,
                    stream=True):
                if 'content' in resp['choices'][0]['delta']:
                    response.append(resp['choices'][0]['delta']['content'])
                    result = "".join(response).strip()
                    model_response_display.markdown(f'{result}')

            ss.model_reply = "".join(response).strip()
            qu_attempts = 11

        except:
            print(f"openai error, attempt {qu_attempts}")
            qu_attempts += 1
            time.sleep(1)

    st.experimental_rerun()


def collect_user_info(label: str, input_type: str, placeholder: str = '', options: list = None, index: int = None):
    if input_type == "text":
        return st.text_input(label=label, placeholder=placeholder)
    elif input_type == "selectbox":
        return st.selectbox(label=label, options=options, index=index)
    elif input_type == "text_area":
        return st.text_area(label=label, placeholder=placeholder)
    else:
        raise ValueError("Invalid input_type")


def get_topic_info():
    if ss.current_topic.get('Name') is None:
        topic_index = 0
    else:
        topic_index = ss.topic_prompts.index.get_loc(ss.current_topic['name'])
    ss.current_topic['name'] = \
        st.selectbox(label="What topic would you like to discuss?",
                     options=ss.topic_prompts.index.tolist(), on_change=load_questions, index=topic_index)
    ss.current_topic['max_questions'] = ss.topic_prompts.loc[ss.current_topic['name'], 'max_questions']
    if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'company_info']):
        ss.current_topic['company_info'] = get_company_info(ss.topic_prompts.loc[ss.current_topic['name'], 'company_info'])
    else:
        ss.current_topic['company_info'] = ""
    ss.current_topic['question_format'] = ss.prompts.loc['question_format', 'prompt']
    ss.current_topic['question_1'] = ss.topic_prompts.loc[ss.current_topic['name'], 'question1']
    ss.current_topic['question_2'] = ss.topic_prompts.loc[ss.current_topic['name'], 'question2']
    ss.current_topic['reply_1'] = ""
    ss.current_topic['reply_2'] = ""

    if ss.load_questions:
        if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'description']):
            st.markdown('**' + ss.topic_prompts.loc[ss.current_topic['name'], 'description'] + '**')

        if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'question1']):
            st.markdown(ss.current_topic['question_1'])
            ss.current_topic['reply_1'] = st.text_area("Reply 1", label_visibility='collapsed')

        if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'question2']):
            st.markdown(ss.current_topic['question_2'])
            ss.current_topic['reply_1=2'] = st.text_area("Reply 2", label_visibility='collapsed')


def create_coaching_prompt():
    local_prompt = ss.prompts.loc['coaching_prompt', 'prompt'] \
        .format(user_name=ss.user_info["name"], band=ss.user_info["band"], function=ss.user_info["function"],
                position=ss.user_info["position"], experience=ss.user_info["experience"],
                function_detail=ss.user_info["function_detail"],
                topic_name=ss.current_topic['name'], company_info=ss.current_topic['company_info'],
                question_1=ss.current_topic['question_1'], question_2=ss.current_topic['question_2'],
                reply_1=ss.current_topic['reply_1'], reply_2=ss.current_topic['reply_2'],
                question_guidance=ss.topic_prompts.loc[ss.current_topic['name'], 'question_guidance'],
                max_questions=ss.current_topic['max_questions'], question_format=ss.current_topic['question_format'])
    return local_prompt


def handle_intro():
    """
        Handles the 'Intro' section where welcome message is displayed.
    """
    global ss
    render_logo()
    # Load data into local session states
    load_data()
    display_headers()
    if st.button("Let's Start!", type='primary'):
        ss.state = 'About You'
        st.experimental_rerun()


def handle_about_you():
    """
    Handles the 'About You' section where user inputs their personal information.
    """

    global index, ss
    display_headers()
    # Collect user info
    user_inputs = [
        ("How should we address you?", "text", "e.g. John", None, None, "name"),
        ("Function", "selectbox", "", ss.functions.index.tolist(), 4, "function"),
        ("Level", "selectbox", "", ss.bands.index.tolist(), 4, "band"),
        ("Title", "text", "e.g. Finance, Procurement", None, None, "position"),
        ("Can you describe your role in more detail?", "text_area", "", None, None, "function_detail"),
        (f"Please share your work experience at {COMPANY} and elsewhere in a few lines:", "text_area",
         f"e.g. I've been working at {COMPANY} in this team for 10 years, previously I worked at...", None, None,
         "experience"),
    ]
    for label, input_type, placeholder, options, index, key in user_inputs:
        if key == "function_detail":
            function_detail = ss.functions.loc[ss.user_info["function"], 'function_detail']
            value = function_detail if function_detail else ''
            ss.user_info[key] = collect_user_info(label, input_type, placeholder, options, index)
        else:
            ss.user_info[key] = collect_user_info(label, input_type, placeholder, options, index)
    if st.button("Next", type='primary'):
        # Build prompt and change state to next page
        ss.state = 'Topic Selection'
        prompt = ss.prompts.loc['intro_prompt', 'prompt'] \
            .format(name=ss.user_info["name"], function=ss.user_info["function"],
                    position=ss.user_info["position"], experience=ss.user_info["experience"],
                    function_detail=ss.user_info["function_detail"])

        ss.messages.append({"role": "user", "content": prompt})
        ss.model_reply = ""
        st.experimental_rerun()
    if st.button("Back"):
        change_state('Intro')


def handle_topic_selection():
    """
        Handles the 'Topic Selection' section where user selects a topic for discussion.
    """
    global ss
    render_logo()
    display_headers()
    get_topic_info()
    if st.button("Next", type='primary'):
        if contains_pattern(ss.current_topic['name'], ['...', '---']):
            st.error('Please select a topic to discuss')

        elif len(ss.current_topic['reply_1']) > 3:
            ss.state = 'Topic Questions'
            prompt = create_coaching_prompt()
            update_messages(prompt)
            ss.user_reply = ""
            st.experimental_rerun()
        else:
            st.error('To facilitate a more meaningful discussion, '
                     'please include more information in your response.')
    if st.button("Back"):
        change_state('About You')


def handle_topic_questions():
    """
        Handles the 'Chat-like' section where user is asked a series of questions generated via prompt.
    """
    global model_response_display, ss
    display_headers()
    if ss.model_reply == "":
        model_response_display = st.empty()
        update_model_response()
    else:
        model_response_display = st.markdown(ss.model_reply)
    if ss.counts <= ss.topic_prompts.loc[ss.current_topic['name'], 'max_questions']:
        ss.user_reply = st.text_area("Response:", label_visibility='collapsed',
                                     placeholder="Take your time to think about your reply.",
                                     key='reply')
    st.button("Next", on_click=next_coaching_question, type='primary')


def handle_summary():
    """
        Handles the 'Summary' section where user is shown a structured summary of the conversation.
    """
    global model_response_display, ss
    render_logo()
    display_headers()
    actions = []
    response = ['Error: No actions loaded...']
    if ss.model_reply == "":
        model_response_display = st.empty()
        update_model_response()
        st.experimental_rerun()
    else:
        response = ss.model_reply.split('::Action::')
        model_response_display = st.markdown(response[0])

        for i, action in enumerate(response[1:]):
            action_text = action.strip()
            actions.append("")
            actions[i] = st.text_area(label=str(i), label_visibility='collapsed', value=action_text)
    col1, col2 = st.columns(2)
    with col1:
        email_address = st.text_input("Email address", label_visibility='collapsed', placeholder="Enter your email")
        if st.button("Send me a copy", type='primary'):

            action_bullets = get_action_bullets(actions)

            html_blocks = {
                '{summary}': github_markup_to_html(response[0]),
                '{actions}': github_markup_to_html(action_bullets)
            }

            html_file_path = 'email_template.html'

            updated_html = add_html_blocks(html_file_path, html_blocks)

            if send_email("Career Coach - Discussion Summary and Actions", updated_html, email_address):
                st.text("Email sent!")
            else:
                st.text("Problem with email address provided. Email not sent.")
    with col2:
        ss.current_topic['name'] = \
            st.selectbox(label="What topic would you like to discuss?",
                         options=ss.topic_prompts.index.tolist(), label_visibility='collapsed')

        if st.button("Discuss another topic"):
            ss.counts = 1
            change_state('Topic Selection')


LOGO_PATH = 'placeholder.png'
COMPANY = 'Company'

# Initiate states and variables
st.set_page_config(page_title=f"{COMPANY} Career Coach", page_icon=":star2:", layout="centered",
                   initial_sidebar_state="collapsed", menu_items=None)

ss = st.session_state

# Initiate streamlit states
initiate_states()

state_functions = {
    "Intro": handle_intro,
    "About You": handle_about_you,
    "Topic Selection": handle_topic_selection,
    "Topic Questions": handle_topic_questions,
    "Summary": handle_summary,
}

state_functions[ss.state]()






