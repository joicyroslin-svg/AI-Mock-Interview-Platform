# utils/ai_interviewer.py

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

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


def generate_interview_question(role, level, question_type):
    client = get_client()

    if not client:
        return "Gemini API key is missing. Please add GEMINI_API_KEY."

    prompt = f"""
You are an expert interview coach.

Generate one interview question for a candidate.

Role: {role}
Level: {level}
Question Type: {question_type}

Rules:
- Ask only one question
- Keep it clear and realistic
- Suitable for students/freshers
- Do not include answer
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception:
        return "AI model is busy. Please try again."


def evaluate_answer(question, answer, role):
    client = get_client()

    if not client:
        return "Gemini API key is missing. Please add GEMINI_API_KEY."

    prompt = f"""
You are an expert interview evaluator.

Role: {role}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer in this format:

1. Score out of 10
2. What was good
3. What can be improved
4. Better sample answer
5. Confidence improvement tip

Keep the feedback beginner-friendly and practical.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text

    except Exception:
        return "AI model is busy. Please try again."