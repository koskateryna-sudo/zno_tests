import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_questions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "questions.csv")
    
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    return df
    
def get_topic_questions(questions):
    return questions[questions['topic'] == st.session_state['topic']].reset_index(drop=True)
