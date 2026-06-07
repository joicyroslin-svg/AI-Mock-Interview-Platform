# AI Mock Interview Platform

AI Mock Interview Platform is an AI-powered interview practice dashboard that helps users prepare for job interviews through role-based questions, resume-based questions, typed answers, voice answers, AI feedback, performance analytics, and downloadable interview reports.

## Live Demo

[Try the App](https://ai-mock-interview-platform.streamlit.app/)

## Project Demo Screen Recording

Watch the screen recording of the AI Mock Interview Platform workflow:

[View Demo Video](assets/ai-mock-interview-demo.mp4)

## Project Overview

This project is designed to help students, freshers, and job seekers practice interviews in a more realistic and personalized way.

Instead of only giving random questions, the platform can generate questions based on:

* Selected job role
* Difficulty level
* Question type
* Uploaded resume
* User’s previous answers and performance

The app uses Gemini AI to generate questions, evaluate answers, transcribe voice answers, and create final interview performance summaries.

## Features

* Role-based interview question generation
* Resume-based interview questions
* Beginner, intermediate, and advanced levels
* HR, technical, project-based, scenario-based, and resume-based questions
* Single question mode
* Multiple question mode
* Answer boxes for multiple questions
* Typed answer evaluation
* Voice answer recording
* AI voice transcription
* AI-powered answer feedback
* Score out of 10 for each answer
* Interview performance dashboard
* Average score and best score tracking
* Interview readiness level
* Score trend visualization
* Attempt-wise score analysis
* Question history
* Feedback history
* Downloadable interview report
* Final AI interview performance summary
* Deployed on Streamlit Cloud

## Supported Job Roles

* AI/ML Intern
* Generative AI Engineer
* Data Analyst
* Data Scientist
* Python Developer
* Backend Developer
* Full Stack Developer
* Computer Vision Intern
* NLP Intern
* MLOps Engineer
* Prompt Engineer
* AI Product Analyst
* Business Analyst
* Product Manager
* Technical Writer
* Software Engineer Intern

## Tech Stack

* Python
* Streamlit
* Gemini API
* Google GenAI SDK
* Plotly
* Pandas
* PDFPlumber
* Python-dotenv
* Git & GitHub
* Streamlit Community Cloud

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/joicyroslin-svg/AI-Mock-Interview-Platform.git
```

Move into the project folder:

```bash
cd AI-Mock-Interview-Platform
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not upload the `.env` file to GitHub.

## Deployment

This project is deployed on Streamlit Community Cloud.

For deployment, add the Gemini API key in Streamlit Secrets:

```toml
GEMINI_API_KEY = "your_real_api_key_here"
```

## Project Structure

```text
AI-Mock-Interview-Platform/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
│
├── utils/
│   ├── ai_interviewer.py
│   └── pdf_reader.py
│
├── assets/
│   └── ai-mock-interview-demo.mp4
│
└── resumes/
```

## What I Learned

While building this project, I learned how to:

* Connect Gemini API with a Streamlit app
* Generate interview questions using AI
* Create resume-based interview questions
* Evaluate user answers using AI
* Add voice answer recording and transcription
* Track interview performance using scores
* Build performance visualizations using Plotly
* Create downloadable interview reports
* Deploy an AI app on Streamlit Cloud
* Secure API keys using `.env` and Streamlit Secrets

## Future Improvements

* Add login system
* Add user interview history database
* Add company-specific interview preparation
* Add coding interview question mode
* Add webcam-based confidence analysis
* Add speech clarity and speaking speed analysis
* Add PDF performance report download
* Add real job description-based interview simulation
* Add multi-round interview mode

## Resume Description

AI Mock Interview Platform — Built an AI-powered Streamlit mock interview platform that generates role-based and resume-based interview questions, evaluates typed and voice answers using Gemini AI, tracks interview performance analytics, and generates downloadable interview reports.

## Author

Joicy Roslin

GitHub: [joicyroslin-svg](https://github.com/joicyroslin-svg)

Live App: [AI Mock Interview Platform](https://ai-mock-interview-platform.streamlit.app/)
