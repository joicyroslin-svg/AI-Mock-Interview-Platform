from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ai_interviewer import (
    generate_interview_question,
    generate_multiple_questions,
    evaluate_answer,
    transcribe_audio_answer,
    generate_final_interview_summary,

)
from utils.pdf_reader import extract_text_from_pdf


RESUME_DIR = Path("resumes")


def save_uploaded_resume(uploaded_file):
    RESUME_DIR.mkdir(exist_ok=True)
    resume_path = RESUME_DIR / uploaded_file.name

    with resume_path.open("wb") as file:
        file.write(uploaded_file.getbuffer())

    return resume_path


def extract_score(feedback):
    match = re.search(r"Score:\s*(\d+)", feedback)

    if match:
        score = int(match.group(1))

        if score > 10:
            return 10

        return score

    return 0


def build_interview_report(role, level, question_type, feedback_history):
    report = f"""
AI Mock Interview Report

Role: {role}
Level: {level}
Question Type: {question_type}

Total Attempts: {len(feedback_history)}

----------------------------------------
"""

    for index, item in enumerate(feedback_history, start=1):
        report += f"""
Attempt {index}

Question:
{item["question"]}

Candidate Answer:
{item["answer"]}

Score:
{item["score"]}/10

AI Feedback:
{item["feedback"]}

----------------------------------------
"""

    return report

def get_readiness_level(average_score):
    if average_score >= 8:
        return "Interview Ready"

    if average_score >= 6:
        return "Almost Ready"

    if average_score >= 4:
        return "Needs Practice"

    return "Beginner Level"


