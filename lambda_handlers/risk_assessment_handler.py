import json
import logging
import os
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    try:
        logger.info(f"Lambda function started. Remaining time: {context.get_remaining_time_in_millis() if context else 'unknown'}ms")
        
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        if event.get("path") == "/risk-assessment/health":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "status": "healthy",
                    "service": "Risk Assessment",
                    "timestamp": time.time(),
                    "version": "1.0.0"
                })
            }

        # Parse request body
        try:
            if isinstance(event.get("body"), str):
                body = json.loads(event["body"])
            else:
                body = event.get("body", {})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "success": False,
                    "error": "Invalid JSON in request body"
                })
            }

        company = body.get("companyName", body.get("company", "Unknown"))
        logger.info(f"Processing risk assessment for: {company}")


        if context and context.get_remaining_time_in_millis() < 10000:
            logger.warning("Insufficient time remaining to process request")
            return {
                "statusCode": 408,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "success": False,
                    "error": "Request timeout - insufficient time to process"
                })
            }

        from app.risk_assessment.service import RiskAssessmentService
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            return {
                "statusCode": 500,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "success": False,
                    "error": "OpenAI API key not configured"
                })
            }

        # Initialize service
        logger.info("Initializing RiskAssessmentService...")
        client = RiskAssessmentService(api_key=api_key)
        logger.info("RiskAssessmentService initialized successfully")

        if context and context.get_remaining_time_in_millis() < 30000:
            logger.warning("Insufficient time remaining for OpenAI API call")
            return {
                "statusCode": 408,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "success": False,
                    "error": "Request timeout - insufficient time for AI processing"
                })
            }

        logger.info("Assessing risk...")
        assessment = client.assess_risk(body)
        logger.info("Risk assessment completed successfully")

        # Return successful response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "success": True,
                "data": {
                    "assessmentId": assessment.assessmentId,
                    "overallRiskLevel": assessment.overallRiskLevel,
                    "riskScore": assessment.riskScore,
                    "financialRisk": assessment.financialRisk,
                    "operationalRisk": assessment.operationalRisk,
                    "marketRisk": assessment.marketRisk,
                    "complianceRisk": assessment.complianceRisk,
                    "riskFactors": assessment.riskFactors,
                    "mitigationStrategies": assessment.mitigationStrategies,
                    "riskSummary": assessment.riskSummary
                }
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            })
        }