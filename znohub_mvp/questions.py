import pandas as pd
import streamlit as st


@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv", sep=';', encoding='utf-8')
    for col in ["option1", "option2", "option3", "option4", "answer"]:
        df[col] = df[col].astype(str).str.replace(" ⭐️", "", regex=False).str.strip()
    return df

def get_topic_questions(questions):
    return questions[questions['topic'] == st.session_state['topic']].reset_index(drop=True)
