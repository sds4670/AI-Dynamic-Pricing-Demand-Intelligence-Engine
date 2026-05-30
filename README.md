# 💰 AI Dynamic Pricing & Demand Intelligence Engine

**An AI-powered platform for small e-commerce sellers to make data-driven pricing decisions and forecast demand.**

---

## 🎯 Problem

Small e-commerce sellers on Meesho, Flipkart, and Amazon India face challenges:
- **Blind pricing decisions** leading to lost margins
- **Missing demand spikes** during peak seasons
- **Excessive discounting** without understanding elasticity
- **No data-driven insights** into price sensitivity

This engine solves all of these by combining:
1. **Demand Forecasting** (Prophet) - Predict next 30 days of sales
2. **Price Elasticity Analysis** - Understand how customers respond to price changes
3. **AI Recommendations** (Azure OpenAI + LangChain) - Get strategic pricing advice

---

## ✨ Key Features

| Feature | What it Does |
|---------|-------------|
| **Demand Forecasting** | Predict product sales for the next 30 days using Facebook Prophet |
| **Price Elasticity** | Measure price sensitivity per product (elastic vs inelastic) |
| **Pricing Recommendations** | AI agent suggests "raise 5%" or "hold price" with revenue impact |
| **KPI Dashboard** | Real-time metrics: revenue, margins, forecast confidence |
| **AI Chat** | Ask "should I discount?" and get reasoning |
| **Multi-Market Validation** | Uses Olist, Flipkart India, Amazon India datasets |

---

## 🏗️ Architecture

```
Raw Data (Olist, Flipkart, Amazon India)
    ↓
Azure Blob Storage (store CSV data)
    ↓
PySpark + Databricks (clean, aggregate, transform)
    ↓
Delta Tables (fast, queryable processed data)
    ↓
Prophet → Demand Forecasts
Elasticity Model → Price Sensitivity Scores
    ↓
Azure OpenAI + LangChain Agent
(reason over analytics, generate recommendations)
    ↓
Streamlit Dashboard
(seller sees KPIs, charts, chat recommendations)
```

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Data Processing** | PySpark | Scalable pipeline for millions of transactions |
| **Analytics Platform** | Databricks | Managed Spark + collaborative notebooks |
| **Cloud Storage** | Azure Blob Storage | Store raw CSVs, maintain data versioning |
| **Forecasting** | Prophet | Handles seasonality, holidays, trends |
| **ML Models** | Scikit-learn | Price elasticity regression |
| **AI Agent** | Azure OpenAI + LangChain | Tool-calling agent for reasoning |
| **UI/Dashboard** | Streamlit | Interactive web app for sellers |
| **Backend** | Python | Everything orchestrated in Python |

---

## 📂 Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── data/                      # Data processing
│   │   ├── __init__.py
│   │   └── data_processor.py      # PySpark data pipeline
│   ├── models/                    # ML models
│   │   ├── __init__.py
│   │   ├── forecaster.py          # Prophet demand forecasting
│   │   └── elasticity.py          # Price elasticity estimation
│   ├── agents/                    # AI agents
│   │   ├── __init__.py
│   │   └── pricing_agent.py       # LangChain pricing recommendation agent
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── config.py              # Configuration management
│       ├── logger.py              # Logging setup
│       └── azure_clients.py       # Azure SDK clients
├── dashboards/
│   └── app.py                     # Streamlit dashboard
├── notebooks/
│   ├── 01_data_processing.py      # Databricks data pipeline
│   └── 02_model_training.py       # Model training notebook
├── tests/
│   ├── test_data_processor.py     # Data processing tests
│   └── test_models.py             # Model tests
├── config/
│   └── config.yaml                # Configuration file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- Azure account (Storage, OpenAI)
- Databricks workspace (optional, for production pipelines)
- Kaggle datasets (Olist, Flipkart, Amazon India)

### 2. Installation

```bash
# Clone repository
git clone <repo-url>
cd AI-Dynamic-Pricing-Demand-Intelligence-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your Azure credentials
nano .env
```

Set these environment variables:

```env
# Azure Storage
AZURE_STORAGE_ACCOUNT=your_account_name
AZURE_STORAGE_KEY=your_account_key

# Azure OpenAI
AZURE_OPENAI_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Databricks (optional)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_token
```

### 4. Run Dashboard

```bash
streamlit run dashboards/app.py
```

Visit `http://localhost:8501` to see the dashboard.

### 5. Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Usage Examples

### Load and Process Data

```python
from src.data import OlistDataProcessor
from src.utils import logger

# Initialize processor
processor = OlistDataProcessor()

# Process Olist data
df = processor.process_olist("path/to/olist_data.csv")
logger.info(f"Processed {df.count()} rows")

# Get specific product forecast data
forecast_data = processor.prepare_forecast_data(df, product_id="P001")
```

### Forecast Demand

