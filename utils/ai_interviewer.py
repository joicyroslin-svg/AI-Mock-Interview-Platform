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
- If resume is provided, make question related to resume projects/skills
- Keep it realistic for internships and fresher interviews
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

Evaluate the answer in this format:

## Score
Give score out of 10.

## What Was Good
Mention strengths in the answer.

## What Can Be Improved
Mention mistakes or missing points.

## Better Sample Answer
Give a better beginner-friendly answer.

## Confidence Tip
Give one practical tip to answer better in interviews.

Keep feedback simple, practical, and useful for a student/fresher.
"""

    return ask_gemini(prompt)