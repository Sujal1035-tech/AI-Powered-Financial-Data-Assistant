import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = "llama-3.1-8b-instant"  # Groq model
    
    # Paths
    DATA_PATH = os.getenv("DATA_PATH", "./data/transactions.json")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./embeddings/chroma_db")
    
    # Data Generation Settings
    NUM_USERS = 3
    TRANSACTIONS_PER_USER = 150
    
    # Categories
    CATEGORIES = [
        "Food", "Shopping", "Rent", "Salary", 
        "Utilities", "Entertainment", "Travel", "Others"
    ]
    
    # Search Settings
    TOP_K_RESULTS = 10

settings = Settings()