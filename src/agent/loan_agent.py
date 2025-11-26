import os
import logging
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langchain.agents import initialize_agent, AgentType
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from src.agent.tools import tools
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not found or import error: {e}. Using mock agent.")

class LoanAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
            self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
            self.agent = initialize_agent(
                tools,
                self.llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                handle_parsing_errors=True
            )
        else:
            self.agent = None

    def process_document(self, file_path):
        """
        Run the agent workflow on a document.
        """
        if not self.agent:
            # Mock response for demonstration/testing without API key or LangChain
            logger.info("Running in Mock Mode (No Agent/API Key)")
            import json
            return json.dumps({
                "extracted_data": {
                    "names": ["John Doe"], 
                    "pan": "ABCDE1234F", 
                    "salary": 50000
                },
                "validation_issues": [],
                "fraud_status": "Normal",
                "risk_score": 10,
                "eligibility": "Eligible",
                "summary": "Mock Agent Report: Document processed successfully."
            })

        prompt = f"""
        You are a Loan Document Intelligence Agent.
        Process the document at this path: {file_path}
        
        Steps:
        1. Read the document using OCR.
        2. Extract key data fields (Name, PAN, Salary, etc.).
        3. Validate the extracted data.
        4. Run a fraud check.
        5. Generate a final Risk Summary Report.
        
        The Final Answer should be a JSON string with keys: 
        - extracted_data: dict
        - validation_issues: list
        - fraud_status: string
        - risk_score: int (0-100, where 100 is high risk)
        - eligibility: string (Eligible/Rejected)
        - summary: string
        """
        
        try:
            response = self.agent.run(prompt)
            return response
        except Exception as e:
            logger.error(f"Agent failed: {str(e)}")
            return str(e)

if __name__ == "__main__":
    # Mock run if API key is present
    if os.getenv("OPENAI_API_KEY"):
        agent = LoanAgent()
        print(agent.process_document("data/salary_slip_john.pdf"))
