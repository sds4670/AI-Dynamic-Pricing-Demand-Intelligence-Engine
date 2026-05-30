"""
LangChain-based AI agent for pricing recommendations.
Uses Azure OpenAI to reason over data and provide strategic recommendations.
"""

from typing import Dict, List, Tuple, Any
import json
import pandas as pd
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from src.utils.logger import logger
from src.utils.config import get_config
from src.utils.azure_clients import get_openai_client


class PricingRecommendationAgent:
    """AI agent for intelligent pricing recommendations."""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize pricing recommendation agent.
        
        Args:
            verbose: Whether to log agent reasoning
        """
        self.verbose = verbose
        self.llm = self._setup_llm()
        self.tools = self._setup_tools()
        self.agent_executor = self._setup_agent()
        self.conversation_history = []
        
        logger.info("Initialized PricingRecommendationAgent")
    
    def _setup_llm(self) -> AzureChatOpenAI:
        """Setup Azure OpenAI LLM."""
        openai_client = get_openai_client()
        config = openai_client.get_config()
        
        llm = AzureChatOpenAI(
            api_key=config['api_key'],
            azure_endpoint=config['azure_endpoint'],
            deployment_name=config['deployment_name'],
            api_version=config['api_version'],
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )
        
        return llm
    
    def _setup_tools(self) -> List[Tool]:
        """Setup agent tools."""
        tools = [
            Tool(
                name="analyze_elasticity",
                func=self._tool_analyze_elasticity,
                description="Analyze price elasticity to determine price sensitivity of a product"
            ),
            Tool(
                name="analyze_forecast",
                func=self._tool_analyze_forecast,
                description="Analyze demand forecast to identify trends and patterns"
            ),
            Tool(
                name="calculate_price_impact",
                func=self._tool_calculate_price_impact,
                description="Calculate revenue impact of price changes"
            ),
            Tool(
                name="get_market_insights",
                func=self._tool_get_market_insights,
                description="Get insights from historical pricing and sales data"
            )
        ]
        
        return tools
    
    def _setup_agent(self) -> AgentExecutor:
        """Setup agent executor."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert e-commerce pricing strategist helping sellers optimize their pricing.
            
Your role is to:
1. Analyze product elasticity to understand price sensitivity
2. Review demand forecasts to identify trends
3. Calculate potential revenue impacts of price changes
4. Provide clear, actionable pricing recommendations
5. Consider market conditions and competition

