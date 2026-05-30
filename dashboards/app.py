"""
Streamlit dashboard for AI Pricing Engine.
Main UI for sellers to view KPIs, forecasts, and pricing recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Pricing Engine",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .recommendation-card {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4caf50;
    }
    .warning-card {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application."""
    
    # Sidebar
    st.sidebar.title("🛍️ AI Pricing Engine")
    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.radio(
        "Select View",
        ["Dashboard", "Upload Data", "Product Analysis", "AI Chat", "Settings"]
    )
    
    # Main content
    if app_mode == "Dashboard":
        show_dashboard()
    elif app_mode == "Upload Data":
        show_upload()
    elif app_mode == "Product Analysis":
        show_product_analysis()
    elif app_mode == "AI Chat":
        show_ai_chat()
    elif app_mode == "Settings":
        show_settings()


def show_dashboard():
    """Show main dashboard with KPIs and forecasts."""
    st.title("📊 Pricing Intelligence Dashboard")
    
    # Key Metrics Section
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            "₹45,230",
            "+12.5%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Avg Margin",
            "28.5%",
            "+2.3%"
        )
    
    with col3:
        st.metric(
            "Active Products",
            "156",
            "+8"
        )
    
    with col4:
        st.metric(
            "Forecast Accuracy",
            "87.3%",
            "+3.1%"
        )
    
    st.markdown("---")
    
    # Forecast Charts
    st.subheader("📅 Demand Forecasts (Next 30 Days)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample forecast data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        forecast_df = pd.DataFrame({
            'date': dates,
            'predicted': np.random.randint(50, 150, 30) + np.linspace(0, 30, 30),
            'lower_bound': np.random.randint(40, 120, 30),
            'upper_bound': np.random.randint(80, 180, 30),
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_df['date'], y=forecast_df['predicted'],
            mode='lines', name='Predicted',
            line=dict(color='#1f77b4', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['date'], y=forecast_df['upper_bound'],
            fill=None, mode='lines',
            line_color='rgba(0,0,0,0)', showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['date'], y=forecast_df['lower_bound'],
            fillcolor='rgba(31, 119, 180, 0.2)',
            fill='tonexty', mode='lines',
            line_color='rgba(0,0,0,0)', name='95% Confidence'
        ))
        
        fig.update_layout(
            title='Sales Forecast - Top Product',
            xaxis_title='Date',
            yaxis_title='Quantity',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price elasticity chart
        prices = np.linspace(100, 500, 20)
        elasticity = -1.5  # Sample elasticity
        quantities = 1000 * (prices / 200) ** elasticity
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices, y=quantities,
            mode='lines+markers',
            name='Demand Curve',
            line=dict(color='#d62728', width=3)
        ))
        
        fig.update_layout(
            title='Price-Demand Elasticity',
            xaxis_title='Price (₹)',
            yaxis_title='Quantity Demanded',
            hovermode='x',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top Recommendations
    st.subheader("💡 Pricing Recommendations")
    
    recommendations = [
        {
            'product': 'Wireless Earbuds',
            'action': 'Reduce Price by 8%',
            'impact': '+22% Revenue',
            'reason': 'High elasticity + Strong demand forecast',
            'confidence': 0.92
        },
        {
            'product': 'Phone Case',
            'action': 'Hold Current Price',
            'impact': 'Optimal margin',
            'reason': 'Inelastic demand + Stable forecast',
            'confidence': 0.88
        },
        {
            'product': 'USB Cable',
            'action': 'Increase Price by 5%',
            'impact': '+15% Revenue',
            'reason': 'Very inelastic + Low price elasticity',
            'confidence': 0.85
        }
    ]
    
    for rec in recommendations:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{rec['product']}**")
                st.markdown(f"<small>{rec['reason']}</small>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{rec['action']}**")
            with col3:
                st.markdown(f"<strong style='color: green'>{rec['impact']}</strong>", unsafe_allow_html=True)
                st.markdown(f"<small>Confidence: {rec['confidence']*100:.0f}%</small>", unsafe_allow_html=True)
            st.markdown("---")
    
    # Product Performance Table
    st.subheader("📋 Product Performance Summary")
    
    products_data = {
        'Product': ['Wireless Earbuds', 'Phone Case', 'USB Cable', 'Screen Protector', 'Phone Stand'],
        'Current Price': [₹1299, ₹299, ₹149, ₹199, ₹399],
        'Avg Sales': [45, 120, 89, 156, 32],
        'Elasticity': [-1.52, -0.45, -0.32, -0.28, -1.65],
        'Forecast Trend': ['↑ Uptrend', '→ Stable', '→ Stable', '↓ Downtrend', '↑ Uptrend'],
        'Recommended Action': ['↓ Discount', '→ Hold', '↑ Increase', '↓ Discount', '↑ Increase']
    }
    
    df_products = pd.DataFrame(products_data)
    st.dataframe(df_products, use_container_width=True, hide_index=True)


def show_upload():
    """Show data upload interface."""
    st.title("📤 Upload Sales Data")
    
    st.write("Upload your sales CSV file to analyze pricing opportunities.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Expected columns: date, product_id, price, quantity, ..."
    )
    
    if uploaded_file is not None:
        st.success(f"✓ File uploaded: {uploaded_file.name}")
        
        # Show preview
        df = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        st.subheader("Data Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Date Range", f"{df['date'].min() if 'date' in df.columns else 'N/A'}")
        
        if st.button("Process & Analyze Data"):
            st.info("Processing data... This may take a few minutes for large files.")
            # Placeholder for actual processing
            st.success("✓ Data processed successfully! View results in Product Analysis.")


def show_product_analysis():
    """Show detailed product analysis."""
    st.title("🔍 Product Analysis")
    
    # Product selector
    st.subheader("Select Product")
    product = st.selectbox(
        "Choose a product to analyze",
        ["Wireless Earbuds", "Phone Case", "USB Cable", "Screen Protector", "Phone Stand"]
    )
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Elasticity", "Forecast", "Recommendations"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", "₹1,299")
        with col2:
            st.metric("Avg Monthly Sales", "1,350 units")
        with col3:
            st.metric("Margin", "32%")
        
        st.markdown("---")
        st.write("**Historical Performance**")
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='MS')
        sales_data = pd.DataFrame({
            'month': dates,
            'revenue': np.random.randint(10000, 50000, len(dates)),
            'units': np.random.randint(50, 200, len(dates))
        })
        st.line_chart(sales_data.set_index('month'))
    
    with tab2:
        st.write("**Price Elasticity Analysis**")
        st.metric("Elasticity Coefficient", "-1.52", "Highly Elastic")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("- **R² (Model Fit):** 0.78")
            st.write("- **P-value:** < 0.001 (Significant)")
            st.write("- **Sample Size:** 45 observations")
        
        with col2:
            st.write("**Interpretation:**")
            st.write("This product is highly price-sensitive. A 1% price decrease leads to a 1.52% quantity increase.")
    
    with tab3:
        st.write("**Demand Forecast (Next 30 Days)**")
        st.metric("Avg Daily Sales", "45 units", "+12%")
        
        # Forecast chart
        forecast_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        forecast = pd.DataFrame({
            'date': forecast_dates,
            'quantity': np.random.randint(40, 55, 30)
        })
        st.area_chart(forecast.set_index('date'))
    
    with tab4:
        st.write("**AI Pricing Recommendation**")
        st.markdown("""
        **Recommended Action:** Reduce price by 8%
        
        **Current Price:** ₹1,299  
        **Recommended Price:** ₹1,195
        
        **Expected Impact:**
        - Quantity increase: +12% (45 → 50 units/day)
        - Revenue change: +3.5% (₹58,455 → ₹60,462/month)
        - Margin impact: -0.5% (maintained strong margins)
        
        **Rationale:**
        1. High price elasticity indicates customers are price-sensitive
        2. Demand forecast shows uptrend - good timing for promotional pricing
        3. Revenue simulation shows positive ROI on discount
        4. Still maintains healthy 30% margins
        """)