```python
from src.models import DemandForecaster
import pandas as pd

# Load historical sales
sales_df = pd.read_csv("sales_data.csv")

# Train forecaster
forecaster = DemandForecaster(forecast_horizon=30)
forecast = forecaster.forecast(sales_df, product_id="P001")

print(forecast[['date', 'predicted_quantity', 'confidence_score']])
```

### Analyze Price Elasticity

```python
from src.models import PriceElasticityModel

# Load price-quantity data
price_data = pd.read_csv("price_data.csv")

# Estimate elasticity
elasticity_model = PriceElasticityModel()
elasticity = elasticity_model.estimate_elasticity(price_data, product_id="P001")

print(f"Elasticity: {elasticity['elasticity']:.3f}")
print(f"Classification: {elasticity_model.classify_elasticity(elasticity['elasticity'])}")

# Calculate impact of 10% price reduction
impact = elasticity_model.estimate_price_impact(
    current_price=500,
    current_quantity=100,
    new_price=450,  # 10% reduction
    product_id="P001"
)
print(f"Revenue change: {impact['revenue_change_pct']:.1f}%")
```

### Get AI Pricing Recommendations

```python
from src.agents import PricingRecommendationAgent

# Initialize agent
agent = PricingRecommendationAgent()

# Get recommendation
recommendation = agent.get_recommendation(
    product_name="Wireless Earbuds",
    current_price=1299,
    elasticity=-1.52,
    forecast={'predicted_quantity': 45, 'confidence_score': 0.92, 'trend': 'uptrend'},
    market_data={'avg_price_market': 1200}
)

print(recommendation['recommendation'])

# Chat with agent
response = agent.chat("Should I discount this product for the next week?")
print(response)
```

---

## 🔄 Data Pipeline

### Step 1: Data Loading
- Load CSV from local/Azure Blob Storage
- Support for Olist, Flipkart, Amazon India formats
- Validate schema and data types

### Step 2: Data Cleaning
- Remove duplicates
- Handle missing values
- Filter invalid records (negative prices/quantities)
- Normalize column names

### Step 3: Feature Engineering
- Parse dates and extract temporal features
- Aggregate to daily level
- Calculate price changes and elasticity features
- Compute revenue metrics

### Step 4: Aggregation
- Store in Delta tables for fast querying
- Create daily_sales, product_stats aggregates
- Partition by date for efficient queries

### Step 5: Model Training
- Train Prophet on historical sales
- Fit elasticity regression models
- Evaluate forecast accuracy and elasticity significance

### Step 6: Recommendation Generation
- Use LangChain agent to reason over results
- Generate actionable pricing recommendations
- Calculate expected revenue impact

---

## 📈 Dashboard Features

### KPI Cards
- **Total Revenue** - Monthly revenue with trend
- **Average Margin** - Current margin %
- **Active Products** - Number of products selling
- **Forecast Accuracy** - Historical forecast accuracy

### Forecasting Charts
- **Demand Forecast** - 30-day sales prediction with confidence bands
- **Price-Demand Curve** - Elasticity visualization
- **Seasonal Patterns** - Yearly/weekly seasonality breakdown

### Recommendations
- **Priority Actions** - Top 3 pricing changes with expected impact
- **Product Summary** - All products with elasticity, forecast, recommendation

### AI Chat
- Ask questions about pricing strategy
- Get reasoning-based recommendations
- View conversation history

---

## 🧪 Testing

Run unit tests for data processing and models:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_processor.py -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html
```

---

## 🔐 Security Best Practices

1. **Never commit `.env`** - Use `.env.example` as template
2. **Rotate API keys** regularly
3. **Use Azure Key Vault** for production secrets
4. **Restrict blob storage** with IAM roles
5. **Enable audit logging** on Databricks

---

## 📚 Datasets

Download datasets from Kaggle:

1. **Olist E-Commerce Dataset** (primary training)
   - 100K transactions, multiple product categories
   - [Link](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

2. **Flipkart India Dataset** (validation)
   - Indian market prices and reviews
   - [Link](https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-india-products-inventory)

3. **Amazon India Dataset** (secondary validation)
   - Indian market products and pricing
   - [Link](https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-amazon-google-product-inventory)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## 📞 Support

For issues, questions, or suggestions:
- Open an GitHub issue
- Check existing documentation
- Review test files for usage examples

---

## 📄 License

This project is licensed under the MIT License.

---

## 🎓 Learning Resources

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [LangChain Documentation](https://python.langchain.com/)
- [PySpark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Azure OpenAI Guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

---

## 🌟 What Makes This Special

✅ **Real Business Problem** - Solves actual challenges for e-commerce sellers  
✅ **Production-Grade Architecture** - Cloud-native, scalable design  
✅ **Advanced ML** - Combines forecasting, elasticity, and AI reasoning  
✅ **Indian Market Focused** - Validated on Meesho, Flipkart, Amazon India data  
✅ **End-to-End Solution** - From raw data to actionable recommendations  
✅ **Modern Stack** - LLMs, Databricks, Delta Lake, Streamlit  

---

**Built with ❤️ for Indian e-commerce sellers**