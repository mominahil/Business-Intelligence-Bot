# Business Intelligence Assistant

AI-powered business intelligence platform providing comprehensive business analysis and risk assessment services. Perfect for consulting firms, investment companies, and business analysts.

## What This Project Does

The Business Intelligence Assistant is a serverless AI platform that transforms raw business data into actionable strategic insights. Built with AWS Lambda and OpenAI's GPT-4o, it automates the complex process of business evaluation and risk analysis that traditionally requires teams of analysts.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│   API Gateway   │────│      Lambda      │────│  OpenAI GPT-4o    │
│                 │    │                  │    │                   │
│ /business-      │────│ business_        │────│ Business Analysis │
│  analysis       │    │ analysis         │    │                   │
│ /risk-          │────│ risk_            │────│ Risk Assessment   │
│  assessment     │    │ assessment       │    │                   │
└─────────────────┘    └──────────────────┘    └───────────────────┘
```

## Project Structure

```
business-intelligence-assistant/
├── lambda_handlers/                    # Lambda handler functions
│   ├── business_analysis_handler.py   # Business Analysis Lambda
│   └── risk_assessment_handler.py     # Risk Assessment Lambda
├── app/                               # Core application logic
│   ├── business_analysis/            # Business Analysis AI service
│   │   ├── service.py               # Core AI logic for business intelligence
│   │   ├── schema.py                # Pydantic request/response models
│   │   └── Sample_Business_Payload.json     # Sample data format
│   └── risk_assessment/              # Risk Assessment AI service
│       ├── service.py               # Core AI logic for risk analysis
│       ├── schema.py                # Pydantic request/response models
│       ├── rag_manager.py          # RAG system for enhanced analysis
│       ├── setup_rag.py            # RAG system setup utility
│       └── check_rag.py            # RAG system verification
├── template.yaml                     # AWS SAM template
├── requirements.txt                  # Python dependencies
└── README.md                        # This documentation
```


## Services

### Business Analysis
- **Industry Classification**: Automated industry category identification
- **Market Positioning**: Competitive landscape analysis  
- **Strategic Insights**: Business model and growth potential assessment
- **Market Exposure**: Risk and opportunity identification

### Risk Assessment
- **Risk Scoring**: Comprehensive risk level classification
- **Financial Stability**: Credit and financial health analysis
- **Operational Risk**: Business legitimacy and compliance assessment
- **Strategic Recommendations**: Risk mitigation and improvement strategies

## Features

- **AI-Powered Analysis**: Uses GPT-4o for intelligent business insights
- **RAG Enhanced**: Optional knowledge base integration for policy-based assessments
- **Scalable Architecture**: Serverless AWS Lambda deployment
- **REST API**: Easy integration with existing business systems
- **Health Monitoring**: Built-in health checks and monitoring

## Run code locally
```powershell
sam build
$env:OPENAI_API_KEY = "your-openai-api-key"
sam local start-api --port 3000
```

## API Endpoints

- `POST /business-analysis` - Generate comprehensive business intelligence analysis
- `POST /risk-assessment` - Perform detailed business risk assessment
- `GET /business-analysis/health` - Service health check
- `GET /risk-assessment/health` - Service health check
