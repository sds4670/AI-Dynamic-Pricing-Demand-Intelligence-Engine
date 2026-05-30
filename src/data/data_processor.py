"""
Data processing pipeline using PySpark.
Handles data ingestion, cleaning, transformation, and aggregation.
"""

from typing import Optional, List, Tuple
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
from src.utils.logger import logger
from src.utils.config import get_config


class DataProcessor:
    """Process sales data for demand forecasting and elasticity analysis."""
    
    def __init__(self, app_name: str = "pricing-engine"):
        """
        Initialize Spark session.
        
        Args:
            app_name: Spark application name
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        logger.info("Spark session initialized")
    
    def load_csv_to_spark(self, csv_path: str, infer_schema: bool = True) -> DataFrame:
        """
        Load CSV file into Spark DataFrame.
        
        Args:
            csv_path: Path to CSV file
            infer_schema: Whether to infer schema
            
        Returns:
            Spark DataFrame
        """
        df = self.spark.read \
            .option("header", "true") \
            .option("inferSchema", infer_schema) \
            .csv(csv_path)
        
        logger.info(f"Loaded CSV: {csv_path} with {df.count()} rows")
        return df
    
    def load_pandas_to_spark(self, pdf: pd.DataFrame) -> DataFrame:
        """Convert pandas DataFrame to Spark DataFrame."""
        df = self.spark.createDataFrame(pdf)
        logger.info(f"Converted pandas DataFrame with {df.count()} rows to Spark")
        return df
    
    def clean_sales_data(self, df: DataFrame) -> DataFrame:
        """
        Clean and standardize sales data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Remove duplicates
        df = df.dropDuplicates()
        
        # Remove null values in critical columns
        critical_cols = ['product_id', 'price', 'quantity', 'date']
        for col in critical_cols:
            if col in df.columns:
                df = df.filter(F.col(col).isNotNull())
        
        # Standardize column names to lowercase
        df = df.select([F.col(c).alias(c.lower()) for c in df.columns])
        
        # Remove rows with negative quantities or prices
        if 'quantity' in df.columns:
            df = df.filter(F.col('quantity') > 0)
        if 'price' in df.columns:
            df = df.filter(F.col('price') > 0)
        
        logger.info(f"Cleaned data: {df.count()} rows remaining")
        return df
    
    def parse_dates(self, df: DataFrame, date_col: str = 'date') -> DataFrame:
        """
        Parse and convert date columns.
        
        Args:
            df: Input DataFrame
            date_col: Name of date column
            
        Returns:
            DataFrame with parsed dates
        """
        if date_col not in df.columns:
            logger.warning(f"Date column {date_col} not found")
            return df
        
        df = df.withColumn(date_col, F.to_date(date_col, 'yyyy-MM-dd'))
        
        # Extract date features
        df = df.withColumn('year', F.year(F.col(date_col))) \
               .withColumn('month', F.month(F.col(date_col))) \
               .withColumn('day', F.dayofmonth(F.col(date_col))) \
               .withColumn('week', F.weekofyear(F.col(date_col)))
        
        logger.info(f"Parsed dates in column: {date_col}")
        return df
    
    def aggregate_daily_sales(
        self,
        df: DataFrame,
        date_col: str = 'date',
        product_col: str = 'product_id'
    ) -> DataFrame:
        """
        Aggregate sales to daily level per product.
        
        Args:
            df: Input DataFrame with transaction-level data
            date_col: Date column name
            product_col: Product ID column name
            
        Returns:
            Daily aggregated DataFrame
        """
        agg_df = df.groupBy(product_col, date_col).agg(
            F.sum('quantity').alias('total_quantity'),
            F.sum(F.col('price') * F.col('quantity')).alias('revenue'),
            F.avg('price').alias('avg_price'),
            F.min('price').alias('min_price'),
            F.max('price').alias('max_price'),
            F.stddev('price').alias('price_std'),
            F.count('*').alias('transaction_count')
        ).orderBy(product_col, date_col)
        
        logger.info(f"Aggregated to daily sales: {agg_df.count()} records")
        return agg_df
    
    def calculate_elasticity_features(
        self,
        df: DataFrame,
        product_col: str = 'product_id'
    ) -> DataFrame:
        """
        Calculate features for elasticity model.
        
        Args:
            df: Daily aggregated DataFrame
            product_col: Product ID column name
            
        Returns:
            DataFrame with elasticity features
        """
        from pyspark.sql.window import Window
        
        # Window for previous period comparison
        window_spec = Window.partitionBy(product_col).orderBy('date')
        
        df = df.withColumn(
            'quantity_change_pct',
            (F.col('total_quantity') - F.lag('total_quantity').over(window_spec)) / 
            F.lag('total_quantity').over(window_spec)
        ).withColumn(
            'price_change_pct',
            (F.col('avg_price') - F.lag('avg_price').over(window_spec)) / 
            F.lag('avg_price').over(window_spec)
        )
        
        # Calculate elasticity (price sensitivity)
        df = df.withColumn(
            'price_elasticity',
            F.when(
                F.col('price_change_pct') != 0,
                F.col('quantity_change_pct') / F.col('price_change_pct')
            ).otherwise(0)
        )
        
        # Fill nulls with 0
        df = df.fillna(0)
        
        logger.info("Calculated elasticity features")
        return df
    
    def prepare_forecast_data(
        self,
        df: DataFrame,
        product_id: str,
        product_col: str = 'product_id'
    ) -> pd.DataFrame:
        """
        Prepare data for Prophet forecasting.
        
        Args:
            df: Daily aggregated DataFrame
            product_id: Specific product to forecast
            product_col: Product ID column name
            
        Returns:
            Pandas DataFrame ready for Prophet
        """
        product_df = df.filter(F.col(product_col) == product_id) \
                       .select('date', 'total_quantity') \
                       .orderBy('date')
        
        # Convert to pandas
        pdf = product_df.toPandas()
        
        # Rename columns for Prophet
        pdf = pdf.rename(columns={'date': 'ds', 'total_quantity': 'y'})
        
        logger.info(f"Prepared forecast data for product {product_id}: {len(pdf)} records")
        return pdf
    
    def save_to_delta(self, df: DataFrame, table_name: str, mode: str = "overwrite") -> None:
        """
        Save DataFrame to Delta table.
        
        Args:
            df: Spark DataFrame
            table_name: Table name in database
            mode: Save mode (overwrite, append, etc.)
        """
        df.write.format("delta").mode(mode).saveAsTable(table_name)
        logger.info(f"Saved DataFrame to Delta table: {table_name}")
    
    def get_unique_products(self, df: DataFrame, product_col: str = 'product_id') -> List[str]:
        """Get list of unique products in DataFrame."""
        products = df.select(product_col).distinct().collect()
        return [row[0] for row in products]
    
    def stop_spark(self):
        """Stop Spark session."""
        self.spark.stop()
        logger.info("Spark session stopped")


