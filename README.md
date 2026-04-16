# 🏦 AI-Powered Financial Data Assistant

An intelligent financial assistant that uses semantic search and AI to help users query and analyze their financial transactions using natural language.

## 🌟 Features

- **AI-Generated Dummy Data**: Generates realistic financial transactions using Faker
- **Vector Embeddings**: Uses Sentence Transformers for semantic understanding
- **Semantic Search**: Natural language queries to find relevant transactions
- **AI Summarization**: Groq LLM provides intelligent insights and summaries
- **Interactive Dashboard**: Beautiful Streamlit UI with charts and analytics
- **REST API**: FastAPI backend for programmatic access

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: Groq API (Llama 3)
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Data Generation**: Faker

## 📁 Project Structure
```
financial-data-assistant/
│
├── data/
│   └── transactions.json          # Generated financial transactions
│
├── embeddings/
│   └── chroma_db/                 # ChromaDB vector store
│
├── services/
│   ├── __init__.py
│   ├── data_generator.py          # Generate dummy transactions
│   ├── embedding_service.py       # Create embeddings
│   ├── vector_search_service.py   # ChromaDB operations
│   └── summarizer_service.py      # LLM summarization
│
├── api/
│   ├── __init__.py
│   ├── app.py                     # FastAPI application
│   └── routes/
│       ├── __init__.py
│       └── search.py              # Search endpoints
│
├── config/
│   ├── __init__.py
│   └── settings.py                # Configuration
│
├── streamlit_app.py               # Streamlit UI
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── .env.example                   # Environment template
└── .gitignore
```

## 🚀 Setup and Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd financial-data-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./embeddings/chroma_db
DATA_PATH=./data/transactions.json
```

**Get your free Groq API key**: [https://console.groq.com](https://console.groq.com)

### 5. Generate Dummy Data
```bash
python -m services.data_generator
```

This will create `data/transactions.json` with 450 transactions (3 users × 150 transactions).

### 6. Initialize Vector Database
```bash
python -m services.vector_search_service
```

This will create embeddings and store them in ChromaDB.

## 🎯 Usage

### Option : Streamlit UI (Recommended)
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `https://ai-powered-financial-data-assistant-fsgofezhq9mqbty3vmcv2t.streamlit.app`

#### Features:
- **Search Tab**: Natural language queries
- **Dashboard Tab**: Visual analytics and charts
- **All Transactions Tab**: Filtered transaction view
- **Insights Tab**: AI-powered financial insights

### 1. Search Transactions
```bash
POST /api/search
```

**Request Body:**
```json
{
  "query": "Show my top 5 expenses in September",
  "user_id": "user_1",
  "top_k": 10,
  "summarize": true
}
```

**Response:**
```json
{
  "query": "Show my top 5 expenses in September",
  "transactions": [...],
  "count": 10,
  "summary": "You spent ₹12,300 on food in September..."
}
```

### 2. Get All Transactions
```bash
GET /api/transactions?user_id=user_1&limit=100
```

### 3. Get Insights
```bash
GET /api/insights?user_id=user_1
```

## 🔍 Example Queries

Try these natural language queries:

- "Show all UPI transactions above ₹1000"
- "What's my biggest expense in August?"
- "How much did I spend on food last month?"
- "Show my top 5 expenses in September"
- "List all salary credits"
- "What did I spend on entertainment?"
- "Show transactions from Swiggy"
- "My total spending on shopping"

## 📊 Models & Configuration

### Embedding Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimension**: 384
- **Use Case**: Semantic similarity search

### LLM Model
- **Provider**: Groq
- **Model**: Llama 3 (8B)
- **Use Case**: Transaction summarization and insights

### Vector Database
- **Database**: ChromaDB
- **Storage**: Persistent (local)
- **Similarity**: Cosine similarity

## 🧪 Testing

### Using cURL
```bash
# Search transactions
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show food expenses above 500 rupees",
    "user_id": "user_1",
    "top_k": 5,
    "summarize": true
  }'
```

## 📈 Sample Output

**Query:** "What are my top 3 expenses last month?"

**Response:**
```
Transactions:
- Amazon Purchase – ₹2,500 – 2024-09-15 [Shopping]
- Swiggy – ₹1,300 – 2024-09-10 [Food]
- Big Basket – ₹1,150 – 2024-09-18 [Shopping]

💬 Summary: You spent the most on shopping and food, totaling ₹4,950 in September. 
Your biggest single expense was an Amazon purchase of ₹2,500.
```


