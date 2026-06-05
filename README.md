# 🚀 AI Career Path Recommendor

Bridge the gap between your current tech skills and your dream job! This intelligent web application analyzes a user's current skill set—either typed manually or parsed directly from a PDF resume—and generates a personalized, step-by-step learning roadmap.

By leveraging Generative AI (Groq/Llama 3) for structured milestone generation and a RAG pipeline (Tavily API) for fetching real-time, high-quality learning resources, this tool provides actionable guidance for aspiring tech professionals.

---

## ✨ Features
* **Resume Parsing:** Automatically extracts skills from uploaded PDF resumes using `PyPDF`.
* **Smart Gap Analysis:** Compares current skills against industry requirements for target roles (e.g., Data Scientist, Backend Developer).
* **AI-Powered Roadmaps:** Generates a structured, 4-step chronological learning plan in strict JSON format using **Groq (Llama-3.3-70b)**.
* **Resources-fetch** Dynamically fetches the best free YouTube tutorials and articles for missing skills using the **Tavily Search API**.
* **Responsive UI:** Clean, modern, and user-friendly interface built with HTML, CSS, and Jinja2 templates.

---

## 🛠️ Tech Stack
* **Backend:** FastAPI, Python
* **AI & LLM:** Groq API (Llama 3)
* **Search/RAG:** Tavily API
* **Document Processing:** PyPDF
* **Frontend:** HTML5, CSS3, Jinja2
