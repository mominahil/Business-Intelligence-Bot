import os
from typing import Optional, Dict, Any
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class BusinessAnalysis:
    def __init__(self, industryClassification: str, marketPosition: str, growthPotential: str,
                 strengthsAndAdvantages: str, marketOpportunities: str, strategicRecommendations: str,
                 businessOverview: str, analysisId: str):
        self.industryClassification = industryClassification
        self.marketPosition = marketPosition
        self.growthPotential = growthPotential
        self.strengthsAndAdvantages = strengthsAndAdvantages
        self.marketOpportunities = marketOpportunities
        self.strategicRecommendations = strategicRecommendations
        self.businessOverview = businessOverview
        self.analysisId = analysisId


class BusinessData:
    def __init__(self, **kwargs):
        self.company_name = kwargs.get('companyName', kwargs.get('company', ''))
        self.industry = kwargs.get('industry', '')
        self.business_type = kwargs.get('businessType', kwargs.get('businessStructure', ''))
        self.location = kwargs.get('location', f"{kwargs.get('businessCity', '')}, {kwargs.get('businessState', '')}")
        self.years_in_operation = kwargs.get('yearsInOperation', kwargs.get('yearsInBusiness', 0))
        self.employee_count = kwargs.get('employeeCount', 0)
        
        self.annual_revenue = kwargs.get('annualRevenue', 0)
        self.total_assets = kwargs.get('totalAssets', kwargs.get('totalEquipmentCost', 0))
        self.credit_rating = kwargs.get('creditRating', '')
        
        self.owner_full_name = kwargs.get('ownerFullName', '')
        self.company_ownership_percent = kwargs.get('companyOwnershipPercent', 0)
        self.ssn = kwargs.get('ssn', '')
        self.home_street_addr = kwargs.get('homeStreetAddr', '')
        self.home_city = kwargs.get('homeCity', '')
        self.home_state = kwargs.get('homeState', '')
        self.home_zip = kwargs.get('homeZip', '')
        self.home_phone = kwargs.get('homePhone', '')
        self.pg_email = kwargs.get('pgEmail', '')
        
        self.primary_markets = kwargs.get('primaryMarkets', [])
        self.competitive_advantages = kwargs.get('competitiveAdvantages', [])
        self.business_model = kwargs.get('businessModel', '')
        
        self.key_products = kwargs.get('keyProducts', kwargs.get('leadEquipments', []))
        self.recent_developments = kwargs.get('recentDevelopments', '')
        self.additional_info = kwargs.get('additionalInfo', {})
        
        self.legacy_fields = {
            'experianScore': kwargs.get('experianScore', ''),
            'paynetScore': kwargs.get('paynetScore', ''),
            'isVendor': kwargs.get('isVendor', False),
            'documents': kwargs.get('documents', [])
        }


