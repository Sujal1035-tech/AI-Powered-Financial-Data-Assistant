from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from services.vector_search_service import VectorSearchService
from services.summarizer_service import SummarizerService

router = APIRouter()

# Initialize services
vector_service = VectorSearchService()
summarizer_service = SummarizerService()

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    top_k: Optional[int] = 10
    summarize: Optional[bool] = False

class SearchResponse(BaseModel):
    query: str
    transactions: List[Dict]
    count: int
    summary: Optional[str] = None

@router.post("/search", response_model=SearchResponse)
async def search_transactions(request: SearchRequest):
    """Search transactions using semantic similarity"""
    try:
        # Perform vector search
        transactions = vector_service.search(
            query=request.query,
            n_results=request.top_k,
            user_id=request.user_id
        )
        
        summary = None
        if request.summarize and transactions:
            summary = summarizer_service.summarize_transactions(
                query=request.query,
                transactions=transactions
            )
        
        return SearchResponse(
            query=request.query,
            transactions=transactions,
            count=len(transactions),
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions")
async def get_transactions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: Optional[int] = Query(100, description="Maximum number of transactions")
):
    """Get all transactions"""
    try:
        transactions = vector_service.get_all_transactions(user_id=user_id)
        return {
            "transactions": transactions[:limit],
            "count": len(transactions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights(user_id: Optional[str] = Query(None)):
    """Get spending insights"""
    try:
        transactions = vector_service.get_all_transactions(user_id=user_id)
        insights = summarizer_service.get_spending_insights(transactions)
        
        return {
            "insights": insights,
            "transaction_count": len(transactions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))