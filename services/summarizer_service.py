from groq import Groq
from typing import List, Dict
from config.settings import settings

class SummarizerService:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
    
    def summarize_transactions(self, query: str, transactions: List[Dict]) -> str:
        """Summarize transactions using Groq LLM"""
        if not transactions:
            return "No transactions found for your query."
        
        # Prepare transaction data for the prompt
        transaction_text = "\n".join([
            f"- {txn['date']}: {txn['description']} - ₹{txn['amount']} ({txn['type']}) [{txn['category']}]"
            for txn in transactions[:10]  # Limit to top 10 for context
        ])
        
        # Create prompt
        prompt = f"""You are a financial assistant. Based on the user's query and the transactions below, provide a helpful, concise summary.

User Query: {query}

Transactions:
{transaction_text}

Please provide:
1. A brief answer to the user's question
2. Key insights about spending patterns
3. Total amounts if relevant

Keep the response conversational and helpful."""

        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial assistant that provides clear, concise summaries of financial transactions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def get_spending_insights(self, transactions: List[Dict]) -> str:
        """Get spending insights from transactions"""
        if not transactions:
            return "No transactions available for insights."
        
        # Calculate statistics
        total_debit = sum(txn['amount'] for txn in transactions if txn['type'] == 'Debit')
        total_credit = sum(txn['amount'] for txn in transactions if txn['type'] == 'Credit')
        
        category_spending = {}
        for txn in transactions:
            if txn['type'] == 'Debit':
                category = txn['category']
                category_spending[category] = category_spending.get(category, 0) + txn['amount']
        
        # Create prompt for insights
        prompt = f"""Analyze these financial statistics and provide 3-4 key insights:

Total Spent: ₹{total_debit:,.2f}
Total Received: ₹{total_credit:,.2f}
Net: ₹{total_credit - total_debit:,.2f}

Spending by Category:
{chr(10).join([f'- {cat}: ₹{amt:,.2f}' for cat, amt in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)])}

Provide brief, actionable insights about spending patterns."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor providing spending insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=300
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error generating insights: {str(e)}"


if __name__ == "__main__":
    service = SummarizerService()
    print("Summarizer service initialized successfully")