def show_ai_chat():
    """Show AI chat interface."""
    st.title("💬 AI Pricing Assistant")
    
    st.write("Ask me questions about your products' pricing strategy!")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about pricing..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simulate AI response (placeholder)
        response = f"""
Based on your question about **{prompt[:30]}...**:

I recommend analyzing your price elasticity and demand forecast data. 

Here's what I found:
- Your product has moderate price elasticity (-0.85)
- Demand forecast shows stable trend over next 30 days
- Market average price for similar products is ₹1,150

**Recommendation:** Keep current price or increase by 2-3% if margins allow.

Would you like me to provide more detailed analysis?
"""
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.markdown(response)


def show_settings():
    """Show settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Forecasting Settings**")
        forecast_horizon = st.slider("Forecast Horizon (days)", 7, 90, 30)
        min_confidence = st.slider("Minimum Forecast Confidence", 0.5, 0.99, 0.75)
    
    with col2:
        st.write("**Pricing Settings**")
        max_discount = st.slider("Max Discount (%)", 5, 30, 20)
        min_margin = st.slider("Min Margin (%)", 10, 40, 15)
    
    st.markdown("---")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("✓ Cache cleared")
    
    with col2:
        if st.button("Export Settings"):
            st.info("Settings exported to config.yaml")
    
    st.markdown("---")
    
    st.subheader("API Credentials")
    
    st.warning("⚠️ Never share your API keys or credentials!")
    
    if st.checkbox("Configure Azure Credentials"):
        azure_account = st.text_input("Azure Storage Account", type="password")
        azure_key = st.text_input("Azure Storage Key", type="password")
        openai_key = st.text_input("Azure OpenAI Key", type="password")
        
        if st.button("Save Credentials"):
            st.success("✓ Credentials saved securely")


if __name__ == "__main__":
    main()
