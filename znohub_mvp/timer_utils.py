
import time
import streamlit as st
import math

def start_timer():
    """Ініціалізує час початку, якщо його немає."""
    if "quiz_start_time" not in st.session_state or st.session_state["quiz_start_time"] is None:
        st.session_state["quiz_start_time"] = time.time()

@st.fragment(run_every=1)
def render_timer(total_seconds):
    if "quiz_start_time" not in st.session_state:
        st.session_state["quiz_start_time"] = time.time()

    elapsed = time.time() - st.session_state["quiz_start_time"]
    remaining = total_seconds - elapsed

    # 1. Логіка завершення часу
    if remaining <= 0:
        st.session_state["page"] = "timeout"
        st.session_state["timed_out"] = True
        st.rerun()
        return

    # 2. Відображення таймера
    secs = math.ceil(remaining % 60)
    mins = math.ceil(remaining // 60)
    time_str = f"{mins}:{secs:02d}"

    # Кольори
    if remaining > total_seconds * 0.5:
        color = "green"
    elif remaining > total_seconds * 0.25:
        color = "orange"
    else:
        color = "red"

    st.markdown(
        f"""
        <div style="
            text-align: center; 
            font-size: 24px; 
            font-weight: bold; 
            color: {color};
            border: 2px solid {color};
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 10px;
        ">
            ⏱ {time_str}
        </div>
        """, 
        unsafe_allow_html=True
    )