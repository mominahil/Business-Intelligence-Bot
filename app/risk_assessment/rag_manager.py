import os
import json
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, api_key=None):
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        main_env_path = os.path.join(project_root, '.env')
        if os.path.exists(main_env_path):
            load_dotenv(main_env_path)
            logger.info("✅ Loaded main .env file")
    
        openai_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=openai_key)

        self.assistant_id = os.getenv('RAG_ASSISTANT_ID')
        self.vector_store_id = os.getenv('RAG_VECTOR_STORE_ID')
        self.file_id = os.getenv('RAG_FILE_ID')
        
        logger.info(f"RAG Manager initialized with Assistant ID: {self.assistant_id}")
        logger.info(f"Vector Store ID: {self.vector_store_id}")
        logger.info(f"File ID: {self.file_id}")
        
    def create_vector_store(self, name):
        """Create a new vector store"""
        try:
            logger.info(f"Creating vector store: {name}")
            vector_store = self.client.vector_stores.create(
                name=name
            )
            logger.info(f"Vector store created with ID: {vector_store.id}")
            return vector_store.id
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise

    def upload_pdf(self, pdf_path, vector_store_id):
        """Upload PDF to vector store"""
        try:
            logger.info(f"Uploading PDF: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose='assistants'
                )
            
            # Add file to vector store
            self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=uploaded_file.id
            )
            
            logger.info(f"PDF uploaded successfully. File ID: {uploaded_file.id}")
            return uploaded_file.id
            
        except Exception as e:
            logger.error(f"Failed to upload PDF: {e}")
            raise

    def create_assistant(self, vector_store_id):
        """Create OpenAI Assistant"""
        try:
            logger.info("Creating OpenAI Assistant for deal evaluation")
            
            assistant = self.client.beta.assistants.create(
                name="Deal Evaluation Assistant",
                instructions="""You are a deal evaluation assistant that helps analyze loan applications against credit underwriting policies.
                
                When evaluating a deal, please provide a structured response with:
                1. Overall recommendation (APPROVE, DECLINE, or CONDITIONAL_APPROVAL)
                2. Key findings and analysis
                3. Risk factors identified
                4. Compliance with underwriting policies
                5. Confidence score (0.0 to 1.0)
                
                Base your analysis on the credit underwriting policies in your knowledge base.""",
                model="gpt-4o",
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store_id]
                    }
                }
            )
            
            logger.info(f"Assistant created with ID: {assistant.id}")
            return assistant.id
            
        except Exception as e:
            logger.error(f"Failed to create assistant: {e}")
            raise

    def query_assistant(self, query, max_retries=3):
        """Query the assistant with better error handling"""
        if not self.assistant_id:
            logger.error("Cannot query assistant: ASSISTANT_ID is None")
            return None
            
        try:
            logger.info(f"Querying assistant with: {query}")
            
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )
            logger.info("Added message to thread")
            
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            logger.info(f"Created run: {run.id}")
        
            timeout = 60
            start_time = time.time()
            
            while run.status in ['queued', 'in_progress']:
                if time.time() - start_time > timeout:
                    logger.error("Assistant run timed out")
                    return None
                    
                time.sleep(2)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                logger.info(f"Run status: {run.status}")
            
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                assistant_messages = [msg for msg in messages.data if msg.role == 'assistant']
                if assistant_messages:
                    response_content = assistant_messages[0].content[0].text.value
                    logger.info(f"Assistant response received: {len(response_content)} characters")
                    return response_content
                else:
                    logger.error("No assistant messages found")
                    return None
            else:
                logger.error(f"Run failed with status: {run.status}")
                if hasattr(run, 'last_error') and run.last_error:
                    logger.error(f"Error details: {run.last_error}")
                return None
                
        except Exception as e:
            logger.error(f"Error querying assistant: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_config(self, vector_store_id, assistant_id, file_id):
        """Save configuration to .env.rag file"""
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_path = os.path.join(project_root, '.env.rag')
        
        with open(config_path, 'w') as f:
            f.write(f"VECTOR_STORE_ID={vector_store_id}\n")
            f.write(f"ASSISTANT_ID={assistant_id}\n")
            f.write(f"FILE_ID={file_id}\n")
        
        logger.info(f"Configuration saved to: {config_path}")