def create_score_trend_chart(scores):
    df = pd.DataFrame(
        {
            "Attempt": list(range(1, len(scores) + 1)),
            "Score": scores,
        }
    )

    fig = px.line(
        df,
        x="Attempt",
        y="Score",
        markers=True,
        title="Interview Score Trend",
    )

    fig.update_layout(
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


def create_score_bar_chart(feedback_history):
    df = pd.DataFrame(
        {
            "Attempt": [
                f"Attempt {index}"
                for index in range(1, len(feedback_history) + 1)
            ],
            "Score": [
                item["score"]
                for item in feedback_history
            ],
        }
    )

    fig = px.bar(
        df,
        x="Attempt",
        y="Score",
        text="Score",
        title="Attempt-wise Score Analysis",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig

st.set_page_config(
    page_title="AI Mock Interview Platform",
    page_icon="🎤",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(124, 58, 237, 0.14), transparent 28%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 55%, #ecfeff 100%);
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #2563eb 100%);
        padding: 34px;
        border-radius: 30px;
        box-shadow: 0 20px 50px rgba(15, 23, 42, 0.22);
        margin-bottom: 25px;
    }

    .main-title {
        font-size: 46px;
        font-weight: 900;
        color: white;
        margin-bottom: 10px;
    }

    .subtitle {
        font-size: 18px;
        color: #cbd5e1;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        height: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        border: none;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%);
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="main-title">AI Mock Interview Platform</div>
        <div class="subtitle">
            Practice interviews with AI-generated questions, resume-based questioning,
            answer evaluation, performance tracking, and downloadable interview reports.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "question" not in st.session_state:
    st.session_state.question = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "transcribed_answer" not in st.session_state:
    st.session_state.transcribed_answer = ""    


st.sidebar.title("Interview Setup")

uploaded_resume = st.sidebar.file_uploader(
    "Upload Resume PDF",
    type=["pdf"],
)

if uploaded_resume:
    resume_path = save_uploaded_resume(uploaded_resume)
    st.session_state.resume_text = extract_text_from_pdf(resume_path)
    st.sidebar.success("Resume uploaded successfully.")

role = st.sidebar.selectbox(
    "Choose Role",
    [
        "AI/ML Intern",
        "Data Analyst",
        "Python Developer",
        "Generative AI Engineer",
        "Computer Vision Intern",
        "NLP Intern",
        "Backend Developer",
        "Business Analyst",
    ],
)

level = st.sidebar.selectbox(
    "Choose Level",
    [
        "Beginner",
        "Intermediate",
    ],
)

question_type = st.sidebar.selectbox(
    "Question Type",
    [
        "HR",
        "Technical",
        "Project-Based",
        "Scenario-Based",
        "Resume-Based",
    ],
)

mode = st.sidebar.radio(
    "Interview Mode",
    [
        "Single Question",
        "Multiple Questions",
    ],
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Selected Role", role)

with metric2:
    st.metric("Level", level)

with metric3:
    st.metric("Mode", mode)

total_attempts = len(st.session_state.feedback_history)

if st.session_state.scores:
    average_score = sum(st.session_state.scores) / len(st.session_state.scores)
    best_score = max(st.session_state.scores)
else:
    average_score = 0
    best_score = 0

st.subheader("Interview Performance Dashboard")
if st.session_state.scores:
    readiness_level = get_readiness_level(average_score)

    st.subheader("Interview Readiness Level")

    if readiness_level == "Interview Ready":
        st.success(readiness_level)
    elif readiness_level == "Almost Ready":
        st.warning(readiness_level)
    else:
        st.error(readiness_level)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(
            create_score_trend_chart(st.session_state.scores),
            use_container_width=True,
        )

    with chart_col2:
        st.plotly_chart(
            create_score_bar_chart(st.session_state.feedback_history),
            use_container_width=True,
        )
else:
    st.info("Complete at least one interview attempt to see performance analytics.")

score_col1, score_col2, score_col3 = st.columns(3)

with score_col1:
    st.metric("Total Attempts", total_attempts)

with score_col2:
    st.metric("Average Score", f"{average_score:.1f}/10")

with score_col3:
    st.metric("Best Score", f"{best_score}/10")

if st.session_state.feedback_history:
    report_text = build_interview_report(
        role,
        level,
        question_type,
        st.session_state.feedback_history,
    )

    st.download_button(
        label="Download Interview Report",
        data=report_text,
        file_name="ai_mock_interview_report.txt",
        mime="text/plain",
    )

if st.session_state.resume_text:
    with st.expander("View Extracted Resume Text"):
        st.text_area(
            "Resume Text",
            st.session_state.resume_text,
            height=250,
        )

st.subheader("Interview Question Generator")

if mode == "Single Question":
    if st.button("Generate Interview Question"):
        with st.spinner("Generating interview question..."):
            st.session_state.question = generate_interview_question(
                role,
                level,
                question_type,
                st.session_state.resume_text,
            )

        st.session_state.history.append(st.session_state.question)

    if st.session_state.question:
        st.info(st.session_state.question)

        st.subheader("Your Answer")

        answer_mode = st.radio(
            "Choose Answer Mode",
            ["Type Answer", "Record Voice Answer"],
            horizontal=True,
        )

        user_answer = ""

        if answer_mode == "Type Answer":
            user_answer = st.text_area(
                "Type your answer here",
                height=220,
                placeholder="Write your interview answer here...",
            )

        else:
            recorded_audio = st.audio_input(
                "Record your interview answer",
                sample_rate=16000,
            )

            if recorded_audio:
                st.audio(recorded_audio)

                if st.button("Transcribe Voice Answer"):
                    with st.spinner("Transcribing your voice answer..."):
                        audio_bytes = recorded_audio.getvalue()
                        mime_type = recorded_audio.type or "audio/wav"

                        st.session_state.transcribed_answer = transcribe_audio_answer(
                            audio_bytes,
                            mime_type,
                        )

            if st.session_state.transcribed_answer:
                st.subheader("Transcribed Answer")
                st.info(st.session_state.transcribed_answer)

            user_answer = st.session_state.transcribed_answer

        if st.button("Evaluate My Answer"):
            if not user_answer.strip():
                st.warning("Please type an answer or record and transcribe your voice answer before evaluation.")
            else:
                with st.spinner("AI is evaluating your answer..."):
                    feedback = evaluate_answer(
                        st.session_state.question,
                        user_answer,
                        role,
                        st.session_state.resume_text,
                    )

                score = extract_score(feedback)

                st.session_state.feedback_history.append(
                    {
                        "question": st.session_state.question,
                        "answer": user_answer,
                        "feedback": feedback,
                        "score": score,
                    }
                )

                if score > 0:
                    st.session_state.scores.append(score)

                st.subheader("AI Feedback")
                st.markdown(feedback)

else:
    question_count = st.slider(
        "Number of Questions",
        min_value=3,
        max_value=10,
        value=5,
    )

    if st.button("Generate Question Set"):
        with st.spinner("Generating multiple interview questions..."):
            questions = generate_multiple_questions(
                role,
                level,
                question_type,
                st.session_state.resume_text,
                question_count,
            )

        st.subheader("Generated Interview Questions")
        st.markdown(questions)

        st.session_state.history.append(questions)


st.subheader("Question History")

if st.session_state.history:
    for index, item in enumerate(st.session_state.history, start=1):
        with st.expander(f"Question History {index}"):
            st.write(item)
else:
    st.info("No questions generated yet.")


st.subheader("Feedback History")

if st.session_state.feedback_history:
    for index, item in enumerate(st.session_state.feedback_history, start=1):
        with st.expander(f"Attempt {index} — Score: {item['score']}/10"):
            st.markdown("### Question")
            st.write(item["question"])

            st.markdown("### Your Answer")
            st.write(item["answer"])

            st.markdown("### AI Feedback")
            st.markdown(item["feedback"])
else:
    st.info("No feedback history yet.")

st.subheader("Final AI Interview Summary")

if st.session_state.feedback_history:
    if st.button("Generate Final Performance Summary"):
        with st.spinner("AI is analyzing your complete interview performance..."):
            final_summary = generate_final_interview_summary(
                role,
                level,
                st.session_state.feedback_history,
            )

        st.markdown(final_summary)
else:
    st.info("Complete at least one evaluated answer to generate final summary.")    
