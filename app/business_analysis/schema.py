from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BusinessAnalysisRequest(BaseModel):
    companyName: str = Field(description="Name of the company")
    companyName: str = Field(description="Name of the company")
    industry: Optional[str] = Field(None, description="Primary industry or sector")
    businessType: Optional[str] = Field(None, description="Type of business (LLC, Corporation, Partnership, etc.)")
    location: Optional[str] = Field(None, description="Business location (city, state, country)")
    yearsInOperation: Optional[int] = Field(None, ge=0, description="Number of years in operation")
    employeeCount: Optional[int] = Field(None, ge=0, description="Number of employees")
    
    # Financial Information
    annualRevenue: Optional[float] = Field(None, ge=0, description="Annual revenue")
    totalAssets: Optional[float] = Field(None, ge=0, description="Total assets value")
    creditRating: Optional[str] = Field(None, description="Credit rating or financial score")
    
    # Market Information
    primaryMarkets: Optional[List[str]] = Field(None, description="Primary markets served")
    competitiveAdvantages: Optional[List[str]] = Field(None, description="Key competitive advantages")
    businessModel: Optional[str] = Field(None, description="Business model description")
    
    # Additional Context
    keyProducts: Optional[List[str]] = Field(None, description="Key products or services")
    recentDevelopments: Optional[str] = Field(None, description="Recent business developments or news")
    additionalInfo: Optional[Dict[str, Any]] = Field(None, description="Additional business information")


class BusinessAnalysisResponse(BaseModel):
    analysisId: str = Field(
        description="Unique identifier for this business analysis"
    )
    industryClassification: str = Field(
        description="Primary industry classification and category"
    )
    marketPosition: str = Field(
        description="Current market positioning and competitive standing"
    )
    growthPotential: str = Field(
        description="Growth opportunities and expansion potential"
    )
    strengthsAndAdvantages: str = Field(
        description="Key business strengths and competitive advantages"
    )
    marketOpportunities: str = Field(
        description="Identified market opportunities and trends"
    )
    strategicRecommendations: str = Field(
        description="Strategic recommendations for business development"
    )
    businessOverview: str = Field(
        description="Comprehensive business analysis summary"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysisId": "TECHCORP_BA_1732800000",
                "industryClassification": "Technology Services - Enterprise Software Solutions",
                "marketPosition": "Mid-tier player in regional technology market with strong customer retention",
                "growthPotential": "High growth potential through cloud migration services and AI integration",
                "strengthsAndAdvantages": "Strong technical expertise, established client relationships, innovative solutions",
                "marketOpportunities": "Digital transformation demand, SMB market expansion, partnership opportunities",
                "strategicRecommendations": "Focus on cloud services, expand sales team, develop AI capabilities",
                "businessOverview": "Well-positioned technology company with solid fundamentals and clear growth trajectory in expanding digital markets."
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid input data",
                "detail": "Credit score must be between 300 and 850"
            }
        }