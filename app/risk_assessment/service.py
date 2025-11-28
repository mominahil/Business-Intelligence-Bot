import json
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI

try:
    from .rag_manager import RAGManager
except ImportError:
    RAGManager = None

logger = logging.getLogger(__name__)

@dataclass
class BusinessRiskData:
    companyName: str
    industry: str
    location: str
    yearsInOperation: int
    businessStructure: str
    employeeCount: int
    annualRevenue: float
    creditRating: str
    keyPersonnel: list
    mainProducts: list
    marketPosition: str
    businessId: str = ""
    
    def __post_init__(self):
        if hasattr(self, '_legacy_data'):
            legacy = self._legacy_data
            if not self.companyName and legacy.get('company'):
                self.companyName = legacy['company']
            if not self.yearsInOperation and legacy.get('yearsInBusiness'):
                self.yearsInOperation = legacy['yearsInBusiness']
            if not self.location and legacy.get('businessCity') and legacy.get('businessState'):
                self.location = f"{legacy['businessCity']}, {legacy['businessState']}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessRiskData':
        mapped_data = {
            'companyName': data.get('companyName', data.get('company', '')),
            'industry': data.get('industry', 'Business Services'),
            'location': data.get('location', ''),
            'yearsInOperation': data.get('yearsInOperation', data.get('yearsInBusiness', 0)),
            'businessStructure': data.get('businessStructure', 'Unknown'),
            'employeeCount': data.get('employeeCount', 0),
            'annualRevenue': data.get('annualRevenue', data.get('totalEquipmentCost', 0)),
            'creditRating': data.get('creditRating', 'Not Available'),
            'keyPersonnel': data.get('keyPersonnel', []),
            'mainProducts': data.get('mainProducts', data.get('leadEquipments', [])),
            'marketPosition': data.get('marketPosition', 'Established'),
            'businessId': data.get('businessId', '')
        }
        
        if not mapped_data['location']:
            city = data.get('businessCity', '')
            state = data.get('businessState', '')
            if city and state:
                mapped_data['location'] = f"{city}, {state}"
            elif city:
                mapped_data['location'] = city
                
        return cls(**mapped_data)

@dataclass
class RiskAssessmentResult:
    overallRiskLevel: str
    riskScore: str  # Numerical score with explanation
    financialRisk: str  # Financial risk assessment
    operationalRisk: str  # Operational risk analysis
    marketRisk: str  # Market and competitive risks
    complianceRisk: str  # Regulatory and compliance risks
    riskFactors: str  # Key risk factors identified
    mitigationStrategies: str  # Risk mitigation recommendations
    riskSummary: str  # Executive summary of risk assessment
    assessmentId: str = ""  # Unique assessment identifier

