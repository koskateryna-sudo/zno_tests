import pandas as pd
import streamlit as st


@st.cache_data
def load_questions():
    return pd.read_csv("questions.csv", sep=';')


def get_topic_questions(questions):
    return questions[questions['topic'] == st.session_state['topic']].reset_index(drop=True)