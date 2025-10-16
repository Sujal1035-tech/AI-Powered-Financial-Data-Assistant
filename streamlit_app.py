import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from services.data_generator import FinancialDataGenerator
from services.vector_search_service import VectorSearchService
from services.summarizer_service import SummarizerService
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .transaction-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_service' not in st.session_state:
    st.session_state.vector_service = None
if 'summarizer_service' not in st.session_state:
    st.session_state.summarizer_service = None
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/money-bag.png", width=80)
    st.title("🏦 Financial Assistant")
    st.markdown("---")
    
    # Setup Section
    st.header("⚙️ Setup")
    
    # Step 1: Generate Data
    st.subheader("1️⃣ Generate Data")
    col1, col2 = st.columns([2, 1])
    with col1:
        num_users = st.number_input("Users", min_value=1, max_value=10, value=3)
        num_transactions = st.number_input("Transactions/User", min_value=50, max_value=500, value=150)
    
    if st.button("🔄 Generate Transactions", use_container_width=True):
        with st.spinner("Generating transactions..."):
            try:
                generator = FinancialDataGenerator()
                transactions = generator.generate_data(
                    num_users=num_users,
                    transactions_per_user=num_transactions
                )
                generator.save_to_json(transactions, settings.DATA_PATH)
                st.success(f"✅ Generated {len(transactions)} transactions!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Step 2: Initialize Database
    st.subheader("2️⃣ Initialize Vector DB")
    if st.button("🗄️ Initialize ChromaDB", use_container_width=True):
        with st.spinner("Initializing vector database..."):
            try:
                if os.path.exists(settings.DATA_PATH):
                    st.session_state.vector_service = VectorSearchService()
                    st.session_state.vector_service.initialize_database(settings.DATA_PATH)
                    st.session_state.db_initialized = True
                    st.success("✅ Database initialized!")
                else:
                    st.error("⚠️ Please generate data first!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Step 3: API Key Check
    st.subheader("3️⃣ API Configuration")
    if settings.GROQ_API_KEY:
        st.success("✅ Groq API Key configured")
        if st.session_state.summarizer_service is None:
            try:
                st.session_state.summarizer_service = SummarizerService()
            except:
                pass
    else:
        st.warning("⚠️ Set GROQ_API_KEY in .env")
    
    st.markdown("---")
    
    # User Selection
    if os.path.exists(settings.DATA_PATH):
        with open(settings.DATA_PATH, 'r') as f:
            all_transactions = json.load(f)
        users = list(set([t['userId'] for t in all_transactions]))
        selected_user = st.selectbox("👤 Select User", ["All Users"] + users)
    else:
        selected_user = "All Users"
    
    st.markdown("---")
    st.caption("Built with Streamlit, ChromaDB & Groq")

# Main content
st.markdown('<div class="main-header">💰 AI-Powered Financial Assistant</div>', unsafe_allow_html=True)

# Check if services are initialized
if not st.session_state.vector_service:
    st.session_state.vector_service = VectorSearchService()

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "📊 Dashboard", "📝 All Transactions", "💡 Insights"])

