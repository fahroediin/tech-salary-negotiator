from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

from database import init_database, get_db_connection
from models import OfferAnalysisCreate
from services.offer_parser import OfferLetterParser
from services.salary_analyzer import SalaryAnalyzer
from services.script_generator import NegotiationScriptGenerator
from routes import umk_admin

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_database()
    yield
    # Cleanup if needed

app = FastAPI(
    title="Tech Salary Negotiator",
    description="AI-powered salary negotiation helper for tech professionals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for authentication (placeholder)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Include routers
app.include_router(umk_admin.router)

# Initialize services
offer_parser = OfferLetterParser()
salary_analyzer = SalaryAnalyzer()
script_generator = NegotiationScriptGenerator()

@app.get("/")
async def root():
    return {"message": "Tech Salary Negotiator API", "version": "1.0.0"}

@app.post("/api/analyze-offer")
async def analyze_offer(
    file: UploadFile = File(...),
    years_experience: int = Form(...),
    tech_stack: str = Form(...),
    current_salary: int = Form(None),
    has_competing_offers: bool = Form(False)
):
    """
    Analyze a job offer from uploaded PDF/PDF file
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.PDF')):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Read file content
        file_content = await file.read()

        # Parse offer letter
        logger.info(f"Parsing offer letter: {file.filename}")
        offer_data = await offer_parser.parse_pdf(file_content)

        # Add user profile data
        offer_data['years_experience'] = years_experience
        offer_data['tech_stack'] = [tech.strip() for tech in tech_stack.split(',')]
        offer_data['current_salary'] = current_salary
        offer_data['has_competing_offers'] = has_competing_offers

        # Analyze offer
        logger.info("Analyzing offer with AI")
        analysis_result = await salary_analyzer.analyze_offer(offer_data)

        # Generate negotiation scripts
        user_profile = {
            'years_experience': years_experience,
            'current_salary': current_salary or 0,
            'tech_stack': offer_data['tech_stack'],
            'has_competing_offers': has_competing_offers
        }

        scripts = await script_generator.generate_scripts(analysis_result, user_profile)

        # Save analysis to database (placeholder for now)
        # await save_analysis(offer_data, analysis_result, scripts)

        return {
            "success": True,
            "data": {
                "offer_data": offer_data,
                "analysis": analysis_result,
                "scripts": scripts
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing offer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contribute-salary")
async def contribute_salary(
    job_title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    base_salary: int = Form(...),
    bonus: int = Form(0),
    equity_value: int = Form(0),
    years_experience: int = Form(...),
    tech_stack: str = Form(...)
):
    """
    Contribute anonymous salary data to help others
    """
    try:
        from services.salary_contribution import SalaryContributionService

        contribution_service = SalaryContributionService(os.getenv("DATABASE_URL"))

        data = {
            'job_title': job_title,
            'company': company,
            'location': location,
            'base_salary': base_salary,
            'bonus': bonus,
            'equity_value': equity_value,
            'years_experience': years_experience,
            'tech_stack': [tech.strip() for tech in tech_stack.split(',')]
        }

        result = await contribution_service.submit_salary_data(data)

        return result

    except Exception as e:
        logger.error(f"Error contributing salary data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()

        return {
            "status": "healthy",
            "database": "connected",
            "gemini_api": "configured" if os.getenv("GEMINI_API_KEY") else "missing"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )