from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Create database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salary_negotiator.db")

# SQLite special configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class SalaryData(Base):
    __tablename__ = "salary_data"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(200), nullable=False)
    normalized_title = Column(String(100), nullable=False, index=True)
    company = Column(String(200))
    company_tier = Column(String(20))
    location = Column(String(100), nullable=False)
    location_tier = Column(String(20), index=True)
    base_salary = Column(Integer, nullable=False)
    bonus = Column(Integer, default=0)
    equity_value = Column(Integer, default=0)
    total_comp = Column(Integer, nullable=False)
    years_experience = Column(Integer, nullable=False, index=True)
    tech_stack = Column(JSON)  # Store as JSON
    benefits = Column(JSON)
    is_verified = Column(Boolean, default=False, index=True)
    confidence_score = Column(Float)
    submission_hash = Column(String(64), unique=True)
    submitted_date = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        CheckConstraint('base_salary BETWEEN 20000 AND 1000000'),
    )

class OfferAnalysis(Base):
    __tablename__ = "offer_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)  # UUID as string
    session_id = Column(String(100))
    offer_data = Column(JSON, nullable=False)
    analysis_result = Column(JSON, nullable=False)
    market_data = Column(JSON)
    generated_scripts = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class NegotiationOutcome(Base):
    __tablename__ = "negotiation_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer)
    outcome = Column(String(50))
    final_salary = Column(Integer)
    increase_amount = Column(Integer)
    increase_percentage = Column(Float)
    user_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    subscription_tier = Column(String(20), default='free')
    subscription_expires = Column(DateTime)
    analyses_used = Column(Integer, default=0)
    analyses_limit = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

def init_database():
    """
    Initialize database tables and sample data
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # Check if we need to add sample data
        add_sample_data()

        logger.info("✅ Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False

def get_db() -> Session:
    """
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    """
    Get database connection for raw SQL queries
    """
    return engine.connect()

def add_sample_data():
    """
    Add sample data if tables are empty
    """
    try:
        db = SessionLocal()

        # Check if salary_data table has data
        count = db.query(SalaryData).count()
        if count > 0:
            logger.info("Sample data already exists")
            db.close()
            return

        # Sample salary data
        sample_data = [
            SalaryData(
                job_title='Senior Software Engineer',
                normalized_title='senior_software_engineer',
                company='TechCorp',
                company_tier='Standard',
                location='San Francisco, CA',
                location_tier='tier1',
                base_salary=145000,
                bonus=20000,
                equity_value=30000,
                total_comp=195000,
                years_experience=6,
                tech_stack=['Python', 'JavaScript', 'React', 'AWS'],
                benefits={'health': 'Full', '401k': 'Match'},
                is_verified=True,
                confidence_score=0.9,
                submission_hash='sample1',
                submitted_date=datetime.utcnow() - timedelta(days=5)
            ),
            SalaryData(
                job_title='Software Engineer',
                normalized_title='software_engineer',
                company='StartupXYZ',
                company_tier='Startup',
                location='Austin, TX',
                location_tier='tier2',
                base_salary=95000,
                bonus=10000,
                equity_value=15000,
                total_comp=120000,
                years_experience=3,
                tech_stack=['JavaScript', 'Node.js', 'React', 'MongoDB'],
                benefits={'health': 'Full'},
                is_verified=True,
                confidence_score=0.8,
                submission_hash='sample2',
                submitted_date=datetime.utcnow() - timedelta(days=10)
            ),
            SalaryData(
                job_title='Senior Software Engineer',
                normalized_title='senior_software_engineer',
                company='Google',
                company_tier='FAANG',
                location='Seattle, WA',
                location_tier='tier1',
                base_salary=165000,
                bonus=30000,
                equity_value=55000,
                total_comp=250000,
                years_experience=8,
                tech_stack=['Java', 'Python', 'Kubernetes', 'GCP'],
                benefits={'health': 'Premium', '401k': 'Full Match', 'meals': 'Provided'},
                is_verified=True,
                confidence_score=0.95,
                submission_hash='sample3',
                submitted_date=datetime.utcnow() - timedelta(days=2)
            ),
            SalaryData(
                job_title='Product Manager',
                normalized_title='product_manager',
                company='Microsoft',
                company_tier='FAANG',
                location='Redmond, WA',
                location_tier='tier1',
                base_salary=140000,
                bonus=25000,
                equity_value=40000,
                total_comp=205000,
                years_experience=5,
                tech_stack=['SQL', 'Tableau', 'JIRA'],
                benefits={'health': 'Premium', '401k': 'Match'},
                is_verified=True,
                confidence_score=0.9,
                submission_hash='sample4',
                submitted_date=datetime.utcnow() - timedelta(days=15)
            ),
            SalaryData(
                job_title='Senior Data Scientist',
                normalized_title='senior_data_scientist',
                company='Amazon',
                company_tier='FAANG',
                location='New York, NY',
                location_tier='tier1',
                base_salary=155000,
                bonus=28000,
                equity_value=47000,
                total_comp=230000,
                years_experience=7,
                tech_stack=['Python', 'R', 'TensorFlow', 'PyTorch', 'AWS'],
                benefits={'health': 'Premium', '401k': 'Full Match'},
                is_verified=True,
                confidence_score=0.9,
                submission_hash='sample5',
                submitted_date=datetime.utcnow() - timedelta(days=8)
            )
        ]

        # Add sample data
        db.add_all(sample_data)
        db.commit()

        logger.info(f"✅ Added {len(sample_data)} sample salary records")

    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()