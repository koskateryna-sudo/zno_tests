import streamlit as st
from questions import load_questions, get_topic_questions
from pages import render_home, render_timeout, render_quiz, render_results

st.title("НМТ тести з історії України — зароби свій бейдж! 🎓")

questions = load_questions()

defaults = {
    'page': 'home',
    'topic': None,
    'current_question': 0,
    'answers': {},
    'confirmed': set(),
    'quiz_start_time': None,
    'timed_out': False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state['page'] == 'home':
    render_home(questions)

elif st.session_state['page'] == 'timeout':
    topic_questions = get_topic_questions(questions)
    render_timeout(topic_questions)

elif st.session_state['page'] == 'quiz':
    topic_questions = get_topic_questions(questions)
    render_quiz(topic_questions)

elif st.session_state['page'] == 'results':
    topic_questions = get_topic_questions(questions)
    render_results(topic_questions)