# Tab 1: Semantic Search
with tab1:
    st.header("🔍 Semantic Search")
    st.markdown("Ask questions in natural language about your transactions")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - Show all UPI transactions above ₹1000
        - What's my biggest expense in August?
        - How much did I spend on food last month?
        - Show my top 5 expenses in September
        - List all salary credits
        - What did I spend on entertainment?
        - Show transactions from Swiggy
        - My total spending on shopping
        """)
    
    # Search interface
    query = st.text_input("🔎 Enter your query:", placeholder="e.g., Show my top 5 expenses last month")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        top_k = st.slider("Number of results", min_value=5, max_value=50, value=10)
    with col2:
        use_summary = st.checkbox("Generate Summary", value=True)
    with col3:
        search_button = st.button("🚀 Search", use_container_width=True, type="primary")
    
    if search_button and query:
        if st.session_state.db_initialized or st.session_state.vector_service.collection:
            with st.spinner("Searching..."):
                try:
                    # Get user filter
                    user_filter = None if selected_user == "All Users" else selected_user
                    
                    # Search
                    results = st.session_state.vector_service.search(
                        query=query,
                        n_results=top_k,
                        user_id=user_filter
                    )
                    
                    if results:
                        st.success(f"Found {len(results)} relevant transactions")
                        
                        # Generate summary
                        if use_summary and st.session_state.summarizer_service:
                            with st.spinner("Generating summary..."):
                                summary = st.session_state.summarizer_service.summarize_transactions(
                                    query=query,
                                    transactions=results
                                )
                                st.info(f"**💬 Summary:**\n\n{summary}")
                        
                        # Display results
                        st.markdown("### 📋 Transactions")
                        for i, txn in enumerate(results, 1):
                            with st.container():
                                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                                
                                with col1:
                                    st.markdown(f"**{txn['description']}**")
                                    st.caption(f"{txn['date']} • {txn['category']}")
                                
                                with col2:
                                    st.text(txn['userId'])
                                
                                with col3:
                                    color = "🔴" if txn['type'] == "Debit" else "🟢"
                                    st.markdown(f"{color} **₹{txn['amount']:,}**")
                                
                                with col4:
                                    st.caption(f"Balance: ₹{txn['balance']:,}")
                                
                                st.markdown("---")
                    else:
                        st.warning("No transactions found for your query.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Please initialize the database first from the sidebar!")

# Tab 2: Dashboard
with tab2:
    st.header("📊 Financial Dashboard")
    
    if os.path.exists(settings.DATA_PATH):
        # Load data
        with open(settings.DATA_PATH, 'r') as f:
            transactions = json.load(f)
        
        # Filter by user
        if selected_user != "All Users":
            transactions = [t for t in transactions if t['userId'] == selected_user]
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_credit = df[df['type'] == 'Credit']['amount'].sum()
        total_debit = df[df['type'] == 'Debit']['amount'].sum()
        net_balance = total_credit - total_debit
        avg_transaction = df['amount'].mean()
        
        with col1:
            st.metric("💰 Total Income", f"₹{total_credit:,.0f}")
        with col2:
            st.metric("💸 Total Expenses", f"₹{total_debit:,.0f}")
        with col3:
            st.metric("📈 Net Balance", f"₹{net_balance:,.0f}", 
                     delta=f"{(net_balance/total_credit*100):.1f}%" if total_credit > 0 else "0%")
        with col4:
            st.metric("📊 Avg Transaction", f"₹{avg_transaction:,.0f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Spending by Category
            category_spending = df[df['type'] == 'Debit'].groupby('category')['amount'].sum().reset_index()
            category_spending = category_spending.sort_values('amount', ascending=False)
            
            fig_category = px.pie(
                category_spending,
                values='amount',
                names='category',
                title='💳 Spending by Category',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_category.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Credit vs Debit
            type_summary = df.groupby('type')['amount'].sum().reset_index()
            
            fig_type = go.Figure(data=[
                go.Bar(
                    x=type_summary['type'],
                    y=type_summary['amount'],
                    marker_color=['#ff6b6b', '#51cf66'],
                    text=type_summary['amount'].apply(lambda x: f'₹{x:,.0f}'),
                    textposition='outside'
                )
            ])
            fig_type.update_layout(
                title='💵 Credit vs Debit',
                xaxis_title='Transaction Type',
                yaxis_title='Amount (₹)',
                showlegend=False
            )
            st.plotly_chart(fig_type, use_container_width=True)
        
        # Monthly Trend
        monthly_data = df.groupby(['month', 'type'])['amount'].sum().reset_index()
        
        fig_trend = px.line(
            monthly_data,
            x='month',
            y='amount',
            color='type',
            title='📈 Monthly Transaction Trend',
            markers=True,
            color_discrete_map={'Credit': '#51cf66', 'Debit': '#ff6b6b'}
        )
        fig_trend.update_layout(
            xaxis_title='Month',
            yaxis_title='Amount (₹)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Top Merchants
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Expenses")
            top_expenses = df[df['type'] == 'Debit'].nlargest(10, 'amount')[['date', 'description', 'amount', 'category']]
            st.dataframe(
                top_expenses.style.format({'amount': '₹{:,.0f}'}),
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.subheader("💎 Category-wise Spending")
            category_detail = df[df['type'] == 'Debit'].groupby('category').agg({
                'amount': ['sum', 'mean', 'count']
            }).round(0)
            category_detail.columns = ['Total', 'Average', 'Count']
            category_detail = category_detail.sort_values('Total', ascending=False)
            st.dataframe(
                category_detail.style.format({'Total': '₹{:,.0f}', 'Average': '₹{:,.0f}'}),
                use_container_width=True
            )
    
    else:
        st.info("📂 Please generate transaction data first from the sidebar.")

# Tab 3: All Transactions
with tab3:
    st.header("📝 All Transactions")
    
    if os.path.exists(settings.DATA_PATH):
        with open(settings.DATA_PATH, 'r') as f:
            transactions = json.load(f)
        
        # Filter by user
        if selected_user != "All Users":
            transactions = [t for t in transactions if t['userId'] == selected_user]
        
        df = pd.DataFrame(transactions)
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_type = st.multiselect("Type", options=['Credit', 'Debit'], default=['Credit', 'Debit'])
        with col2:
            categories = df['category'].unique().tolist()
            filter_category = st.multiselect("Category", options=categories, default=categories)
        with col3:
            min_amount = st.number_input("Min Amount", min_value=0, value=0)
        with col4:
            max_amount = st.number_input("Max Amount", min_value=0, value=int(df['amount'].max()))
        
        # Apply filters
        filtered_df = df[
            (df['type'].isin(filter_type)) &
            (df['category'].isin(filter_category)) &
            (df['amount'] >= min_amount) &
            (df['amount'] <= max_amount)
        ].sort_values('date', ascending=False)
        
        st.info(f"Showing {len(filtered_df)} of {len(df)} transactions")
        
        # Display transactions
        st.dataframe(
            filtered_df[['date', 'description', 'amount', 'type', 'category', 'balance']].style.format({
                'amount': '₹{:,.0f}',
                'balance': '₹{:,.0f}'
            }),
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"transactions_{selected_user}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    else:
        st.info("📂 Please generate transaction data first from the sidebar.")

# Tab 4: AI Insights
with tab4:
    st.header("💡 AI-Powered Insights")
    
    if os.path.exists(settings.DATA_PATH) and st.session_state.summarizer_service:
        if st.button("🔮 Generate Insights", type="primary", use_container_width=True):
            with st.spinner("Analyzing your financial data..."):
                try:
                    # Get user filter
                    user_filter = None if selected_user == "All Users" else selected_user
                    
                    # Get transactions
                    if st.session_state.vector_service and st.session_state.vector_service.collection:
                        transactions = st.session_state.vector_service.get_all_transactions(user_id=user_filter)
                        
                        if transactions:
                            insights = st.session_state.summarizer_service.get_spending_insights(transactions)
                            
                            st.success("✨ Insights Generated!")
                            st.markdown("### 📊 Your Financial Analysis")
                            st.info(insights)
                            
                            # Additional stats
                            df = pd.DataFrame(transactions)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 📈 Quick Stats")
                                total_transactions = len(df)
                                debit_count = len(df[df['type'] == 'Debit'])
                                credit_count = len(df[df['type'] == 'Credit'])
                                
                                st.metric("Total Transactions", total_transactions)
                                st.metric("Debit Transactions", debit_count)
                                st.metric("Credit Transactions", credit_count)
                            
                            with col2:
                                st.markdown("#### 💰 Spending Overview")
                                avg_debit = df[df['type'] == 'Debit']['amount'].mean()
                                max_debit = df[df['type'] == 'Debit']['amount'].max()
                                
                                st.metric("Average Expense", f"₹{avg_debit:,.0f}")
                                st.metric("Highest Expense", f"₹{max_debit:,.0f}")
                        else:
                            st.warning("No transactions found.")
                    else:
                        st.warning("Please initialize the database first!")
                
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
    else:
        if not st.session_state.summarizer_service:
            st.warning("⚠️ Groq API key not configured. Please set GROQ_API_KEY in your .env file.")
        else:
            st.info("📂 Please generate transaction data and initialize the database first.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit, ChromaDB, Groq & Sentence Transformers</p>
    </div>
    """,
    unsafe_allow_html=True
)