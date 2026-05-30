"""
Demand forecasting using Facebook Prophet.
Predicts future sales for products.
"""

from typing import Tuple, Dict, Optional
import pandas as pd
from prophet import Prophet
from src.utils.logger import logger
from src.utils.config import get_config


class DemandForecaster:
    """Demand forecasting using Facebook Prophet."""
    
    def __init__(
        self,
        forecast_horizon: int = 30,
        seasonality_mode: str = 'additive',
        seasonality_period: int = 365,
        interval_width: float = 0.95
    ):
        """
        Initialize forecaster.
        
        Args:
            forecast_horizon: Number of days to forecast
            seasonality_mode: 'additive' or 'multiplicative'
            seasonality_period: Period for seasonality (e.g., 365 for yearly)
            interval_width: Confidence interval width (0-1)
        """
        self.forecast_horizon = forecast_horizon
        self.seasonality_mode = seasonality_mode
        self.seasonality_period = seasonality_period
        self.interval_width = interval_width
        self.models = {}  # Store trained models
        
        logger.info(
            f"Initialized DemandForecaster: horizon={forecast_horizon} days, "
            f"seasonality={seasonality_mode}"
        )
    
    def _create_prophet_model(self) -> Prophet:
        """Create and configure Prophet model."""
        return Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode=self.seasonality_mode,
            interval_width=self.interval_width,
            changepoint_prior_scale=0.05
        )
    
    def train(
        self,
        df: pd.DataFrame,
        product_id: str = 'default'
    ) -> Tuple[Prophet, pd.DataFrame]:
        """
        Train Prophet model on product sales data.
        
        Args:
            df: DataFrame with 'ds' (date) and 'y' (quantity) columns
            product_id: Product identifier
            
        Returns:
            Tuple of (trained model, fitted data)
        """
        # Validate data
        if len(df) < 14:
            raise ValueError(f"Need at least 14 data points, got {len(df)}")
        
        # Create and train model
        model = self._create_prophet_model()
        model.fit(df)
        
        # Store model
        self.models[product_id] = model
        
        logger.info(f"Trained forecaster for product {product_id} with {len(df)} historical records")
        
        # Return model and fitted data
        forecast_data = model.predict(df[['ds']])
        
        return model, forecast_data
    
    def forecast(
        self,
        df: pd.DataFrame,
        product_id: str = 'default'
    ) -> pd.DataFrame:
        """
        Forecast future demand for a product.
        
        Args:
            df: Historical data with 'ds' and 'y' columns
            product_id: Product identifier
            
        Returns:
            Forecast DataFrame with future predictions
        """
        # Train if not already trained
        if product_id not in self.models:
            self.train(df, product_id)
        
        model = self.models[product_id]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=self.forecast_horizon)
        forecast = model.predict(future)
        
        # Extract relevant columns
        forecast_output = forecast[[
            'ds', 'yhat', 'yhat_lower', 'yhat_upper'
        ]].tail(self.forecast_horizon).copy()
        
        forecast_output.columns = [
            'date', 'predicted_quantity', 'lower_bound', 'upper_bound'
        ]
        
        # Ensure non-negative quantities
        forecast_output['predicted_quantity'] = forecast_output['predicted_quantity'].clip(lower=0)
        forecast_output['lower_bound'] = forecast_output['lower_bound'].clip(lower=0)
        
        forecast_output['product_id'] = product_id
        
        logger.info(f"Generated forecast for product {product_id}: {len(forecast_output)} days")
        
        return forecast_output
    
    def get_forecast_confidence(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate confidence metrics for forecast.
        
        Args:
            forecast_df: Forecast DataFrame
            
        Returns:
            DataFrame with confidence metrics
        """
        forecast_df = forecast_df.copy()
        
        # Calculate interval width
        forecast_df['confidence_interval'] = (
            forecast_df['upper_bound'] - forecast_df['lower_bound']
        )
        
        # Calculate relative uncertainty
        forecast_df['uncertainty_pct'] = (
            forecast_df['confidence_interval'] / (forecast_df['predicted_quantity'] + 1) * 100
        )
        
        # Confidence score (inverse of uncertainty)
        forecast_df['confidence_score'] = (
            100 - forecast_df['uncertainty_pct'].clip(upper=100)
        ) / 100
        
        return forecast_df
    
    def get_model(self, product_id: str) -> Optional[Prophet]:
        """Get trained model for product."""
        return self.models.get(product_id)
    
    def get_model_components(self, product_id: str) -> Dict:
        """Get model components (trend, seasonality) for product."""
        model = self.get_model(product_id)
        if not model:
            return {}
        
        return {
            'trend': model.trend,
            'yearly_seasonality': model.yearly_seasonality,
            'weekly_seasonality': model.weekly_seasonality
        }
    
    def batch_forecast(self, product_histories: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Forecast for multiple products.
        
        Args:
            product_histories: Dict of {product_id: historical_df}
            
        Returns:
            Combined forecast DataFrame
        """
        all_forecasts = []
        
        for product_id, hist_df in product_histories.items():
            try:
                forecast_df = self.forecast(hist_df, product_id)
                all_forecasts.append(forecast_df)
            except Exception as e:
                logger.warning(f"Failed to forecast for product {product_id}: {str(e)}")
        
        if all_forecasts:
            return pd.concat(all_forecasts, ignore_index=True)
        else:
            return pd.DataFrame()
