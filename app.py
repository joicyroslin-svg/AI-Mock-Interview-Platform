from pathlib import Path

import streamlit as st

from utils.ai_interviewer import (
    generate_interview_question,
    generate_multiple_questions,
    evaluate_answer,
)
from utils.pdf_reader import extract_text_from_pdf


RESUME_DIR = Path("resumes")


def save_uploaded_resume(uploaded_file):
    RESUME_DIR.mkdir(exist_ok=True)
    resume_path = RESUME_DIR / uploaded_file.name

    with resume_path.open("wb") as file:
        file.write(uploaded_file.getbuffer())

    return resume_path


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
            answer evaluation, and personalized feedback.
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

        user_answer = st.text_area(
            "Type your answer here",
            height=220,
            placeholder="Write your interview answer here...",
        )

        if st.button("Evaluate My Answer"):
            if not user_answer.strip():
                st.warning("Please write your answer before evaluation.")
            else:
                with st.spinner("AI is evaluating your answer..."):
                    feedback = evaluate_answer(
                        st.session_state.question,
                        user_answer,
                        role,
                        st.session_state.resume_text,
                    )

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