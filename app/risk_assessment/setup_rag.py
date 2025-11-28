import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.risk_assessment.rag_manager import RAGManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_rag_system():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize RAG manager
        rag_manager = RAGManager()
        
        # Get the PDF file
        pdf_path = Path(__file__).parent / "Policies.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create vector store
        vector_store_id = rag_manager.create_vector_store("credit-policies-v1")
        
        # Upload PDF
        file_id = rag_manager.upload_pdf(str(pdf_path), vector_store_id)
        
        assistant_id = rag_manager.create_assistant(vector_store_id)
        
        env_file = Path(__file__).parent.parent.parent / ".env"
        
        existing_content = ""
        if env_file.exists():
            with open(env_file, "r") as f:
                lines = f.readlines()
                filtered_lines = [line for line in lines if not line.startswith(('RAG_VECTOR_STORE_ID=', 'RAG_ASSISTANT_ID=', 'RAG_FILE_ID='))]
                existing_content = "".join(filtered_lines)
        
        # Append RAG configuration
        with open(env_file, "w") as f:
            f.write(existing_content)
            if not existing_content.endswith('\n'):
                f.write('\n')
            f.write(f"RAG_VECTOR_STORE_ID={vector_store_id}\n")
            f.write(f"RAG_ASSISTANT_ID={assistant_id}\n")
            f.write(f"RAG_FILE_ID={file_id}\n")
        
        print(f"   RAG system setup completed!")
        print(f"   File ID: {file_id}")
        print(f"   Configuration saved to: {env_file}")
        
        return {
            "vector_store_id": vector_store_id,
            "assistant_id": assistant_id,
            "file_id": file_id
        }
        
    except Exception as e:
        logger.error(f"Failed to setup RAG system: {e}")
        raise

if __name__ == "__main__":
    setup_rag_system()