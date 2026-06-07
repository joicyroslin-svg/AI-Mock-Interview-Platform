import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def get_client():
    api_key = get_api_key()

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def ask_gemini(prompt):
    client = get_client()

    if not client:
        return "Gemini API key is missing. Please add GEMINI_API_KEY."

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            if response and response.text:
                return response.text

        except Exception:
            continue

    return "AI model is temporarily busy. Please try again after some time."


def generate_interview_question(role, level, question_type, resume_text=""):
    prompt = f"""
You are an expert interview coach.

Generate one interview question for a candidate.

Role: {role}
Level: {level}
Question Type: {question_type}

Candidate Resume:
{resume_text}

Rules:
- Ask only one question
- If resume is provided, make the question related to resume projects, skills, or experience
- For Beginner level, ask simple conceptual or HR questions
- For Intermediate level, ask project-based and practical questions
- For Advanced level, ask scenario-based, system-design, debugging, optimization, or real-world problem-solving questions
- Make the question realistic for internships and fresher interviews
- Do not include the answer
"""

    return ask_gemini(prompt)


def generate_multiple_questions(role, level, question_type, resume_text="", count=5):
    prompt = f"""
You are an expert interview coach.

Generate {count} interview questions.

Role: {role}
Level: {level}
Question Type: {question_type}

Candidate Resume:
{resume_text}

Rules:
- Give numbered questions
- Make questions practical and realistic
- If resume is provided, ask questions based on resume skills and projects
- Mix basic, project-based, and scenario-based questions
- Do not include answers
"""

    return ask_gemini(prompt)


def evaluate_answer(question, answer, role, resume_text=""):
    prompt = f"""
You are an expert interview evaluator.

Role: {role}

Candidate Resume:
{resume_text}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer in this exact format:

Score: X/10

Answer Quality:
Explain whether the answer is clear, complete, and relevant.

What Was Good:
Mention strengths in the answer.

What Can Be Improved:
Mention missing points, weak explanation, or unclear parts.

Better Sample Answer:
Give a stronger beginner-friendly answer.

Role-Specific Tip:
Give one tip based on the selected role.

Confidence Tip:
Give one practical speaking/interview confidence tip.

Rules:
- Score must be between 1 and 10
- Give specific feedback, not generic feedback
- Keep it useful for a student/fresher
- Be honest but encouraging
"""

    return ask_gemini(prompt)


def transcribe_audio_answer(audio_bytes, mime_type="audio/wav"):
    client = get_client()

    if not client:
        return "Gemini API key is missing. Please add GEMINI_API_KEY."

    prompt = """
Transcribe this interview answer audio into clean text.

Rules:
- Return only the transcript
- Do not add feedback
- Do not summarize
- Keep the candidate's meaning
"""

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type,
                    ),
                ],
            )

            if response and response.text:
                return response.text

        except Exception:
            continue

    return "Audio transcription failed. Please type your answer manually."
def generate_final_interview_summary(role, level, feedback_history):
    if not feedback_history:
        return "No interview attempts found. Please complete at least one answer evaluation."

    attempts_text = ""

    for index, item in enumerate(feedback_history, start=1):
        attempts_text += f"""
Attempt {index}

Question:
{item["question"]}

Candidate Answer:
{item["answer"]}

Score:
{item["score"]}/10

AI Feedback:
{item["feedback"]}
"""

    prompt = f"""
You are an expert interview coach.

Analyze this candidate's complete mock interview performance.

Role: {role}
Level: {level}

Interview Attempts:
{attempts_text}

Give final performance summary in this format:

## Overall Interview Performance
Explain how the candidate performed overall.

## Strengths
List the candidate's strengths.

## Weak Areas
List areas that need improvement.

## Communication Feedback
Give feedback on clarity, confidence, and structure.

## Technical Preparation Advice
Give role-specific technical preparation advice.

## Next 7-Day Practice Plan
Give a practical 7-day improvement plan.

Keep it simple, honest, and useful for a student/fresher.
"""

    return ask_gemini(prompt)