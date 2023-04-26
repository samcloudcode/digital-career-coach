import streamlit as st
import openai
import time
import toml
import pandas as pd
from emailing import send_email, add_html_blocks, github_markup_to_html

# Import the functions from the newly created files
from helper_functions import contains_pattern, get_aia_info
from state_handling import initiate_states, load_data, load_questions


def display_headers():

    if not pd.isna(ss.pages.loc[ss.state, 'title']):
        st.title(ss.pages.loc[ss.state, 'title'])

    if not pd.isna(ss.pages.loc[ss.state, 'subheader']):
        st.subheader(ss.pages.loc[ss.state, 'subheader'])

    if not pd.isna(ss.pages.loc[ss.state, 'markdown']):
        st.markdown(ss.pages.loc[ss.state, 'markdown'])


def next_question():
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


# Initiate states and variables
st.set_page_config(page_title="AIA Career Coach", page_icon=":star2:", layout="centered",
                   initial_sidebar_state="collapsed", menu_items=None)

ss = st.session_state
load_data()
initiate_states()


# Update display, dependent on state
match ss.state:

    case "Intro":
        st.image('AIA_Group_logo.png', width=100)

        display_headers()

        if st.button("Let's Start!", type='primary'):
            ss.state = 'About You'
            st.experimental_rerun()

    case "About You":
        display_headers()

        # Collect user info
        ss.user_info["name"] = st.text_input(label="How should we address you?",
                                             placeholder="e.g. John")

        ss.user_info["function"] = st.selectbox(label="Function", options=ss.functions.index.tolist(), index=4)

        ss.user_info["band"] = st.selectbox(label='Level', options=ss.bands.index.tolist(), index=4)

        ss.user_info["position"] = st.text_input(label="Title",
                                                 placeholder="e.g. Finance, Procurement")

        function_detail = ss.functions.loc[ss.user_info["function"], 'function_detail']

        ss.user_info["function_detail"] = st.text_area(label="Can you describe your role in more detail?",
                                                       value=function_detail)

        ss.user_info["experience"] = st.text_area(label="Please share your work experience at AIA "
                                                         "and elsewhere in a few lines:",
                                                  placeholder="e.g. I've been working at AIA in this team for"
                                                              " 10 years, previously I worked at...")

        if st.button("Next", type='primary'):
            # Build prompt and change state to next page
            ss.state = 'Topic Selection'
            prompt = ss.prompts.loc['intro_prompt', 'prompt']\
                .format(name=ss.user_info["name"], function=ss.user_info["function"],
                        position=ss.user_info["position"], experience=ss.user_info["experience"],
                        function_detail=ss.user_info["function_detail"])

            ss.messages.append({"role": "user", "content": prompt}),
            ss.model_reply = ""
            st.experimental_rerun()

        if st.button("Back"):
            ss.state = 'Intro'
            st.experimental_rerun()

    case "Topic Selection":
        st.image('AIA_Group_logo.png', width=100)
        display_headers()

        if ss.current_topic.get('Name') is None:
            topic_index = 0
        else:
            topic_index = ss.topic_prompts.index.get_loc(ss.current_topic['name'])

        ss.current_topic['name'] = \
            st.selectbox(label="What topic would you like to discuss?",
                         options=ss.topic_prompts.index.tolist(), on_change=load_questions, index=topic_index)

        max_questions = ss.topic_prompts.loc[ss.current_topic['name'], 'max_questions']

        if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'aia_info']):
            aia_info = get_aia_info(ss.topic_prompts.loc[ss.current_topic['name'], 'aia_info'])
        else:
            aia_info = ""

        question_format = ss.prompts.loc['question_format', 'prompt']

        question_1 = ss.topic_prompts.loc[ss.current_topic['name'], 'question1']
        question_2 = ss.topic_prompts.loc[ss.current_topic['name'], 'question2']

        reply_1 = ""
        reply_2 = ""

        if ss.load_questions:
            if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'description']):
                st.markdown('**' + ss.topic_prompts.loc[ss.current_topic['name'], 'description'] + '**')

            if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'question1']):
                st.markdown(question_1)
                reply_1 = st.text_area("Reply 1", label_visibility='collapsed')

            if not pd.isna(ss.topic_prompts.loc[ss.current_topic['name'], 'question2']):
                st.markdown(question_2)
                reply_2 = st.text_area("Reply 2", label_visibility='collapsed')

        if st.button("Next", type='primary'):
            if contains_pattern(ss.current_topic['name'], ['...', '---']):
                st.error('Please select a topic to discuss')

            elif len(reply_1) > 3:
                ss.state = 'Topic Questions'
                prompt = ss.prompts.loc['coaching_prompt', 'prompt']\
                    .format(user_name=ss.user_info["name"], band=ss.user_info["band"], function=ss.user_info["function"],
                            position=ss.user_info["position"], experience=ss.user_info["experience"],
                            function_detail=ss.user_info["function_detail"],
                            topic_name=ss.current_topic['name'], aia_info=aia_info,
                            question_1=question_1, question_2=question_2, reply_1=reply_1, reply_2=reply_2,
                            question_guidance=ss.topic_prompts.loc[ss.current_topic['name'], 'question_guidance'],
                            max_questions=max_questions, question_format=question_format)
                # print(prompt)
                update_messages(prompt)
                ss.user_reply = ""
                st.experimental_rerun()
            else:
                st.error('To facilitate a more meaningful discussion, '
                         'please include more information in your response.')

        if st.button("Back"):
            ss.state = 'About You'
            st.experimental_rerun()

    case "Topic Questions":
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

        st.button("Next", on_click=next_question, type='primary')


    case "Summary":

        st.image('AIA_Group_logo.png', width=100)
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

            # print(response)

            for i, action in enumerate(response[1:]):
                action_text = action.strip()
                actions.append("")
                actions[i] = st.text_area(label=str(i), label_visibility='collapsed', value=action_text)

        col1, col2 = st.columns(2)

        with col1:
            email_address = st.text_input("Email address", label_visibility='collapsed', placeholder="Enter your email")
            if st.button("Send me a copy", type='primary'):

                action_bullets = ""
                for action in actions:
                    action_bullets = action_bullets + '* ' + action + '\n\n'

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
                ss.state = 'Topic Selection'
                ss.counts = 1
                st.experimental_rerun()

    case 'Analysis':
        st.header("Analysis")

        if ss.model_reply == "":
            model_response_display = st.empty()
            update_model_response()
        else:
            model_response_display = st.markdown(ss.model_reply)



