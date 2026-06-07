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
        return min(score, 10)

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
        color_discrete_sequence=["#2563eb"],
    )

    fig.update_traces(line=dict(width=4), marker=dict(size=9))

    fig.update_layout(
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a"),
        title_font=dict(size=20),
    )

    return fig


def create_score_bar_chart(feedback_history):
    df = pd.DataFrame(
        {
            "Attempt": [
                f"Attempt {index}"
                for index in range(1, len(feedback_history) + 1)
            ],
            "Score": [item["score"] for item in feedback_history],
        }
    )

    fig = px.bar(
        df,
        x="Attempt",
        y="Score",
        text="Score",
        title="Attempt-wise Score Analysis",
        color="Score",
        color_continuous_scale=["#dbeafe", "#60a5fa", "#2563eb"],
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a"),
        title_font=dict(size=20),
        coloraxis_showscale=False,
    )

    return fig


def split_questions(question_text):
    lines = question_text.split("\n")
    questions = []

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue

        if re.match(r"^\d+[\).\s-]", clean_line) or clean_line.startswith("-"):
            questions.append(clean_line)

    if not questions and question_text.strip():
        questions = [question_text.strip()]

    return questions


def show_panel(label, title, description):
    st.markdown(
        f"""
        <div class="saas-panel">
            <div class="panel-label">{label}</div>
            <div class="panel-title">{title}</div>
            <div class="panel-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="AI Mock Interview Platform",
    page_icon="AI",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.16), transparent 30%),
            radial-gradient(circle at 100% 0%, rgba(124, 58, 237, 0.16), transparent 30%),
            radial-gradient(circle at 50% 100%, rgba(14, 165, 233, 0.10), transparent 28%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #f8fbff 100%);
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    .hero-card {
        background:
            radial-gradient(circle at top right, rgba(56, 189, 248, 0.23), transparent 30%),
            radial-gradient(circle at bottom left, rgba(124, 58, 237, 0.16), transparent 30%),
            linear-gradient(135deg, #020617 0%, #0f172a 36%, #1d4ed8 100%);
        padding: 44px;
        border-radius: 34px;
        box-shadow: 0 28px 70px rgba(15, 23, 42, 0.30);
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.11);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #dbeafe;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 18px;
    }

    .main-title {
        font-size: 58px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.02;
        letter-spacing: -1.8px;
        margin-bottom: 16px;
    }

    .subtitle {
        font-size: 18px;
        font-weight: 500;
        color: #cbd5e1;
        line-height: 1.8;
        max-width: 980px;
    }

    .saas-panel {
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
        padding: 26px;
        border-radius: 28px;
        margin-top: 18px;
        margin-bottom: 22px;
    }

    .panel-label {
        font-size: 12px;
        font-weight: 900;
        color: #2563eb;
        text-transform: uppercase;
        letter-spacing: 1.3px;
        margin-bottom: 8px;
    }

    .panel-title {
        font-size: 31px;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: -0.9px;
        margin-bottom: 8px;
    }

    .panel-desc {
        font-size: 15px;
        font-weight: 500;
        color: #64748b;
        line-height: 1.7;
        max-width: 950px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 24px;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 800;
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 900;
        font-size: 28px;
    }

    .stButton > button {
        width: 100%;
        min-height: 3.2rem;
        border-radius: 17px;
        border: none;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        font-size: 15px;
        font-weight: 900;
        box-shadow: 0 14px 30px rgba(37, 99, 235, 0.25);
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%);
        color: white;
        transform: translateY(-1px);
    }

    div[data-baseweb="select"] > div {
        border-radius: 16px !important;
        border: 1px solid #dbe4f0 !important;
        min-height: 52px !important;
        box-shadow: none !important;
    }

    .stRadio > div {
        background: rgba(255,255,255,0.92);
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 10px 14px;
    }

    .stTextArea textarea {
        border-radius: 18px !important;
        border: 1px solid #dbe4f0 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    .stFileUploader > div {
        border-radius: 18px !important;
    }

    .stExpander {
        border-radius: 18px !important;
        border: 1px solid #e2e8f0 !important;
        background: rgba(255,255,255,0.92) !important;
    }

    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    :root {
        --ink: #111827;
        --muted: #64748b;
        --line: #d9e2ef;
        --blue: #3157ff;
        --cyan: #05a7c4;
        --mint: #12b981;
        --coral: #ff6b4a;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            linear-gradient(rgba(17, 24, 39, 0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(17, 24, 39, 0.045) 1px, transparent 1px),
            linear-gradient(135deg, #fbfcff 0%, #f3f6fb 48%, #eef7f5 100%);
        background-size: 34px 34px, 34px 34px, auto;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .hero-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 8px;
        box-shadow: 0 28px 70px rgba(17, 24, 39, 0.24);
        margin-bottom: 28px;
        padding: 0;
        position: relative;
        overflow: hidden;
    }

    .hero-card:before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(120deg, rgba(49,87,255,0.36), transparent 38%),
            linear-gradient(280deg, rgba(5,167,196,0.28), transparent 44%),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 72px);
        pointer-events: none;
    }

    .hero-inner {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1.3fr) minmax(300px, 0.7fr);
        gap: 28px;
        align-items: stretch;
        padding: 34px;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        color: #a7f3d0;
        padding: 7px 11px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 18px;
    }

    .main-title {
        font-size: 46px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.04;
        letter-spacing: 0;
        margin-bottom: 14px;
        max-width: 820px;
    }

    .subtitle {
        font-size: 16px;
        font-weight: 500;
        color: #cbd5e1;
        line-height: 1.65;
        max-width: 850px;
    }

    .hero-visual {
        position: relative;
        min-height: 220px;
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04)),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.07) 0 1px, transparent 1px 28px),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.07) 0 1px, transparent 1px 28px);
        border: 1px solid rgba(255,255,255,0.18);
        overflow: hidden;
    }

    .hero-visual:before {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        right: -38px;
        top: -42px;
        border-radius: 50%;
        border: 34px solid rgba(18,185,129,0.28);
    }

    .hero-visual:after {
        content: "";
        position: absolute;
        left: 22px;
        right: 22px;
        bottom: 22px;
        height: 54px;
        border-radius: 8px;
        background:
            linear-gradient(90deg, #12b981 0 18%, transparent 18% 24%, #05a7c4 24% 48%, transparent 48% 55%, #3157ff 55% 82%, transparent 82% 88%, #ff6b4a 88% 100%);
        box-shadow: 0 18px 38px rgba(0,0,0,0.22);
    }

    .visual-card {
        position: absolute;
        border-radius: 8px;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(255,255,255,0.55);
        box-shadow: 0 22px 44px rgba(0,0,0,0.20);
    }

    .visual-card.one {
        width: 64%;
        height: 74px;
        left: 22px;
        top: 24px;
    }

    .visual-card.two {
        width: 44%;
        height: 88px;
        right: 24px;
        top: 78px;
        background: rgba(17,24,39,0.88);
    }

    .visual-card.three {
        width: 36%;
        height: 48px;
        left: 52px;
        top: 126px;
        background: rgba(255,255,255,0.78);
    }

    .visual-card.one:before,
    .visual-card.two:before,
    .visual-card.three:before {
        content: "";
        position: absolute;
        left: 14px;
        top: 14px;
        width: 42px;
        height: 8px;
        border-radius: 999px;
        background: #3157ff;
        box-shadow:
            58px 0 0 #d9e2ef,
            116px 0 0 #d9e2ef,
            0 24px 0 #12b981,
            72px 24px 0 #05a7c4;
    }

    .visual-card.two:before {
        background: #a7f3d0;
        box-shadow:
            58px 0 0 rgba(255,255,255,0.24),
            0 24px 0 #ff6b4a,
            72px 24px 0 #3157ff;
    }

    .visual-card.three:before {
        background: #ff6b4a;
        box-shadow:
            58px 0 0 #d9e2ef,
            116px 0 0 #d9e2ef;
    }

    .visual-node {
        position: absolute;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #a7f3d0;
        box-shadow:
            34px 22px 0 #05a7c4,
            82px -8px 0 #ff6b4a,
            132px 28px 0 #3157ff;
        right: 78px;
        bottom: 96px;
    }

    .hero-console {
        display: none;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 8px;
        padding: 18px;
        min-height: 100%;
    }

    .console-row {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.12);
        padding: 13px 0;
    }

    .console-row:first-child {
        padding-top: 0;
    }

    .console-row:last-child {
        border-bottom: 0;
        padding-bottom: 0;
    }

    .console-label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .console-value {
        color: #ffffff;
        font-size: 16px;
        font-weight: 900;
        text-align: right;
    }

    .saas-panel {
        background: transparent;
        backdrop-filter: none;
        border: 0;
        border-left: 5px solid var(--blue);
        border-radius: 0;
        box-shadow: none;
        padding: 8px 0 8px 18px;
        margin-top: 26px;
        margin-bottom: 18px;
    }

    .panel-label {
        color: var(--cyan);
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 5px;
    }

    .panel-title {
        font-size: 25px;
        color: var(--ink);
        letter-spacing: 0;
        margin-bottom: 5px;
    }

    .panel-desc {
        color: var(--muted);
        line-height: 1.55;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.94);
        border: 1px solid var(--line);
        border-top: 4px solid var(--cyan);
        padding: 18px 18px 16px;
        border-radius: 8px;
        box-shadow: 0 12px 30px rgba(17, 24, 39, 0.08);
        min-width: 0;
    }

    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        border-top-color: var(--mint);
    }

    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        border-top-color: var(--blue);
    }

    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {
        border-top-color: var(--coral);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 800;
        font-size: 13px;
    }

    div[data-testid="stMetricValue"] {
        color: var(--ink);
        font-weight: 900;
        font-size: clamp(17px, 1.35vw, 23px);
        line-height: 1.15;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .stButton > button {
        min-height: 3rem;
        border-radius: 8px;
        border: 1px solid rgba(17,24,39,0.08);
        background: linear-gradient(135deg, var(--ink) 0%, var(--blue) 100%);
        font-size: 14px;
        font-weight: 850;
        box-shadow: 0 12px 26px rgba(49, 87, 255, 0.24);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0f172a 0%, var(--cyan) 100%);
        color: white;
    }

    div[data-baseweb="select"] > div,
    .stRadio > div,
    .stTextArea textarea,
    .stExpander,
    .stFileUploader > div {
        border-radius: 8px !important;
        border-color: var(--line) !important;
    }

    div[data-baseweb="select"] > div:focus-within,
    .stTextArea textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 4px rgba(49,87,255,0.10) !important;
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,0.92);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 12px 30px rgba(17, 24, 39, 0.07);
    }

    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 8px !important;
        border-left-width: 5px !important;
    }

    .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid var(--line);
        background: #ffffff;
        color: var(--ink);
        font-weight: 800;
    }

    h2, h3 {
        letter-spacing: 0 !important;
        color: var(--ink);
    }

    @media (max-width: 900px) {
        .hero-inner {
            grid-template-columns: 1fr;
            padding: 24px;
        }

        .main-title {
            font-size: 34px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-inner">
            <div>
                <div class="hero-badge">Interview Intelligence OS</div>
                <div class="main-title">AI Mock Interview Command Desk</div>
                <div class="subtitle">
                    A focused preparation workspace for role-specific practice, resume-aware prompts,
                    voice answers, score analytics, and final coaching summaries.
                </div>
            </div>
            <div class="hero-visual" aria-hidden="true">
                <div class="visual-card one"></div>
                <div class="visual-card two"></div>
                <div class="visual-card three"></div>
                <div class="visual-node"></div>
            </div>
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

if "multiple_questions" not in st.session_state:
    st.session_state.multiple_questions = []

if "multiple_answers" not in st.session_state:
    st.session_state.multiple_answers = {}


show_panel(
    "Control Center",
    "Interview Setup Workspace",
    "Configure your target role, difficulty level, question category, interview mode, and upload your resume for personalized interview questions.",
)

setup_col1, setup_col2, setup_col3, setup_col4 = st.columns([1.15, 0.95, 1.05, 1.45])

with setup_col1:
    role = st.selectbox(
        "Target Role",
        [
            "AI/ML Intern",
            "Generative AI Engineer",
            "Data Analyst",
            "Data Scientist",
            "Python Developer",
            "Backend Developer",
            "Full Stack Developer",
            "Computer Vision Intern",
            "NLP Intern",
            "MLOps Engineer",
            "Prompt Engineer",
            "AI Product Analyst",
            "Business Analyst",
            "Product Manager",
            "Technical Writer",
            "Software Engineer Intern",
        ],
    )

with setup_col2:
    level = st.selectbox(
        "Difficulty Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
    )

with setup_col3:
    question_type = st.selectbox(
        "Question Category",
        [
            "HR",
            "Technical",
            "Project-Based",
            "Scenario-Based",
            "Resume-Based",
        ],
    )

with setup_col4:
    mode = st.selectbox(
        "Interview Mode",
        [
            "Single Question",
            "Multiple Questions",
        ],
    )

uploaded_resume = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"],
)

if uploaded_resume:
    resume_path = save_uploaded_resume(uploaded_resume)
    st.session_state.resume_text = extract_text_from_pdf(resume_path)
    st.success("Resume uploaded successfully.")

metric1, metric2, metric3, metric4 = st.columns([1.1, 0.85, 1.45, 1.1])

with metric1:
    st.metric("Target Role", role)

with metric2:
    st.metric("Level", level)

with metric3:
    st.metric("Mode", mode)

with metric4:
    resume_status = "Uploaded" if st.session_state.resume_text else "Pending"
    st.metric("Resume Status", resume_status)

total_attempts = len(st.session_state.feedback_history)

if st.session_state.scores:
    average_score = sum(st.session_state.scores) / len(st.session_state.scores)
    best_score = max(st.session_state.scores)
else:
    average_score = 0
    best_score = 0

readiness_level = get_readiness_level(average_score)

show_panel(
    "Analytics",
    "Performance Intelligence Dashboard",
    "Track attempts, average score, best score, interview readiness, and improvement progress using visual analytics.",
)

score_col1, score_col2, score_col3, score_col4 = st.columns(4)

with score_col1:
    st.metric("Total Attempts", total_attempts)

with score_col2:
    st.metric("Average Score", f"{average_score:.1f}/10")

with score_col3:
    st.metric("Best Score", f"{best_score}/10")

with score_col4:
    st.metric("Readiness", readiness_level)

if st.session_state.scores:
    if readiness_level == "Interview Ready":
        st.success("You are interview ready. Keep practicing with advanced questions.")
    elif readiness_level == "Almost Ready":
        st.warning("You are close. Improve answer structure and role-specific examples.")
    else:
        st.error("More practice needed. Focus on clear, structured answers.")

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
    st.info("Complete at least one evaluated answer to see performance analytics.")

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

show_panel(
    "Interview Workspace",
    "Question & Answer Studio",
    "Generate AI interview questions, answer them by text or voice, and receive detailed role-specific feedback.",
)

if mode == "Single Question":
    if st.button("Generate Interview Question"):
        with st.spinner("Generating interview question..."):
            st.session_state.question = generate_interview_question(
                role,
                level,
                question_type,
                st.session_state.resume_text,
            )

        st.session_state.transcribed_answer = ""
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
            questions_text = generate_multiple_questions(
                role,
                level,
                question_type,
                st.session_state.resume_text,
                question_count,
            )

        st.session_state.multiple_questions = split_questions(questions_text)
        st.session_state.multiple_answers = {}
        st.session_state.history.append(questions_text)

    if st.session_state.multiple_questions:
        st.subheader("Answer Multiple Interview Questions")

        for index, question in enumerate(st.session_state.multiple_questions, start=1):
            st.markdown(f"### Question {index}")
            st.info(question)

            answer_key = f"multiple_answer_{index}"

            answer = st.text_area(
                f"Your Answer for Question {index}",
                height=160,
                key=answer_key,
                placeholder="Write your answer here...",
            )

            st.session_state.multiple_answers[answer_key] = answer

        if st.button("Evaluate All Answers"):
            answered_any = False

            for index, question in enumerate(st.session_state.multiple_questions, start=1):
                answer_key = f"multiple_answer_{index}"
                answer = st.session_state.multiple_answers.get(answer_key, "")

                if not answer.strip():
                    st.warning(f"Question {index} skipped because answer is empty.")
                    continue

                answered_any = True

                with st.spinner(f"Evaluating answer {index}..."):
                    feedback = evaluate_answer(
                        question,
                        answer,
                        role,
                        st.session_state.resume_text,
                    )

                score = extract_score(feedback)

                st.session_state.feedback_history.append(
                    {
                        "question": question,
                        "answer": answer,
                        "feedback": feedback,
                        "score": score,
                    }
                )

                if score > 0:
                    st.session_state.scores.append(score)

                with st.expander(f"Feedback for Question {index} - Score: {score}/10"):
                    st.markdown(feedback)

            if not answered_any:
                st.error("Please answer at least one question before evaluation.")

show_panel(
    "AI Review Center",
    "History, Feedback & Final Summary",
    "Review generated questions, evaluated answers, score history, and generate a final AI-powered interview performance summary.",
)

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
        with st.expander(f"Attempt {index} - Score: {item['score']}/10"):
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
