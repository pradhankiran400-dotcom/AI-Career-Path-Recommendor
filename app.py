from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from groq import Groq
import io
from pypdf import PdfReader
import json
import os
from tavily import TavilyClient
from dotenv import load_dotenv

# .env file ko load karo
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    raise RuntimeError("❌ API Keys are missing in the .env file!")

# API Clients Setup
tavily = TavilyClient(api_key=TAVILY_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        request, "error.html",
        {"request": request, "error_message": exc.detail},
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request, "error.html",
        {"request": request, "error_message": f"An unexpected error occurred: {str(exc)}"},
        status_code=500
    )

JOB_ROLES = [
    # Core & Traditional Development
    "Frontend Developer", 
    "Backend Developer", 
    "Full Stack Developer",
    "Android Developer",
    "iOS Developer",
    "Software Engineer",
    
    # Data & Infrastructure
    "Data Scientist", 
    "DevOps Engineer",
    "Cloud Architect",
    "Database Administrator",
    "Systems Administrator",
    "Site Reliability Engineer (SRE)",
    
    # QA & Product
    "QA Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Cybersecurity Analyst",
    
    # Recent & Emerging AI Roles
    "Prompt Engineer",
    "LLM Engineer (Large Language Model)",
    "Machine Learning Engineer",
    "MLOps Engineer",
    "Generative AI Developer",
    "AI Product Manager",
    "AI Solutions Architect",
    "Adversarial Prompt Engineer / AI Red Teamer",
    "AI Ethics & Compliance Specialist",
    "Data Annotation Specialist",
    "AI Trainer"
]
POPULAR_SKILLS = ["HTML", "CSS", "JavaScript", "React", "Node.js", "Python", "SQL", "MongoDB", "Java", "Kotlin", "Docker", "AWS", "Git"]

def fetch_resources(skill: str):
    results = tavily.search(
        query=f"best free tutorial to learn {skill} for beginners 2024",
        max_results=2
    )
    return [{"title": r["title"], "url": r["url"]} for r in results.get("results", [])]

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request, 'index.html',
        {"request": request, "jobs": JOB_ROLES, "all_skills": POPULAR_SKILLS}
    )

@app.get('/about', response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(
        request, 'error.html',
        {"request": request, "error_message": "Welcome to the AI Career Path Recommendor! This project bridges the gap between your current tech skills and your dream job."}
    )

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    target_job: str = Form(...),
    typed_skills: str = Form(None),
    manual_skills: list[str] = Form(None),
    resume_file: UploadFile = File(None)
):
    detected_skill = ""

    if typed_skills:
        detected_skill += typed_skills + ','
    if manual_skills:
        detected_skill += ','.join(manual_skills)

    if resume_file and resume_file.filename.endswith('.pdf'):
        try:
            contents = await resume_file.read()
            pdf_data = io.BytesIO(contents)
            reader = PdfReader(pdf_data)
            for page in reader.pages:
                detected_skill += page.extract_text() or ""
        except Exception as pdf_err:
            print(f"PDF read error: {pdf_err}")

    system_prompt = f"""
    You are an expert tech career advisor. 
    User wants to become a "{target_job}".
    User's current skills: "{detected_skill if detected_skill else 'None Specified'}".
    
    Analyze the gap and return a response strictly in valid JSON format with the following keys:
    1. "user_skills": List of relevant modern skills you identified from the user's data.
    2. "missing_skills": List of critical skills they lack for the target job.
    3. "roadmap": A list of exactly 4 sequential steps/milestones. Each item must have keys: "step" (int), "title" (string), "desc" (string), and "status" (string, either "Learning Needed 📕" or "Already Know ✨").
    
    Do not add markdown wrappers like ```json. Return raw JSON string only.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful tech career advisor. Always respond with raw valid JSON only. No markdown, no extra text."},
                {"role": "user", "content": system_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"} 
        )

        raw_text = response.choices[0].message.content.strip()
        ai_data = json.loads(raw_text)

        for item in ai_data.get("roadmap", []):
            step_title = item.get("title", target_job)
            try:
                item["resources"] = fetch_resources(step_title)
            except Exception as tavily_err:
                print(f"Tavily Error for {step_title}: {tavily_err}")
                item["resources"] = []

    except Exception as e:
        error_detail = f"AI Error: {type(e).__name__}: {str(e)}"
        print(f"[ERROR] {error_detail}")
        return templates.TemplateResponse(
            request, "error.html",
            {"request": request, "error_message": error_detail},
            status_code=500
        )

    return templates.TemplateResponse(
        request, 'roadmap.html',
        {
            "request": request,
            "target_job": target_job,
            "user_skills": ai_data.get("user_skills", []),
            "missing_skills": ai_data.get("missing_skills", []),
            "roadmap": ai_data.get("roadmap", [])
        }
    )