Always provide reasoning for your recommendations and quantify potential impacts.
Focus on maximizing revenue while maintaining healthy margins.
Be conservative with discounts - only recommend them when data strongly supports it."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True
        )
        
        return executor
    
    def _tool_analyze_elasticity(self, elasticity_data: str) -> str:
        """Tool: Analyze price elasticity."""
        try:
            data = json.loads(elasticity_data)
            elasticity = data.get('elasticity', 0)
            r_squared = data.get('r_squared', 0)
            
            if abs(elasticity) > 1.5:
                sensitivity = "HIGHLY ELASTIC - Very price sensitive"
            elif abs(elasticity) > 1.0:
                sensitivity = "ELASTIC - Price sensitive"
            elif abs(elasticity) > 0.5:
                sensitivity = "INELASTIC - Less price sensitive"
            else:
                sensitivity = "HIGHLY INELASTIC - Very insensitive to price"
            
            analysis = f"""
Elasticity Analysis:
- Coefficient: {elasticity:.3f}
- Model Fit (R²): {r_squared:.3f}
- Classification: {sensitivity}
- Interpretation: For every 1% price increase, quantity changes by {elasticity:.2f}%
"""
            return analysis
        except Exception as e:
            return f"Error analyzing elasticity: {str(e)}"
    
    def _tool_analyze_forecast(self, forecast_data: str) -> str:
        """Tool: Analyze demand forecast."""
        try:
            data = json.loads(forecast_data)
            predicted_qty = data.get('predicted_quantity', 0)
            confidence = data.get('confidence_score', 0)
            trend = data.get('trend', 'stable')
            
            analysis = f"""
Demand Forecast Analysis:
- Predicted Quantity (next 30 days avg): {predicted_qty:.0f} units
- Forecast Confidence: {confidence * 100:.1f}%
- Trend: {trend}
- Recommendation: {'Good time to focus on volume' if trend == 'uptrend' else 'Focus on margin optimization'}
"""
            return analysis
        except Exception as e:
            return f"Error analyzing forecast: {str(e)}"
    
    def _tool_calculate_price_impact(self, impact_data: str) -> str:
        """Tool: Calculate price impact."""
        try:
            data = json.loads(impact_data)
            revenue_change_pct = data.get('revenue_change_pct', 0)
            new_revenue = data.get('new_revenue', 0)
            
            impact = f"""
Price Impact Analysis:
- Revenue Impact: {revenue_change_pct:+.1f}%
- Projected New Revenue: ₹{new_revenue:,.0f}
- Recommended: {'✓ Proceed' if revenue_change_pct > 0 else '✗ Not recommended'}
"""
            return impact
        except Exception as e:
            return f"Error calculating impact: {str(e)}"
    
    def _tool_get_market_insights(self, market_data: str) -> str:
        """Tool: Get market insights."""
        try:
            data = json.loads(market_data)
            current_price = data.get('current_price', 0)
            avg_price_market = data.get('avg_price_market', 0)
            price_position = data.get('price_position', 'market_price')
            
            if current_price < avg_price_market * 0.9:
                insight = "Your price is significantly BELOW market - opportunity to increase"
            elif current_price > avg_price_market * 1.1:
                insight = "Your price is significantly ABOVE market - consider competitive positioning"
            else:
                insight = "Your price is competitive with market average"
            
            insights = f"""
Market Insights:
- Your Price: ₹{current_price:,.0f}
- Market Average: ₹{avg_price_market:,.0f}
- Position: {price_position}
- Insight: {insight}
"""
            return insights
        except Exception as e:
            return f"Error getting insights: {str(e)}"
    
    def get_recommendation(
        self,
        product_name: str,
        current_price: float,
        elasticity: float,
        forecast: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get pricing recommendation from agent.
        
        Args:
            product_name: Product name
            current_price: Current selling price
            elasticity: Price elasticity coefficient
            forecast: Demand forecast data
            market_data: Market context data
            
        Returns:
            Recommendation with reasoning
        """
        # Prepare context for agent
        context = f"""
I need a pricing recommendation for the following product:

Product: {product_name}
Current Price: ₹{current_price:,.0f}

Price Elasticity:
- Coefficient: {elasticity:.3f}
- Interpretation: {'Price sensitive' if abs(elasticity) > 1 else 'Price insensitive'}

Demand Forecast (Next 30 Days):
- Predicted Average Quantity: {forecast.get('predicted_quantity', 0):.0f} units
- Confidence Level: {forecast.get('confidence_score', 0) * 100:.1f}%
- Trend: {forecast.get('trend', 'stable')}

Market Context:
- Average Market Price: ₹{market_data.get('avg_price_market', 0):,.0f}
- Your Price Position: {'Below' if current_price < market_data.get('avg_price_market', 0) else 'Above'} market average

Based on this data, what pricing strategy would you recommend? Consider:
1. Revenue optimization vs. volume growth
2. Competitive positioning
3. Margin sustainability
4. Whether to discount or increase price
"""
        
        try:
            response = self.agent_executor.run(context)
            
            recommendation = {
                'product': product_name,
                'current_price': current_price,
                'recommendation': response,
                'elasticity_coefficient': elasticity,
                'confidence_high': forecast.get('confidence_score', 0) > 0.7
            }
            
            self.conversation_history.append({
                'user': context,
                'assistant': response
            })
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting recommendation: {str(e)}")
            return {
                'product': product_name,
                'recommendation': f"Unable to generate recommendation: {str(e)}",
                'error': True
            }
    
    def chat(self, message: str) -> str:
        """
        Have a conversation with the agent about pricing.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        try:
            response = self.agent_executor.run(message)
            
            self.conversation_history.append({
                'user': message,
                'assistant': response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
