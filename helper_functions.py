import streamlit as st


def contains_pattern(string, patterns):
    for pattern in patterns:
        if pattern in string:
            return True
    return False


def get_company_info(info_list):
    topics = info_list.split('\n')

    results = "For reference, this is information on the topic provided by Company's internal guides: \n\n"

    for topic in topics:
        topic = topic.strip()
        if not topic:
            continue

        result = st.session_state.company_info.loc[topic, 'info']
        results = results + result + '\n\n'

    return results


def get_action_bullets(actions):
    return "\n\n".join(f"* {action}" for action in actions)

