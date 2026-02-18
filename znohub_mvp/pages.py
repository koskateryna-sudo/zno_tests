import os
import time
import pandas as pd
import streamlit as st
from badges import BADGES, load_badges, save_badge
from timer_utils import start_timer, render_timer

SECONDS_PER_QUESTION = 3


def render_home(questions):
    earned = load_badges()

    if earned:
        st.markdown("### 🏅 Твої бейджі")
        cols = st.columns(len(earned))
        for i, (topic, data) in enumerate(earned.items()):
            b = BADGES.get(topic, {})
            with cols[i]:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                badge_path = os.path.join(current_dir, b.get("image", ""))
                if os.path.exists(badge_path):
                    st.image(badge_path, width=120)
                else:
                    st.markdown(f"<div style='font-size:64px;text-align:center'>{b.get('emoji','🏅')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center'><b>{b.get('title','')}</b><br><small>{data['earned_at']}</small></div>", unsafe_allow_html=True)
        st.divider()

    st.write("Обери тему:")
    topics = questions['topic'].dropna().unique()
    for t in topics:
        b = BADGES.get(t, {})
        is_earned = t in earned
        label = f"{b.get('emoji','')} {t}  {'✅' if is_earned else ''}"
        if st.button(label, use_container_width=True):
            st.session_state['topic'] = t
            st.session_state['current_question'] = 0
            st.session_state['answers'] = {}
            st.session_state['confirmed'] = set()
            st.session_state['timed_out'] = False
            st.session_state['page'] = 'quiz'

            topic_qs = questions[questions['topic'] == t]
            time_limit = len(topic_qs) * SECONDS_PER_QUESTION

            st.session_state['quiz_start_time'] = time.time()
            st.session_state['quiz_deadline'] = time.time() + time_limit

            st.rerun()


