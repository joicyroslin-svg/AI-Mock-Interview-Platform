import streamlit as st

from utils.ai_interviewer import generate_interview_question, evaluate_answer


st.set_page_config(
    page_title="AI Mock Interview Platform",
    page_icon="🎤",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #ecfeff 100%);
    }

    .main-title {
        font-size: 44px;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 8px;
    }

    .subtitle {
        font-size: 18px;
        color: #475569;
        margin-bottom: 25px;
    }

    .hero-card {
        background: linear-gradient(135deg, #ffffff 0%, #eef2ff 100%);
        padding: 30px;
        border-radius: 28px;
        border: 1px solid #dbeafe;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.10);
        margin-bottom: 25px;
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
            Practice interview questions, answer them, and get AI-powered feedback.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Interview Setup")

role = st.sidebar.selectbox(
    "Choose Role",
    [
        "AI/ML Intern",
        "Data Analyst",
        "Python Developer",
        "Generative AI Engineer",
        "Computer Vision Intern",
        "NLP Intern",
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
    ],
)

if "question" not in st.session_state:
    st.session_state.question = ""

st.subheader("Interview Question Generator")

if st.button("Generate Interview Question"):
    with st.spinner("Generating interview question..."):
        st.session_state.question = generate_interview_question(
            role,
            level,
            question_type,
        )

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
                )

            st.subheader("AI Feedback")
            st.markdown(feedback)