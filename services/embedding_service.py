from sentence_transformers import SentenceTransformer
from typing import List, Dict
import json
from config.settings import settings

class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("✅ Embedding model loaded successfully")
    
    def create_transaction_text(self, transaction: Dict) -> str:
        """Convert transaction to text representation for embedding"""
        return (
            f"{transaction['type']} of ₹{transaction['amount']} "
            f"on {transaction['date']} for {transaction['description']} "
            f"under {transaction['category']} category"
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def load_and_prepare_transactions(self, file_path: str) -> tuple:
        """Load transactions and prepare text representations"""
        with open(file_path, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
        
        texts = [self.create_transaction_text(txn) for txn in transactions]
        
        return transactions, texts


if __name__ == "__main__":
    service = EmbeddingService()
    transactions, texts = service.load_and_prepare_transactions(settings.DATA_PATH)
    print(f"Loaded {len(transactions)} transactions")
    print(f"Sample text: {texts[0]}")