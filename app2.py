import streamlit as st
from pypdf import PdfReader
import sqlite3
import re
import time
import random
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Exam System PRO MAX",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# DATABASE
# ==========================================
conn = sqlite3.connect("exam.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    score INTEGER,
    total INTEGER,
    level TEXT,
    date TEXT
)
""")

conn.commit()

# ==========================================
# PDF READER
# ==========================================
def read_pdf(file):

    try:
        text = ""

        reader = PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

        text = text.replace("\n", " ")

        return text[:20000]

    except Exception as e:
        st.error(f"PDF Error: {e}")
        return ""

# ==========================================
# OPENAI AI GENERATOR
# ==========================================
def ai_generate_questions(text, n):

    api_key = os.getenv("")

    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are an elite university professor.

Generate {n} EXTREMELY HARD multiple choice questions.

Requirements:
- Questions must test:
  - deep understanding
  - inference
  - analysis
  - critical thinking
- Avoid direct memorization questions
- Make distractors realistic
- Each question MUST contain:
  - q
  - options
  - answer
  - explanation

Return ONLY valid JSON.

Example:
[
  {{
    "q": "Question here",
    "options": ["A","B","C","D"],
    "answer": "A",
    "explanation": "Explanation here"
  }}
]

TEXT:
{text}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You generate only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        # تنظيف JSON
        content = content.replace("```json", "")
        content = content.replace("```", "")

        questions = json.loads(content)

        valid_questions = []

        for q in questions:

            if (
                isinstance(q, dict)
                and "q" in q
                and "options" in q
                and "answer" in q
                and "explanation" in q
                and len(q["options"]) == 4
            ):
                valid_questions.append(q)

        if len(valid_questions) > 0:
            return valid_questions

        return None

    except Exception as e:
        st.warning(f"AI Error: {e}")
        return None

# ==========================================
# OFFLINE FALLBACK
# ==========================================
def fallback_questions(text, n):

    sentences = re.split(r"[.!?]", text)

    sentences = [
        s.strip()
        for s in sentences
        if len(s.split()) > 10
    ]

    if len(sentences) == 0:
        sentences = [
            "Artificial Intelligence improves problem solving.",
            "Machine learning depends on data quality.",
            "Deep learning uses neural networks."
        ]

    random.shuffle(sentences)

    questions = []

    for i in range(min(n, len(sentences))):

        s = sentences[i]

        q_type = random.choice([
            "analysis",
            "inference",
            "critical"
        ])

        if q_type == "analysis":
            q = f"What is the BEST analytical interpretation of:\n\n{s}"

        elif q_type == "inference":
            q = f"What can logically be inferred from:\n\n{s}"

        else:
            q = f"What is the strongest critical evaluation of:\n\n{s}"

        words = s.split()

        correct = " ".join(words[:5])

        options = [
            correct,
            "An unrelated conclusion",
            "A partially correct misunderstanding",
            "An unsupported assumption"
        ]

        random.shuffle(options)

        questions.append({
            "q": q,
            "options": options,
            "answer": correct,
            "explanation": s
        })

    return questions

# ==========================================
# LEVEL SYSTEM
# ==========================================
def level(score, total):

    if total == 0:
        return "⚠️ Beginner"

    ratio = score / total

    if ratio >= 0.85:
        return "🔥 Expert"

    elif ratio >= 0.60:
        return "⚡ Intermediate"

    else:
        return "⚠️ Beginner"

# ==========================================
# CERTIFICATE
# ==========================================
def generate_certificate(name, score, total, lvl):

    filename = f"certificate_{name}.pdf"

    pdf = canvas.Canvas(filename, pagesize=letter)

    width, height = letter

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width / 2, 750, "AI UNIVERSITY CERTIFICATE")

    pdf.setFont("Helvetica", 16)

    pdf.drawString(100, 650, f"Student Name: {name}")
    pdf.drawString(100, 610, f"Score: {score}/{total}")
    pdf.drawString(100, 570, f"Level: {lvl}")
    pdf.drawString(100, 530, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    pdf.setFont("Helvetica-Bold", 18)

    pdf.drawCentredString(
        width / 2,
        450,
        "Successfully Completed AI Examination"
    )

    pdf.save()

    return filename

# ==========================================
# TITLE
# ==========================================
st.title("🧠 AI Exam System PRO MAX")

st.markdown("### Generate HARD AI-powered exams from PDFs")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("⚙️ Settings")

name = st.text_input("👤 Student Name")

pdf = st.file_uploader(
    "📄 Upload PDF",
    type=["pdf"]
)

q_count = st.sidebar.slider(
    "❓ Number of Questions",
    5,
    20,
    10
)

duration = st.sidebar.slider(
    "⏱️ Exam Duration (Minutes)",
    1,
    60,
    10
)

# ==========================================
# START EXAM
# ==========================================
if st.button("🚀 Start AI Exam"):

    if not name:
        st.error("Please enter your name.")

    elif not pdf:
        st.error("Please upload a PDF.")

    else:

        text = read_pdf(pdf)

        if len(text.strip()) < 100:
            st.error("PDF text is too short or unreadable.")

        else:

            with st.spinner("🧠 AI is generating HARD questions..."):

                questions = ai_generate_questions(text, q_count)

                if questions is None:

                    st.warning(
                        "AI unavailable or quota exceeded → Using Offline Mode"
                    )

                    questions = fallback_questions(text, q_count)

                st.session_state.questions = questions
                st.session_state.start_time = time.time()
                st.session_state.duration = duration * 60
                st.session_state.submitted = False
                st.session_state.lock = False

            st.success("✅ Exam Generated Successfully!")

# ==========================================
# TIMER
# ==========================================
if "questions" in st.session_state:

    elapsed = time.time() - st.session_state.start_time

    remaining = int(
        st.session_state.duration - elapsed
    )

    if remaining <= 0:
        remaining = 0
        st.session_state.lock = True

    mins = remaining // 60
    secs = remaining % 60

    st.warning(f"⏱️ Time Left: {mins}:{secs:02d}")

    if st.session_state.lock:
        st.error("⛔ TIME OVER")

# ==========================================
# QUESTIONS
# ==========================================
if "questions" in st.session_state:

    st.subheader("📘 Exam Questions")

    for i, q in enumerate(st.session_state.questions):

        st.markdown(f"### Q{i+1}")

        st.write(q["q"])

        if not st.session_state.lock:

            st.radio(
                "Choose Answer",
                q["options"],
                key=f"answer_{i}"
            )

        st.divider()

# ==========================================
# SUBMIT
# ==========================================
if (
    "questions" in st.session_state
    and not st.session_state.get("submitted", False)
):

    if st.button("✅ Submit Exam") or st.session_state.lock:

        score = 0

        total = len(st.session_state.questions)

        st.subheader("🧠 AI Analysis")

        for i, q in enumerate(st.session_state.questions):

            selected = st.session_state.get(f"answer_{i}")

            if selected == q["answer"]:

                score += 1

                st.success(f"Q{i+1}: Correct ✅")

            else:

                st.error(f"Q{i+1}: Wrong ❌")

                st.write(f"✅ Correct Answer: {q['answer']}")

            with st.expander(f"📖 Explanation Q{i+1}"):

                st.write(q["explanation"])

        lvl = level(score, total)

        st.success(f"🎯 Final Score: {score}/{total}")

        st.info(f"📊 Your Level: {lvl}")

        # Save Result
        c.execute(
            """
            INSERT INTO results
            (name, score, total, level, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                score,
                total,
                lvl,
                str(datetime.now())
            )
        )

        conn.commit()

        # Generate Certificate
        cert_file = generate_certificate(
            name,
            score,
            total,
            lvl
        )

        with open(cert_file, "rb") as f:

            st.download_button(
                "🎓 Download Certificate",
                f,
                file_name=cert_file,
                mime="application/pdf"
            )

        st.session_state.submitted = True

# ==========================================
# RANKING
# ==========================================
st.sidebar.title("🏆 Ranking")

c.execute("""
SELECT name, score, total, level
FROM results
ORDER BY score DESC
LIMIT 10
""")

ranking = c.fetchall()

if ranking:

    for i, row in enumerate(ranking):

        st.sidebar.write(
            f"{i+1}. {row[0]} — {row[1]}/{row[2]} ({row[3]})"
        )

else:
    st.sidebar.info("No results yet.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("🚀 AI Exam System PRO MAX | Powered by OpenAI + Streamlit")