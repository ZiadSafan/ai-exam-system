# 🧠 AI Exam System PRO MAX

An advanced, AI-powered examination platform built with **Streamlit** and **OpenAI**. This system allows users to upload academic PDF files and automatically generates highly challenging, university-level multiple-choice questions (MCQs) designed to test deep understanding, critical thinking, and analysis.

---

## 🚀 Features

* **AI Question Generation:** Integrates with OpenAI's API to generate challenging context-aware exams based on uploaded PDF content.
* **Offline Fallback Mode:** Seamlessly switches to a local keyword/text parsing system if the AI API is unavailable or has exceeded its quota.
* **Live Timer:** Dynamic quiz countdown timer that automatically locks the exam when the time is up.
* **Database Tracking:** Local SQLite integration to store student names, final scores, and difficulty ranks.
* **Dynamic Certificates:** Automatically generates a professional PDF certificate using `ReportLab` upon completion.
* **Live Leaderboard:** Real-time sidebar ranking showing the top 10 historical student scores.

---

## 🛠️ Tech Stack & Dependencies

* **Frontend/UI:** Streamlit
* **AI Model:** OpenAI API (`gpt-4.1-mini`)
* **PDF Processing:** PyPDF (`PdfReader`)
* **Database:** SQLite3
* **PDF Generation:** ReportLab
* **Backend Utilities:** Regex, Time, JSON, Datetime

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
   cd YOUR_REPOSITORY_NAME