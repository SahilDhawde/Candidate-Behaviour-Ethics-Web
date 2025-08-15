import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import io
import os

# -----------------------------
# MCQ Questions Setup
# -----------------------------
questions = [
    {
        "dimension": "Integrity",
        "question": "You notice a colleague is acting against company policy. What would you do?",
        "options": [
            ("Ignore it", 25),
            ("Tell a teammate only", 50),
            ("Privately talk to them", 75),
            ("Report to the supervisor and document it", 100)
        ]
    },
    {
        "dimension": "Teamwork",
        "question": "A teammate disagrees with your approach. How do you handle it?",
        "options": [
            ("Stick to my own way", 25),
            ("Avoid discussion", 50),
            ("Discuss and compromise", 75),
            ("Actively seek their input and adjust plan", 100)
        ]
    },
    {
        "dimension": "Accountability",
        "question": "You made a mistake that impacted the team. What would you do?",
        "options": [
            ("Deny involvement", 25),
            ("Blame circumstances", 50),
            ("Acknowledge but don't fix it", 75),
            ("Acknowledge, apologize, and fix it", 100)
        ]
    },
    {
        "dimension": "Proactiveness",
        "question": "You identify an opportunity to improve a process outside your role. What do you do?",
        "options": [
            ("Ignore it", 25),
            ("Mention it casually", 50),
            ("Propose improvement to team", 75),
            ("Research, propose, and take lead", 100)
        ]
    },
    {
        "dimension": "Adaptability",
        "question": "A project scope changes suddenly. How do you react?",
        "options": [
            ("Complain about the change", 25),
            ("Resist but adjust slowly", 50),
            ("Adjust and manage priorities", 75),
            ("Quickly adapt and help others adapt", 100)
        ]
    },
    {
        "dimension": "Punctuality",
        "question": "You are running late for work. You will:",
        "options": [
            ("Not inform anyone", 25),
            ("Send a quick text to a colleague", 50),
            ("Call your supervisor and explain", 75),
            ("Inform in advance and make up lost time", 100)
        ]
    },
    {
        "dimension": "Responsibility",
        "question": "A client reports an error you made. You will:",
        "options": [
            ("Ignore and hope it goes unnoticed", 25),
            ("Blame technical issues", 50),
            ("Admit the mistake but don’t fix it", 75),
            ("Take full responsibility and correct it immediately", 100)
        ]
    },
    {
        "dimension": "Confidentiality",
        "question": "You accidentally receive confidential company data. You will:",
        "options": [
            ("Share it with colleagues", 25),
            ("Keep it but don’t tell anyone", 50),
            ("Report it to IT or HR", 75),
            ("Delete securely and inform relevant authority", 100)
        ]
    },
    {
        "dimension": "Work Ethic",
        "question": "You have finished your tasks early. You will:",
        "options": [
            ("Relax until the day ends", 25),
            ("Browse social media", 25),
            ("Ask for more tasks", 75),
            ("Help others or improve work processes", 100)
        ]
    },
    {
        "dimension": "Initiative",
        "question": "You spot an inefficient process in the workplace. You will:",
        "options": [
            ("Ignore it", 25),
            ("Complain to others", 50),
            ("Mention it to your supervisor", 75),
            ("Propose and help implement a better solution", 100)
        ]
    }
]

# -----------------------------
# Session State Init
# -----------------------------
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# -----------------------------
# Candidate Info Form
# -----------------------------
st.title("Candidate Behaviour & Work Ethics MCQ Evaluation")

with st.form("candidate_info"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    role = st.text_input("Role Applied For")
    submitted_info = st.form_submit_button("Start Questionnaire")

if submitted_info:
    if not name or not email or not role:
        st.warning("Please fill in all details before starting.")
    else:
        st.session_state.name = name
        st.session_state.email = email
        st.session_state.role = role

# -----------------------------
# Questionnaire
# -----------------------------
if 'name' in st.session_state and not st.session_state.submitted:
    with st.form("mcq_form"):
        st.subheader("Answer the following questions:")
        for i, q in enumerate(questions):
            choice = st.radio(q["question"], [opt[0] for opt in q["options"]], key=f"q_{i}")
            st.session_state.answers[i] = choice
        submit_answers = st.form_submit_button("Submit Answers")
    if submit_answers:
        st.session_state.submitted = True

# -----------------------------
# Results Processing
# -----------------------------
if st.session_state.submitted:
    st.success("Thank you for submitting your responses.")
    if st.button("View Results"):
        scores = {}
        total_score = 0
        for i, q in enumerate(questions):
            selected_option = st.session_state.answers[i]
            for opt, score in q["options"]:
                if opt == selected_option:
                    scores[q["dimension"]] = score
                    total_score += score
        avg_score = total_score / len(questions)
        recommendation = "Proceed to Next Round" if avg_score >= 70 else "Do Not Proceed"

        # Pie chart
        fig, ax = plt.subplots()
        ax.pie(scores.values(), labels=scores.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        # Table
        df = pd.DataFrame(list(scores.items()), columns=["Dimension", "Score"])
        st.table(df)

        st.write(f"**Average Score:** {avg_score:.2f}")
        st.write(f"**Recommendation:** {recommendation}")

        # PDF generation
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Candidate Behaviour & Work Ethics Report", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Name: {st.session_state.name}", ln=True)
        pdf.cell(0, 10, f"Email: {st.session_state.email}", ln=True)
        pdf.cell(0, 10, f"Role: {st.session_state.role}", ln=True)
        pdf.cell(0, 10, "", ln=True)
        pdf.cell(0, 10, "Scores:", ln=True)
        for dim, score in scores.items():
            pdf.cell(0, 10, f"{dim}: {score}", ln=True)
        pdf.cell(0, 10, f"Average Score: {avg_score:.2f}", ln=True)
        pdf.cell(0, 10, f"Recommendation: {recommendation}", ln=True)

        # Save pie chart to image and insert in PDF
        fig, ax = plt.subplots()
        ax.pie(df["Score"], labels=df["Dimension"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Behaviour & Work Ethics Score Distribution")
        fig.savefig("chart.png", format="PNG")
        plt.close(fig)
        pdf.image("chart.png", x=10, y=None, w=100)

        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="Download PDF Report",
            data=pdf_output,
            file_name=f"{st.session_state.name}_report.pdf",
            mime='application/pdf'
        )

        
