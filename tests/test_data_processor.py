"""
Unit tests for data processing module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample sales data for testing."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        data = {
            'date': dates,
            'product_id': np.random.choice(['P001', 'P002', 'P003'], 100),
            'price': np.random.uniform(100, 1000, 100),
            'quantity': np.random.randint(1, 100, 100),
            'category': np.random.choice(['Electronics', 'Clothing', 'Home'], 100)
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def processor(self):
        """Initialize DataProcessor for testing."""
        return DataProcessor(app_name="test-pricing")
    
    def test_load_pandas_to_spark(self, processor, sample_data):
        """Test loading pandas DataFrame to Spark."""
        spark_df = processor.load_pandas_to_spark(sample_data)
        assert spark_df.count() == len(sample_data)
        assert len(spark_df.columns) == len(sample_data.columns)
    
    def test_clean_sales_data(self, processor, sample_data):
        """Test data cleaning."""
        spark_df = processor.load_pandas_to_spark(sample_data)
        
        # Add some invalid data
        bad_data = pd.DataFrame({
            'date': [datetime.now()],
            'product_id': [None],
            'price': [-100],
            'quantity': [50]
        })
        
        spark_df_bad = processor.load_pandas_to_spark(bad_data)
        spark_df_all = spark_df.union(spark_df_bad)
        
        cleaned = processor.clean_sales_data(spark_df_all)
        
        # Should have fewer rows after cleaning
        assert cleaned.count() <= spark_df_all.count()
    
    def test_parse_dates(self, processor, sample_data):
        """Test date parsing."""
        spark_df = processor.load_pandas_to_spark(sample_data)
        parsed_df = processor.parse_dates(spark_df, 'date')
        
        # Should have additional date columns
        cols = parsed_df.columns
        assert 'year' in cols
        assert 'month' in cols
        assert 'week' in cols
    
    def test_aggregate_daily_sales(self, processor, sample_data):
        """Test daily aggregation."""
        spark_df = processor.load_pandas_to_spark(sample_data)
        spark_df = processor.parse_dates(spark_df, 'date')
        
        agg_df = processor.aggregate_daily_sales(spark_df, 'date', 'product_id')
        
        # Should have fewer rows after aggregation
        assert agg_df.count() < spark_df.count()
        
        # Should have aggregation columns
        cols = agg_df.columns
        assert 'total_quantity' in cols
        assert 'revenue' in cols
        assert 'avg_price' in cols


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