class BusinessAnalysisService:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o-2024-08-06"
        logger.info(f"BusinessAnalysisService initialized with model: {self.model}")
    
    def _generate_analysis_id(self, business_data: Dict[str, Any]) -> str:
        import time
        
        company_name = business_data.get('companyName', business_data.get('company', 'UNKNOWN_COMPANY'))
        timestamp = str(int(time.time()))

        clean_company = ''.join(c for c in company_name if c.isalnum() or c in [' ', '-', '_'])
        clean_company = clean_company.replace(' ', '_').upper()

        analysis_id = f"{clean_company}_BA_{timestamp}"
        
        if len(analysis_id) > 60:
            analysis_id = f"{clean_company[:30]}_BA_{timestamp}"
        
        logger.info(f"Generated Business Analysis ID: {analysis_id}")
        return analysis_id
        
    def generate_analysis(self, business_data: Dict[str, Any]) -> BusinessAnalysis:
        logger.info("Generating business analysis...")
        
        analysis_id = self._generate_analysis_id(business_data)
        
        structured_data = BusinessData(**business_data)
        
        logger.info(f"Processing data - Company: {structured_data.company_name}, Years in Operation: {structured_data.years_in_operation}, Location: {structured_data.location}")

        prompt = self._create_analysis_prompt(structured_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_business_analysis_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                    {
                        "role": "assistant",
                        "content": "I'll analyze the provided business data and create a comprehensive business intelligence analysis. Let me review the company details, market position, and business information to generate strategic insights."
                    },
                    {
                        "role": "user", 
                        "content": "Generate the analysis now using the exact format: INDUSTRY_CATEGORY: [category] INDUSTRY_ALTERNATIVES: [alternatives] MARKET_EXPOSURE: [exposure] BUSINESS_SUMMARY: [sentences]"
                    }
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            logger.info(f"Business analysis response received: {len(content)} characters")
            
            return self._parse_analysis_response(content, business_data, analysis_id)
            
        except Exception as e:
            logger.error(f"Error generating business analysis: {e}")
            raise Exception(f"Business analysis generation failed: {e}")
    
    def _get_business_analysis_system_prompt(self) -> str:
        return """You are an expert Business Intelligence Analyst specializing in comprehensive business analysis and market positioning. You must analyze the provided company data and create strategic business insights.

        IMPORTANT: You must ONLY use the data provided in the user message. Do not ask for additional information or indicate missing data.

        Your task is to analyze the business and provide ONLY the following 4 specific assessments using the information given to you.

        RESPONSE FORMAT (follow exactly):
        INDUSTRY_CLASSIFICATION: [Primary industry classification and business category]
        MARKET_POSITION: [Current market positioning and competitive standing]
        GROWTH_POTENTIAL: [Growth opportunities and expansion potential assessment]
        STRENGTHS_ADVANTAGES: [Key business strengths and competitive advantages]
        MARKET_OPPORTUNITIES: [Identified market opportunities and trends]
        STRATEGIC_RECOMMENDATIONS: [Strategic recommendations for business development]
        BUSINESS_OVERVIEW: [Comprehensive strategic business analysis summary]

        RULES:
        1. MUST use the actual company name provided
        2. Focus on business intelligence and strategic analysis
        3. Include market positioning and competitive analysis
        4. Assess growth potential and business model sustainability
        5. Include operational maturity based on years in business
        6. Analyze geographic market presence
        7. Never ask for more information - work with what you have
        8. Be specific and use actual details from the data
        9. Focus on strategic business classification and market analysis
        10. Provide comprehensive market exposure assessment
        11. Think like a management consultant providing strategic insights

        EXAMPLES:
        - INDUSTRY_CATEGORY: Transportation & Logistics - Long-haul trucking services
        - INDUSTRY_ALTERNATIVES: Fleet management, Supply chain services, Last-mile delivery
        - MARKET_EXPOSURE: Regional transportation market with established routes, competitive pricing pressure, growth opportunities in e-commerce logistics

        Write professional, strategic assessments using the exact details provided to you."""

    def _create_analysis_prompt(self, data: BusinessData) -> str:
        """
        Create a detailed prompt from the structured business data.
        """
        prompt_parts = ["ANALYZE THIS BUSINESS FOR COMPREHENSIVE STRATEGIC INTELLIGENCE:\n"]
        prompt_parts.append("=== COMPANY OVERVIEW ===")
        if data.company_name:
            prompt_parts.append(f"Company Name: {data.company_name}")
        if data.industry:
            prompt_parts.append(f"Industry: {data.industry}")
        if data.business_type:
            prompt_parts.append(f"Business Type: {data.business_type}")
        if data.location.strip():
            prompt_parts.append(f"Location: {data.location}")
        if data.years_in_operation:
            prompt_parts.append(f"Years in Operation: {data.years_in_operation}")
        if data.employee_count:
            prompt_parts.append(f"Employee Count: {data.employee_count}")
        prompt_parts.append("")

        # Financial Information
        if data.annual_revenue or data.total_assets or data.credit_rating:
            prompt_parts.append("=== FINANCIAL PROFILE ===")
            if data.annual_revenue:
                prompt_parts.append(f"Annual Revenue: ${data.annual_revenue:,.2f}")
            if data.total_assets:
                prompt_parts.append(f"Total Assets: ${data.total_assets:,.2f}")
            if data.credit_rating:
                prompt_parts.append(f"Credit Rating: {data.credit_rating}")
            prompt_parts.append("")

        # Market Information
        if data.primary_markets or data.competitive_advantages or data.business_model:
            prompt_parts.append("=== MARKET INFORMATION ===")
            if data.primary_markets:
                prompt_parts.append(f"Primary Markets: {', '.join(data.primary_markets)}")
            if data.competitive_advantages:
                prompt_parts.append(f"Competitive Advantages: {', '.join(data.competitive_advantages)}")
            if data.business_model:
                prompt_parts.append(f"Business Model: {data.business_model}")
            prompt_parts.append("")
        
        # Products and Services
        if data.key_products or data.recent_developments:
            prompt_parts.append("=== PRODUCTS & SERVICES ===")
            if data.key_products:
                products_list = []
                for product in data.key_products:
                    if isinstance(product, dict):
                        products_list.append(product.get('description', str(product)))
                    else:
                        products_list.append(str(product))
                if products_list:
                    prompt_parts.append(f"Key Products/Services: {', '.join(products_list)}")
            if data.recent_developments:
                prompt_parts.append(f"Recent Developments: {data.recent_developments}")
            prompt_parts.append("")
        
        # Additional Information
        if data.additional_info or data.legacy_fields.get('documents'):
            prompt_parts.append("=== ADDITIONAL INFORMATION ===")
            if data.additional_info:
                for key, value in data.additional_info.items():
                    prompt_parts.append(f"{key}: {value}")
            prompt_parts.append("")
        
        prompt_parts.append("=== STRATEGIC ANALYSIS REQUIRED ===")
        prompt_parts.append("Provide a comprehensive business intelligence analysis covering:")
        prompt_parts.append("1. Industry classification and positioning")
        prompt_parts.append("2. Current market position and competitive landscape")
        prompt_parts.append("3. Growth potential and expansion opportunities")
        prompt_parts.append("4. Key business strengths and competitive advantages")
        prompt_parts.append("5. Market opportunities and emerging trends")
        prompt_parts.append("6. Strategic recommendations for business development")
        prompt_parts.append("7. Overall business assessment and outlook")
        prompt_parts.append("Use ONLY the information provided above.")
        
        return "\n".join(prompt_parts)
    
    def _parse_analysis_response(self, content: str, business_data: Dict[str, Any], analysis_id: str) -> BusinessAnalysis:
        """
        Parse the business analysis response into structured format.
        """
        try:
            logger.info(f"Parsing business analysis response: {content[:200]}...") 
            
            lines = content.strip().split('\n')
            industry_classification = ""
            market_position = ""
            growth_potential = ""
            strengths_advantages = ""
            market_opportunities = ""
            strategic_recommendations = ""
            business_overview = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("INDUSTRY_CLASSIFICATION:"):
                    industry_classification = line.replace("INDUSTRY_CLASSIFICATION:", "").strip()
                elif line.startswith("MARKET_POSITION:"):
                    market_position = line.replace("MARKET_POSITION:", "").strip()
                elif line.startswith("GROWTH_POTENTIAL:"):
                    growth_potential = line.replace("GROWTH_POTENTIAL:", "").strip()
                elif line.startswith("STRENGTHS_ADVANTAGES:"):
                    strengths_advantages = line.replace("STRENGTHS_ADVANTAGES:", "").strip()
                elif line.startswith("MARKET_OPPORTUNITIES:"):
                    market_opportunities = line.replace("MARKET_OPPORTUNITIES:", "").strip()
                elif line.startswith("STRATEGIC_RECOMMENDATIONS:"):
                    strategic_recommendations = line.replace("STRATEGIC_RECOMMENDATIONS:", "").strip()
                elif line.startswith("BUSINESS_OVERVIEW:"):
                    business_overview = line.replace("BUSINESS_OVERVIEW:", "").strip()
            
            business_overview = business_overview.strip()
            
            if not business_overview and len(content.strip()) > 50:
                paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 30]
                if paragraphs:
                    business_overview = paragraphs[0]
                    logger.info("Used fallback paragraph extraction for business overview")
            
            if not business_overview or len(business_overview) < 20:
                logger.warning("Analysis response too short, creating basic analysis from available data")
                company_name = business_data.get('companyName', business_data.get('company', 'Company'))
                years_operation = business_data.get('yearsInOperation', business_data.get('yearsInBusiness', 'Unknown'))
                location = business_data.get('location', '')
                industry = business_data.get('industry', '')
                
                business_overview = f"{company_name} is an established business"
                if industry:
                    business_overview += f" in the {industry} sector"
                if years_operation != 'Unknown':
                    business_overview += f" with {years_operation} years of operational experience"
                if location.strip():
                    business_overview += f" based in {location}"
                business_overview += "."
                
                if not industry_classification:
                    industry_classification = industry or "Business Services"
                if not market_position:
                    market_position = "Established market participant"
                if not growth_potential:
                    growth_potential = "Moderate growth opportunities identified"
                if not strengths_advantages:
                    strengths_advantages = "Operational experience and market presence"
                if not market_opportunities:
                    market_opportunities = "Market expansion and service diversification"
                if not strategic_recommendations:
                    strategic_recommendations = "Continue operational excellence and explore growth opportunities"
            
            return BusinessAnalysis(
                industryClassification=industry_classification,
                marketPosition=market_position,
                growthPotential=growth_potential,
                strengthsAndAdvantages=strengths_advantages,
                marketOpportunities=market_opportunities,
                strategicRecommendations=strategic_recommendations,
                businessOverview=business_overview,
                analysisId=analysis_id
            )
            
        except Exception as e:
            logger.error(f"Error parsing business analysis response: {e}")
            return BusinessAnalysis(
                industryClassification="Business Services",
                marketPosition="Market analysis pending",
                growthPotential="Growth assessment in progress",
                strengthsAndAdvantages="Competitive analysis pending",
                marketOpportunities="Opportunity identification in progress",
                strategicRecommendations="Strategic analysis pending",
                businessOverview="Business analysis completed with available data.",
                analysisId=analysis_id
            )