class OlistDataProcessor(DataProcessor):
    """Specialized processor for Olist dataset."""
    
    def process_olist(self, csv_path: str) -> DataFrame:
        """
        Process Olist dataset with expected schema.
        
        Args:
            csv_path: Path to Olist CSV
            
        Returns:
            Processed DataFrame
        """
        df = self.load_csv_to_spark(csv_path)
        
        # Expected columns: date, product_id, price, quantity, etc.
        df = self.clean_sales_data(df)
        df = self.parse_dates(df, 'order_purchase_timestamp')
        
        # Rename to standard schema
        if 'order_purchase_timestamp' in df.columns:
            df = df.withColumnRenamed('order_purchase_timestamp', 'date')
        
        df = self.aggregate_daily_sales(df)
        df = self.calculate_elasticity_features(df)
        
        return df


class FlipkartDataProcessor(DataProcessor):
    """Specialized processor for Flipkart India dataset."""
    
    def process_flipkart(self, csv_path: str) -> DataFrame:
        """
        Process Flipkart dataset with expected schema.
        
        Args:
            csv_path: Path to Flipkart CSV
            
        Returns:
            Processed DataFrame
        """
        df = self.load_csv_to_spark(csv_path)
        df = self.clean_sales_data(df)
        df = self.parse_dates(df, 'date')
        df = self.aggregate_daily_sales(df)
        df = self.calculate_elasticity_features(df)
        
        return df
