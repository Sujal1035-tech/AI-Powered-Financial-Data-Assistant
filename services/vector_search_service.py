import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import json
from services.embedding_service import EmbeddingService
from config.settings import settings
import os

class VectorSearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        # Initialize ChromaDB
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        self.collection_name = "financial_transactions"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ Loaded existing collection: {self.collection_name}")
        except:
            self.collection = None
            print(f"⚠️ Collection not found. Please initialize the database first.")
    
    def initialize_database(self, transactions_file: str):
        """Initialize ChromaDB with transactions"""
        print("🔄 Initializing vector database...")
        
        # Delete existing collection if exists
        try:
            self.client.delete_collection(name=self.collection_name)
            print("Deleted existing collection")
        except:
            pass
        
        # Create new collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Financial transaction embeddings"}
        )
        
        # Load transactions
        transactions, texts = self.embedding_service.load_and_prepare_transactions(transactions_file)
        
        # Generate embeddings
        print(f"Generating embeddings for {len(transactions)} transactions...")
        embeddings = self.embedding_service.generate_embeddings_batch(texts)
        
        # Prepare data for ChromaDB
        ids = [txn['id'] for txn in transactions]
        documents = texts
        metadatas = transactions
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            self.collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            print(f"Added batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")
        
        print(f"✅ Database initialized with {len(transactions)} transactions")
    
    def search(self, query: str, n_results: int = 10, user_id: Optional[str] = None) -> List[Dict]:
        """Search for relevant transactions"""
        if not self.collection:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Build where filter for user
        where_filter = {"userId": user_id} if user_id else None
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        transactions = []
        if results and results['metadatas']:
            for metadata in results['metadatas'][0]:
                transactions.append(metadata)
        
        return transactions
    
    def get_all_transactions(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get all transactions for a user"""
        if not self.collection:
            return []
        
        where_filter = {"userId": user_id} if user_id else None
        
        results = self.collection.get(
            where=where_filter,
            limit=10000
        )
        
        return results['metadatas'] if results else []


if __name__ == "__main__":
    service = VectorSearchService()
    service.initialize_database(settings.DATA_PATH)