def render_timeout(topic_questions):
    total = len(topic_questions)
    answers = st.session_state['answers']
    confirmed = st.session_state['confirmed']

    score = sum(
        1 for i in confirmed
        if answers.get(i, "").strip() == topic_questions.iloc[i]['answer'].strip()
    )
    answered = len(confirmed)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff4444, #cc0000);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(255,68,68,0.3);
    ">
        <div style="font-size: 72px; margin-bottom: 16px">⏰</div>
        <div style="font-size: 36px; font-weight: bold; margin-bottom: 8px">Час вийшов!</div>
        <div style="font-size: 18px; opacity: 0.9">На жаль, тобі не вдалося завершити тест вчасно</div>
    </div>
    """, unsafe_allow_html=True)

    if answered > 0:
        pct = round(score / answered * 100)
        st.markdown(f"""
        <div style="
            background: #1e1e2e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: white;
            margin: 16px 0;
        ">
            <div style="font-size: 16px; opacity: 0.7; margin-bottom: 8px">Була надана відповідь на</div>
            <div style="font-size: 28px; font-weight: bold">{score} / {answered} правильних</div>
            <div style="font-size: 16px; opacity: 0.7; margin-top: 4px">з {total} питань загалом</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: #1e1e2e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: white;
            margin: 16px 0;
        ">
            <div style="font-size: 22px">Жодної відповіді не отримано:(</div>
        </div>
        """, unsafe_allow_html=True)

    topic = st.session_state['topic']
    badge = BADGES.get(topic)
    if badge:
        time_limit = total * SECONDS_PER_QUESTION
        st.info(f"💡 Для бейджу {badge['emoji']} **«{badge['title']}»** потрібно 100% правильних та вкластися в {time_limit} сек.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Спробувати ще раз", use_container_width=True, type="primary"):
            st.session_state['current_question'] = 0
            st.session_state['answers'] = {}
            st.session_state['confirmed'] = set()
            st.session_state['quiz_start_time'] = time.time()
            st.session_state['timed_out'] = False
            st.session_state['page'] = 'quiz'
            st.rerun()
    with col2:
        if st.button("🏠 На головну", use_container_width=True):
            st.session_state['page'] = 'home'
            st.session_state['topic'] = None
            st.session_state['current_question'] = 0
            st.session_state['answers'] = {}
            st.session_state['confirmed'] = set()
            st.session_state['quiz_start_time'] = None
            st.session_state['timed_out'] = False
            st.rerun()


def render_quiz(topic_questions):
    idx = st.session_state['current_question']
    q = topic_questions.iloc[idx]
    total = len(topic_questions)
    time_limit = total * SECONDS_PER_QUESTION

    start_timer()

    col_title, col_timer = st.columns([3, 1])
    with col_title:
        st.subheader(f"Тема: {st.session_state['topic']}")
        st.caption(f"Питання {idx + 1} з {total}")
    with col_timer:
        render_timer(time_limit)

    st.write(q['question'])

    if pd.notna(q.get('image')) and str(q.get('image', '')).strip() not in ('', 'nan'):
        if q['type'] != 'image_choice':
            current_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(current_dir, str(q['image']).strip())
            if os.path.exists(img_path):
                st.image(img_path, width=600)

    options = [q['option1'], q['option2'], q['option3'], q['option4']]
    correct = q['answer']
    already_confirmed = idx in st.session_state['confirmed']

    saved_answer = st.session_state['answers'].get(idx)

    if q['type'] == 'image_choice':
        labels = ['А', 'Б', 'В', 'Г']

        if not already_confirmed:
            radio_idx = options.index(saved_answer) if saved_answer in options else None

            chosen_label = st.radio(
                "Обери відповідь:",
                labels,
                index=radio_idx,
                horizontal=True,
                key=f"radio_{idx}"
            )

            cols = st.columns(4)
            for i, img_path in enumerate(options):
                with cols[i]:
                    st.markdown(f"**{labels[i]}**")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    full_path = os.path.join(current_dir, img_path)
                    if os.path.exists(full_path):
                        st.image(full_path, width="stretch")

            if chosen_label:
                st.session_state['answers'][idx] = options[labels.index(chosen_label)]

            if st.button(
                "✅ Відповісти",
                type="primary",
                use_container_width=True,
                disabled=(chosen_label is None)
            ):
                st.session_state['confirmed'].add(idx)
                st.rerun()

        else:
            cols = st.columns(4)
            for i, img_path in enumerate(options):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(current_dir, img_path)
                with cols[i]:
                    st.markdown(f"**{labels[i]}**")
                    if img_path == saved_answer and img_path == correct:
                        if os.path.exists(full_path):
                            st.image(full_path, width="stretch")
                            st.success("✅ Твій вибір")
                    elif img_path == saved_answer:
                        if os.path.exists(full_path):
                            st.image(full_path, width="stretch")
                            st.error("❌ Твій вибір")
                    elif img_path == correct:
                        if os.path.exists(full_path):
                            st.image(full_path, width="stretch")
                            st.success("✅ Правильно")
                    else:
                        if os.path.exists(full_path):
                            st.image(full_path, width="stretch")

            if idx < total - 1:
                if st.button("Далі ➡️", type="primary", use_container_width=True):
                    st.session_state['current_question'] += 1
                    st.rerun()
            else:
                if st.button("🏁 Завершити тест", type="primary", use_container_width=True):
                    st.session_state['page'] = 'results'
                    st.rerun()

    else:
        if not already_confirmed:
            radio_idx = options.index(saved_answer) if saved_answer in options else None

            chosen = st.radio(
                "Обери відповідь:",
                options,
                index=radio_idx,
                key=f"radio_{idx}"
            )

            if chosen:
                st.session_state['answers'][idx] = chosen

            if st.button(
                "✅ Відповісти",
                type="primary",
                use_container_width=True,
                disabled=(chosen is None)
            ):
                st.session_state['confirmed'].add(idx)
                st.rerun()

        else:
            for opt in options:
                if opt == saved_answer and opt == correct:
                    st.success(f"✅ {opt}")
                elif opt == saved_answer:
                    st.error(f"❌ {opt}")
                elif opt == correct:
                    st.success(f"✅ {opt}  ← правильна відповідь")
                else:
                    st.markdown(f"○ {opt}")

            if idx < total - 1:
                if st.button("Далі ➡️", type="primary", use_container_width=True):
                    st.session_state['current_question'] += 1
                    st.rerun()
            else:
                if st.button("🏁 Завершити тест", type="primary", use_container_width=True):
                    st.session_state['page'] = 'results'
                    st.rerun()

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Назад", use_container_width=True, disabled=(idx == 0)):
            if idx > 0:
                st.session_state['current_question'] -= 1
                st.rerun()
    with col2:
        if st.button("Пропустити ⏭️", use_container_width=True, disabled=(idx == total - 1)):
            if idx < total - 1:
                st.session_state['current_question'] += 1
                st.rerun()
    with col3:
        if st.button("Завершити 🛑", use_container_width=True):
            st.session_state['page'] = 'results'
            st.rerun()


def render_results(topic_questions):
    total = len(topic_questions)
    answers = st.session_state['answers']
    confirmed = st.session_state['confirmed']

    score = sum(
        1 for i in confirmed
        if answers.get(i, "").strip() == topic_questions.iloc[i]['answer'].strip()
    )
    answered = len(confirmed)
    pct = round(score / answered * 100) if answered > 0 else 0

    elapsed = time.time() - st.session_state['quiz_start_time'] if st.session_state['quiz_start_time'] else 0
    time_limit = total * SECONDS_PER_QUESTION
    finished_in_time = elapsed <= time_limit

    st.subheader("📊 Результат")
    st.metric("Правильних відповідей", f"{score} / {answered}")
    if answered < total:
        st.warning(f"Надана відповідь на {answered} з {total} питань (пропущено: {total - answered})")

    if pct >= 80:   st.success(f"🏆 {pct}% — Відмінно!")
    elif pct >= 60: st.info(f"👍 {pct}% — Непогано!")
    else:           st.warning(f"📚 {pct}% — Варто повторити матеріал")

    topic = st.session_state['topic']
    badge = BADGES.get(topic)
    earned_badges = load_badges()

    if badge:
        st.divider()
        mins_u, secs_u = int(elapsed // 60), int(elapsed % 60)
        st.caption(f"⏱ Час: {mins_u}:{secs_u:02d} / ліміт {time_limit} сек")

        if pct == 100 and finished_in_time:
            already_had = topic in earned_badges
            if not already_had:
                save_badge(topic)
                earned_badges = load_badges()

            st.balloons()
            col_l, col_c, col_r = st.columns([1, 2, 1])
            with col_c:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea, #764ba2);
                            border-radius: 20px; padding: 24px; text-align: center; color: white;'>
                    <div style='font-size: 20px; font-weight: bold; margin-bottom: 12px'>
                        {'🏅 Бейдж вже твій!' if already_had else '🏅 Бейдж отримано!'}
                    </div>
                """, unsafe_allow_html=True)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                badge_path = os.path.join(current_dir, badge["image"])
                if os.path.exists(badge_path):
                    st.image(badge_path, width=160)
                else:
                    st.markdown(f"<div style='font-size:80px;text-align:center'>{badge['emoji']}</div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='color:black; font-size: 24px; font-weight: bold; margin-top: 8px'>«{badge['title']}»</div>
                    <div style='color:black; font-size: 20px; opacity: 0.85; margin-top: 6px'>
                        {'Ти вже заробила цей бейдж раніше 🔥' if already_had else badge['desc']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info(f"💡 Для бейджу {badge['emoji']} **«{badge['title']}»** потрібно 100% правильних + вкластися в {time_limit} сек.")

    st.divider()
    if st.button("🔄 Спробувати ще раз", use_container_width=True):
        st.session_state['current_question'] = 0
        st.session_state['answers'] = {}
        st.session_state['confirmed'] = set()
        st.session_state['quiz_start_time'] = time.time()
        st.session_state['timed_out'] = False
        st.session_state['page'] = 'quiz'
        st.rerun()

    if st.button("🏠 На головну", use_container_width=True):
        st.session_state['page'] = 'home'
        st.session_state['topic'] = None
        st.session_state['current_question'] = 0
        st.session_state['answers'] = {}
        st.session_state['confirmed'] = set()
        st.session_state['quiz_start_time'] = None
        st.session_state['timed_out'] = False
        st.rerun()
