from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Salary Data Models
class SalaryDataBase(BaseModel):
    job_title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: str = Field(..., description="Work location")
    base_salary: int = Field(..., ge=20000, le=1000000, description="Annual base salary")
    bonus: Optional[int] = Field(0, description="Annual bonus")
    equity_value: Optional[int] = Field(0, description="Annual equity value")
    years_experience: int = Field(..., ge=0, le=50, description="Years of experience")
    tech_stack: Optional[List[str]] = Field(default_factory=list, description="Technologies used")

class SalaryDataCreate(SalaryDataBase):
    pass

class SalaryDataResponse(SalaryDataBase):
    id: int
    normalized_title: str
    company_tier: Optional[str]
    location_tier: Optional[str]
    total_comp: int
    benefits: Optional[Dict[str, Any]]
    is_verified: bool
    confidence_score: Optional[float]
    submitted_date: datetime

    class Config:
        from_attributes = True

# Offer Analysis Models
class OfferData(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    base_salary: Optional[int] = None
    bonus: Optional[int] = None
    equity: Optional[str] = None
    equity_value: Optional[int] = None
    start_date: Optional[str] = None
    benefits: Optional[List[str]] = None
    years_experience: Optional[int] = None
    tech_stack: Optional[List[str]] = None
    current_salary: Optional[int] = None
    has_competing_offers: Optional[bool] = False

class MarketData(BaseModel):
    p10: Optional[int]
    p25: Optional[int]
    p50: Optional[int]
    p75: Optional[int]
    p90: Optional[int]
    sample_size: int
    avg_base: Optional[int]
    avg_bonus: Optional[int]
    avg_equity: Optional[int]
    confidence: str
    data_freshness: str

class NegotiationRoom(BaseModel):
    conservative: int
    realistic: int
    aggressive: int
    percentage_increase: Dict[str, float]

class LeveragePoint(BaseModel):
    type: str
    description: str
    strength: str

class Recommendation(BaseModel):
    priority: str
    action: str
    description: str
    target: Optional[int] = None

class AnalysisResult(BaseModel):
    offer_data: OfferData
    market_data: MarketData
    total_compensation: int
    verdict: str
    analysis: str
    negotiation_room: NegotiationRoom
    leverage_points: List[LeveragePoint]
    recommendations: List[Recommendation]

class NegotiationScript(BaseModel):
    assertive: str
    balanced: str
    humble: str
    tips: List[Dict[str, str]]
    talking_points: List[str]

class OfferAnalysisCreate(BaseModel):
    offer_data: OfferData
    analysis_result: AnalysisResult
    scripts: NegotiationScript

class OfferAnalysisResponse(BaseModel):
    id: int
    user_id: Optional[str]
    session_id: Optional[str]
    offer_data: OfferData
    analysis_result: AnalysisResult
    market_data: Optional[MarketData]
    generated_scripts: Optional[NegotiationScript]
    created_at: datetime

    class Config:
        from_attributes = True

# Response Models
class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

class HealthResponse(BaseModel):
    status: str
    database: Optional[str] = None
    gemini_api: Optional[str] = None
    error: Optional[str] = None