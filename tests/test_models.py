"""
Unit tests for ML models module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.models import DemandForecaster, PriceElasticityModel


class TestDemandForecaster:
    """Test cases for DemandForecaster."""
    
    @pytest.fixture
    def sample_forecast_data(self):
        """Create sample time series data."""
        dates = pd.date_range(start='2023-01-01', periods=90, freq='D')
        data = {
            'ds': dates,
            'y': np.random.randint(50, 200, 90) + np.sin(np.arange(90) * 2 * np.pi / 365) * 30
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def forecaster(self):
        """Initialize forecaster for testing."""
        return DemandForecaster(forecast_horizon=30)
    
    def test_train_forecast(self, forecaster, sample_forecast_data):
        """Test model training."""
        model, fitted_data = forecaster.train(sample_forecast_data, 'test_product')
        
        assert model is not None
        assert 'test_product' in forecaster.models
        assert len(fitted_data) == len(sample_forecast_data)
    
    def test_forecast_output(self, forecaster, sample_forecast_data):
        """Test forecast output format."""
        forecast_df = forecaster.forecast(sample_forecast_data, 'test_product')
        
        # Should return 30 forecasts
        assert len(forecast_df) == forecaster.forecast_horizon
        
        # Should have required columns
        assert 'date' in forecast_df.columns
        assert 'predicted_quantity' in forecast_df.columns
        assert 'upper_bound' in forecast_df.columns
        assert 'lower_bound' in forecast_df.columns
        
        # Predictions should be non-negative
        assert (forecast_df['predicted_quantity'] >= 0).all()
    
    def test_forecast_confidence(self, forecaster, sample_forecast_data):
        """Test confidence score calculation."""
        forecast_df = forecaster.forecast(sample_forecast_data, 'test_product')
        forecast_df = forecaster.get_forecast_confidence(forecast_df)
        
        assert 'confidence_score' in forecast_df.columns
        assert 'uncertainty_pct' in forecast_df.columns
        
        # Confidence should be between 0 and 1
        assert (forecast_df['confidence_score'] >= 0).all()
        assert (forecast_df['confidence_score'] <= 1).all()
    
    def test_batch_forecast(self, forecaster, sample_forecast_data):
        """Test batch forecasting for multiple products."""
        product_histories = {
            'product_1': sample_forecast_data,
            'product_2': sample_forecast_data.copy(),
            'product_3': sample_forecast_data.copy()
        }
        
        combined_forecast = forecaster.batch_forecast(product_histories)
        
        # Should have 30 * 3 = 90 forecasts
        assert len(combined_forecast) == 30 * 3


class TestPriceElasticityModel:
    """Test cases for PriceElasticityModel."""
    
    @pytest.fixture
    def sample_price_data(self):
        """Create sample price-quantity data."""
        prices = np.linspace(100, 500, 50)
        elasticity = -1.5
        quantities = 1000 * (prices / 200) ** elasticity + np.random.normal(0, 50, 50)
        
        data = {
            'price': prices,
            'quantity': np.maximum(quantities, 1)  # Ensure positive
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def elasticity_model(self):
        """Initialize elasticity model for testing."""
        return PriceElasticityModel(method='linear')
    
    def test_estimate_elasticity(self, elasticity_model, sample_price_data):
        """Test elasticity estimation."""
        elasticity = elasticity_model.estimate_elasticity(sample_price_data, 'test_product')
        
        # Should return dictionary with required keys
        assert 'elasticity' in elasticity
        assert 'r_squared' in elasticity
        assert 'p_value' in elasticity
        assert 'is_significant' in elasticity
        
        # Elasticity should be negative (normal case)
        assert elasticity['elasticity'] < 0
    
    def test_classify_elasticity(self, elasticity_model):
        """Test elasticity classification."""
        assert elasticity_model.classify_elasticity(-2.0) == 'Highly Elastic'
        assert elasticity_model.classify_elasticity(-1.2) == 'Elastic'
        assert elasticity_model.classify_elasticity(-0.7) == 'Inelastic'
        assert elasticity_model.classify_elasticity(-0.3) == 'Highly Inelastic'
    
    def test_price_impact_estimation(self, elasticity_model, sample_price_data):
        """Test price change impact calculation."""
        elasticity_model.estimate_elasticity(sample_price_data, 'test_product')
        
        impact = elasticity_model.estimate_price_impact(
            current_price=200,
            current_quantity=100,
            new_price=180,
            product_id='test_product'
        )
        
        # Should return impact metrics
        assert 'price_change_pct' in impact
        assert 'quantity_change_pct' in impact
        assert 'revenue_change' in impact
        assert 'revenue_change_pct' in impact
        
        # Price decreased by 10%, so quantity should increase (negative elasticity)
        assert impact['quantity_change_pct'] > 0
    
    def test_batch_estimate(self, elasticity_model):
        """Test batch estimation for multiple products."""
        product_data = {
            'product_1': pd.DataFrame({
                'price': np.linspace(100, 500, 30),
                'quantity': np.random.randint(50, 200, 30)
            }),
            'product_2': pd.DataFrame({
                'price': np.linspace(100, 500, 30),
                'quantity': np.random.randint(50, 200, 30)
            })
        }
        
        results = elasticity_model.batch_estimate(product_data)
        
        assert len(results) == 2
        assert 'product_id' in results.columns
        assert 'elasticity' in results.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