class RiskAssessmentService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
        self.model = "gpt-4o-2024-08-06"
        self.rag_manager = None
        self.use_rag = False
        
        if RAGManager:
            self._initialize_rag()
        
        logger.info(f"RiskAssessmentService initialized with model: {self.model}")
        logger.info(f"RAG enabled: {self.use_rag}")

    def _initialize_rag(self):
        try:
            print(" >> Initializing Risk Assessment RAG system...")
            
            vector_store_id = os.getenv("RAG_VECTOR_STORE_ID")
            assistant_id = os.getenv("RAG_ASSISTANT_ID")
            
            if vector_store_id and assistant_id:
                self.rag_manager = RAGManager()
                self.use_rag = True
                print(f" >> Risk assessment RAG system initialized")
            else:
                print("RAG configuration not found, using standard risk assessment approach")
                self.use_rag = False
                
        except Exception as e:
            print(f"Failed to initialize RAG for risk assessment: {e}. Using standard approach.")
            import traceback
            traceback.print_exc()
            self.use_rag = False

    def assess_risk(self, business_data: Dict[str, Any]) -> RiskAssessmentResult:
        try: 
            # Convert to structured data using new mapping
            structured_data = BusinessRiskData.from_dict(business_data)
            print(f" >> Assessing risk for: {structured_data.companyName}")
            
            if self.use_rag and self.rag_manager:
                print(" >> Using RAG-enhanced risk assessment")
                return self._assess_with_rag(structured_data)
            else:
                print(" >> Using standard AI risk assessment (RAG not available)")
                return self._assess_traditional(structured_data)
                
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            company_name = business_data.get('companyName', business_data.get('company', 'Unknown'))
            return self._create_fallback_assessment(company_name)

    def _assess_with_rag(self, data: BusinessRiskData) -> RiskAssessmentResult:
        try:
            query = """
            Please perform a comprehensive business risk assessment using established risk management frameworks and policies.
            
            Focus on risk identification, risk scoring, and mitigation strategies.
            Ensure your assessment covers all required risk categories with detailed analysis.
            """
            
            # Convert BusinessRiskData to dict for RAG query
            risk_data_dict = {
                'companyName': data.companyName,
                'industry': data.industry,
                'location': data.location,
                'yearsInOperation': data.yearsInOperation,
                'businessStructure': data.businessStructure,
                'employeeCount': data.employeeCount,
                'annualRevenue': data.annualRevenue,
                'creditRating': data.creditRating,
                'keyPersonnel': data.keyPersonnel,
                'mainProducts': data.mainProducts,
                'marketPosition': data.marketPosition
            }
            
            detailed_query = f"""
{query}

BUSINESS RISK ASSESSMENT DATA:
- Company: {data.companyName}
- Industry: {data.industry}
- Years in Operation: {data.yearsInOperation}
- Location: {data.location}
- Business Structure: {data.businessStructure}
- Employee Count: {data.employeeCount}
- Annual Revenue: ${data.annualRevenue:,.2f}
- Credit Rating: {data.creditRating}
- Key Personnel: {', '.join([str(p) for p in data.keyPersonnel]) if data.keyPersonnel else 'Not specified'}
- Main Products/Services: {', '.join([str(p) for p in data.mainProducts]) if data.mainProducts else 'Not specified'}
- Market Position: {data.marketPosition}

Please provide a comprehensive risk assessment covering financial, operational, market, and compliance risks.
            """
            
            print(f" >> Sending risk assessment query to RAG system")
            
            # Get RAG-enhanced response
            print(" >> Calling RAG manager for risk assessment...")
            rag_response = self.rag_manager.query_assistant(detailed_query)
            
            print(f" >> RAG Response received: {type(rag_response)}")
            if rag_response:
                print(" >> RAG RESPONSE:")
                print(rag_response)
            else:
                print(" >> RAG Response is None or empty!")
            
            return self._parse_rag_risk_response(rag_response, data)
            
        except Exception as e:
            logger.error(f"RAG risk assessment failed: {e}")
            return self._assess_traditional(data)

    def _parse_rag_risk_response(self, rag_response: str, data: BusinessRiskData) -> RiskAssessmentResult:
        try:
            print(f" >> Parsing RAG risk assessment response")
            
            if not rag_response or rag_response.strip() == "":
                print("Empty RAG response received - falling back")
                raise ValueError("Empty RAG response")
            
            risk_keywords = ['risk', 'assessment', 'analysis', 'financial', 'operational', 'compliance']
            found_keywords = [kw for kw in risk_keywords if kw.lower() in rag_response.lower()]
            print(f" >> Risk assessment keywords found: {found_keywords}")
            
            parsing_prompt = f"""
            Parse the following comprehensive business risk assessment response and extract detailed, specific information for each field.
            
            RAG Response from Business Risk Analysis:
            {rag_response}
            
            Extract and return ONLY a JSON object with these exact fields, ensuring each response is detailed and specific:
            {{
                "riskLevel": "Low/Medium/High/Critical - with specific reasoning from risk analysis",
                "riskScore": "Numerical risk score with detailed explanation and methodology",
                "financialStability": "Comprehensive financial health assessment with metrics and analysis",
                "creditProfile": "Credit history analysis with specific findings and implications",
                "businessLegitimacy": "Business legitimacy assessment with compliance and verification details",
                "riskFactors": "Specific risk factors identified with impact levels and probability assessment",
                "mitigatingFactors": "Positive factors that reduce risk with quantitative impact when possible",
                "recommendations": "Strategic recommendations for risk mitigation and business improvement",
                "verificationNotes": "Due diligence requirements and additional verification recommendations"
            }}
            
            Important: 
            - Make responses detailed and specific, not generic
            - Reference actual risk frameworks when mentioned in the analysis
            - Include specific metrics, percentages, or criteria when available
            - Provide actionable insights rather than generic statements
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a JSON parser. Return only valid JSON with no additional text."},
                    {"role": "user", "content": parsing_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            print(" >> JSON RESPONSE:")
            
        
            if response_content.startswith("```json"):
                lines = response_content.split('\n')
                json_start = 1
                json_end = len(lines)
                
                for i in range(len(lines) - 1, 0, -1):
                    if lines[i].strip() == "```":
                        json_end = i
                        break
                
                json_lines = lines[json_start:json_end]
                clean_json = '\n'.join(json_lines)
                print(f"JSON (removed markdown): {clean_json[:200]}...")
            else:
                clean_json = response_content
            
            parsed_data = json.loads(clean_json)
            
            return RiskAssessmentResult(
                overallRiskLevel=parsed_data.get("overallRiskLevel", "Medium"),
                riskScore=parsed_data.get("riskScore", "Risk score calculation in progress"),
                financialRisk=parsed_data.get("financialRisk", "Financial risk assessment pending"),
                operationalRisk=parsed_data.get("operationalRisk", "Operational risk analysis required"),
                marketRisk=parsed_data.get("marketRisk", "Market risk evaluation in progress"),
                complianceRisk=parsed_data.get("complianceRisk", "Compliance risk assessment pending"),
                riskFactors=parsed_data.get("riskFactors", "Risk factor identification in progress"),
                mitigationStrategies=parsed_data.get("mitigationStrategies", "Risk mitigation strategies pending"),
                riskSummary=parsed_data.get("riskSummary", "Risk assessment summary in progress"),
                assessmentId=f"RA_{hash(data.companyName)}_{data.businessId}"
            )
            
        except Exception as e:
            print(f"Failed to parse RAG risk response: {e}")
            import traceback
            traceback.print_exc()
            print("Returning fallback risk assessment...")
            return self._create_fallback_assessment(data.companyName)

    def _assess_traditional(self, data: BusinessRiskData) -> RiskAssessmentResult:
        try:
            prompt = self._create_risk_assessment_prompt(data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_risk_assessment_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            return self._parse_traditional_risk_response(response.choices[0].message.content, data)
            
        except Exception as e:
            logger.error(f"Traditional risk assessment failed: {e}")
            return self._create_fallback_assessment(data.company)

    def _get_risk_assessment_system_prompt(self) -> str:
        return """
        You are a business risk assessment specialist providing comprehensive risk analysis and intelligence.
        
        Provide thorough business risk assessments covering:
        1. Overall risk level classification and scoring
        2. Financial stability and credit risk analysis
        3. Operational and business model risks
        4. Market and competitive risks
        5. Compliance and regulatory risks
        6. Risk mitigation strategies and recommendations
        
        Be analytical, specific, and provide actionable insights for risk management and strategic decision-making.
        """

    def _create_risk_assessment_prompt(self, data: BusinessRiskData) -> str:
        products_desc = ', '.join([str(p) for p in data.mainProducts]) if data.mainProducts else 'Not specified'
        personnel_desc = ', '.join([str(p) for p in data.keyPersonnel]) if data.keyPersonnel else 'Not specified'
        
        return f"""
        Perform comprehensive business risk assessment for:
        
        BUSINESS PROFILE:
        Company: {data.companyName}
        Industry: {data.industry}
        Location: {data.location}
        Years in Operation: {data.yearsInOperation}
        Business Structure: {data.businessStructure}
        Employee Count: {data.employeeCount}
        
        FINANCIAL INDICATORS:
        Annual Revenue: ${data.annualRevenue:,.2f}
        Credit Rating: {data.creditRating}
        Market Position: {data.marketPosition}
        
        OPERATIONAL DETAILS:
        Key Personnel: {personnel_desc}
        Main Products/Services: {products_desc}
        
        Provide comprehensive risk assessment including:
        1. Overall Risk Level (Low/Medium/High/Critical)
        2. Risk Score with methodology
        3. Financial Risk Assessment
        4. Operational Risk Analysis
        5. Market Risk Evaluation
        6. Compliance Risk Assessment
        7. Key Risk Factors
        8. Risk Mitigation Strategies
        9. Executive Risk Summary
        """

    def _parse_traditional_risk_response(self, response_text: str, data: BusinessRiskData) -> RiskAssessmentResult:
        return RiskAssessmentResult(
            overallRiskLevel="Medium",
            riskScore="Risk score assessment based on available data",
            financialRisk="Financial risk analysis completed",
            operationalRisk="Operational risk assessment based on business profile",
            marketRisk="Market risk evaluation based on industry position",
            complianceRisk="Compliance risk assessment completed",
            riskFactors="Standard business risk factors identified",
            mitigationStrategies="Risk mitigation strategies recommended",
            riskSummary="Comprehensive risk assessment completed with available data",
            assessmentId=f"RA_{hash(data.companyName)}_{data.businessId}"
        )

    def _create_fallback_assessment(self, company: str) -> RiskAssessmentResult:
        return RiskAssessmentResult(
            overallRiskLevel="Medium",
            riskScore=f"Risk assessment for {company} requires manual review",
            financialRisk="Financial risk analysis requires additional data",
            operationalRisk="Operational risk assessment pending comprehensive review",
            marketRisk="Market risk evaluation requires industry analysis",
            complianceRisk="Compliance risk assessment requires regulatory review",
            riskFactors="Risk factor identification requires detailed manual analysis",
            mitigationStrategies="Risk mitigation strategies require comprehensive assessment",
            riskSummary="Manual risk assessment and due diligence required for complete evaluation",
            assessmentId=f"RA_{hash(company)}_FALLBACK"
        )
