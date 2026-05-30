"""
Price elasticity model to measure price sensitivity of products.
Estimates how demand changes with price changes.
"""

from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
from src.utils.logger import logger


class PriceElasticityModel:
    """Model to estimate price elasticity of demand."""
    
    def __init__(self, method: str = 'linear', min_data_points: int = 10):
        """
        Initialize elasticity model.
        
        Args:
            method: 'linear' or 'polynomial'
            min_data_points: Minimum observations needed to fit model
        """
        self.method = method
        self.min_data_points = min_data_points
        self.models = {}
        self.elasticities = {}
        
        logger.info(f"Initialized PriceElasticityModel: method={method}")
    
    def estimate_elasticity(
        self,
        df: pd.DataFrame,
        product_id: str = 'default'
    ) -> Dict[str, float]:
        """
        Estimate price elasticity for a product.
        
        Args:
            df: DataFrame with 'price' and 'quantity' columns
            product_id: Product identifier
            
        Returns:
            Dictionary with elasticity metrics
        """
        # Clean data
        df = df[['price', 'quantity']].dropna()
        df = df[(df['price'] > 0) & (df['quantity'] > 0)].copy()
        
        if len(df) < self.min_data_points:
            logger.warning(
                f"Insufficient data for {product_id}: {len(df)} observations"
            )
            return {
                'elasticity': 0,
                'r_squared': 0,
                'p_value': 1,
                'is_significant': False,
                'confidence': 0
            }
        
        # Calculate percentage changes
        df['log_price'] = np.log(df['price'])
        df['log_quantity'] = np.log(df['quantity'])
        
        # Fit regression: log(quantity) ~ log(price)
        X = df[['log_price']].values
        y = df['log_quantity'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        elasticity = float(model.coef_[0])
        
        # Calculate R-squared and p-value
        y_pred = model.predict(X)
        residuals = y - y_pred
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # T-test for significance
        n = len(df)
        t_stat = elasticity * np.sqrt((n - 2) / (1 - r_squared + 1e-10))
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
        
        # Confidence score based on R-squared and sample size
        confidence = min(r_squared * np.sqrt(n / 30), 1.0)
        
        result = {
            'elasticity': elasticity,
            'r_squared': r_squared,
            'p_value': p_value,
            'is_significant': p_value < 0.05,
            'confidence': confidence,
            'n_observations': len(df),
            'price_range': (df['price'].min(), df['price'].max()),
            'quantity_range': (df['quantity'].min(), df['quantity'].max())
        }
        
        # Store model
        self.models[product_id] = model
        self.elasticities[product_id] = result
        
        logger.info(
            f"Estimated elasticity for {product_id}: {elasticity:.3f} "
            f"(R²={r_squared:.3f}, p={p_value:.4f})"
        )
        
        return result
    
    def classify_elasticity(self, elasticity: float) -> str:
        """
        Classify product by elasticity.
        
        Args:
            elasticity: Elasticity coefficient
            
        Returns:
            Classification: 'Highly Elastic', 'Elastic', 'Inelastic', 'Highly Inelastic'
        """
        abs_elasticity = abs(elasticity)
        
        if abs_elasticity > 1.5:
            return 'Highly Elastic'
        elif abs_elasticity > 1.0:
            return 'Elastic'
        elif abs_elasticity > 0.5:
            return 'Inelastic'
        else:
            return 'Highly Inelastic'
    
    def predict_quantity(
        self,
        price: float,
        product_id: str
    ) -> float:
        """
        Predict quantity sold at given price.
        
        Args:
            price: Target price
            product_id: Product identifier
            
        Returns:
            Predicted quantity
        """
        model = self.models.get(product_id)
        if not model:
            logger.warning(f"No model found for {product_id}")
            return 0
        
        log_price = np.log(price)
        log_quantity = model.predict([[log_price]])[0]
        quantity = np.exp(log_quantity)
        
        return max(0, quantity)
    
    def estimate_price_impact(
        self,
        current_price: float,
        current_quantity: float,
        new_price: float,
        product_id: str
    ) -> Dict[str, float]:
        """
        Estimate impact of price change on quantity and revenue.
        
        Args:
            current_price: Current price
            current_quantity: Current quantity sold
            new_price: Proposed price
            product_id: Product identifier
            
        Returns:
            Impact metrics (quantity change, revenue change, etc.)
        """
        elasticity_info = self.elasticities.get(product_id)
        if not elasticity_info:
            return {'error': 'No elasticity model for product'}
        
        elasticity = elasticity_info['elasticity']
        
        # Calculate percentage changes
        price_change_pct = (new_price - current_price) / current_price
        quantity_change_pct = elasticity * price_change_pct
        
        # Predict new quantity
        new_quantity = current_quantity * (1 + quantity_change_pct)
        new_quantity = max(0, new_quantity)
        
        # Revenue impact
        current_revenue = current_price * current_quantity
        new_revenue = new_price * new_quantity
        revenue_change = new_revenue - current_revenue
        revenue_change_pct = revenue_change / current_revenue if current_revenue > 0 else 0
        
        return {
            'price_change_pct': price_change_pct * 100,
            'quantity_change_pct': quantity_change_pct * 100,
            'current_revenue': current_revenue,
            'new_revenue': new_revenue,
            'revenue_change': revenue_change,
            'revenue_change_pct': revenue_change_pct * 100,
            'new_quantity': new_quantity,
            'elasticity_coefficient': elasticity
        }
    
    def batch_estimate(self, product_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Estimate elasticity for multiple products.
        
        Args:
            product_data: Dict of {product_id: dataframe}
            
        Returns:
            DataFrame with elasticity estimates
        """
        results = []
        
        for product_id, df in product_data.items():
            elasticity_info = self.estimate_elasticity(df, product_id)
            elasticity_info['product_id'] = product_id
            results.append(elasticity_info)
        
        return pd.DataFrame(results)
    
    def get_elasticity(self, product_id: str) -> Optional[float]:
        """Get elasticity coefficient for product."""
        info = self.elasticities.get(product_id)
        return info['elasticity'] if info else None
    
    def get_all_elasticities(self) -> pd.DataFrame:
        """Get elasticity for all products."""
        if not self.elasticities:
            return pd.DataFrame()
        
        data = []
        for product_id, info in self.elasticities.items():
            row = {'product_id': product_id}
            row.update(info)
            data.append(row)
        
        return pd.DataFrame(data)
