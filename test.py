import streamlit as st

input = st.text_area("text", key="text")

def clear_text():
    st.session_state["text"] = ""


st.button("clear text input", on_click=clear_text)
st.write(input)