from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class PolicyDecision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RiskAssessmentRequest(BaseModel):
    companyName: str = Field(description="Name of the company")
    companyName: str = Field(description="Name of the company")
    industry: Optional[str] = Field(None, description="Primary industry or sector")
    businessType: Optional[str] = Field(None, description="Type of business entity")
    location: Optional[str] = Field(None, description="Primary business location")
    yearsInOperation: Optional[int] = Field(None, ge=0, description="Number of years in operation")
    employeeCount: Optional[int] = Field(None, ge=0, description="Number of employees")
    
    # Financial Information
    annualRevenue: Optional[float] = Field(None, ge=0, description="Annual revenue")
    totalAssets: Optional[float] = Field(None, ge=0, description="Total assets value")
    totalDebt: Optional[float] = Field(None, ge=0, description="Total debt obligations")
    creditRating: Optional[str] = Field(None, description="Credit rating or financial score")
    profitMargin: Optional[float] = Field(None, description="Profit margin percentage")
    
    # Risk Indicators
    cashFlow: Optional[str] = Field(None, description="Cash flow status (positive/negative/stable)")
    marketVolatility: Optional[str] = Field(None, description="Market volatility level (low/medium/high)")
    competitionLevel: Optional[str] = Field(None, description="Competition level in market")
    regulatoryRisk: Optional[str] = Field(None, description="Regulatory risk level")
    
    # Operational Information
    keyDependencies: Optional[List[str]] = Field(None, description="Key business dependencies or suppliers")
    businessModel: Optional[str] = Field(None, description="Business model description")
    additionalInfo: Optional[Dict[str, Any]] = Field(None, description="Additional risk-relevant information")


class RiskAssessmentResponse(BaseModel):
    overallRiskLevel: str = Field(
        description="Overall risk level (Low, Medium, High, Critical)"
    )
    riskScore: str = Field(
        description="Numerical risk score with methodology explanation"
    )
    financialRisk: str = Field(
        description="Financial stability and cash flow risk assessment"
    )
    operationalRisk: str = Field(
        description="Operational and business model risk evaluation"
    )
    marketRisk: str = Field(
        description="Market conditions and competitive risk analysis"
    )
    identifiedRisks: str = Field(
        description="Specific risk factors identified in the assessment"
    )
    strengthsAndMitigants: str = Field(
        description="Business strengths and risk-mitigating factors"
    )
    riskManagementRecommendations: str = Field(
        description="Recommendations for managing and reducing risks"
    )
    monitoringRequirements: str = Field(
        description="Key metrics and areas requiring ongoing monitoring"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "overallRiskLevel": "Medium",
                "riskScore": "65/100 - Moderate risk profile with manageable concerns",
                "financialRisk": "Moderate - Stable revenue but high debt-to-equity ratio requires monitoring",
                "operationalRisk": "Low - Well-established operations with experienced management team",
                "marketRisk": "Medium - Competitive market with some volatility in demand cycles",
                "identifiedRisks": "Market concentration, supplier dependency, seasonal revenue patterns",
                "strengthsAndMitigants": "Strong brand recognition, diversified product portfolio, solid customer relationships",
                "riskManagementRecommendations": "Diversify supplier base, develop counter-cyclical revenue streams, improve debt management",
                "monitoringRequirements": "Monthly cash flow analysis, quarterly market share assessment, supplier relationship monitoring"
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Invalid input data provided"
            }
        }