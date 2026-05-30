# Databricks notebook source
# AI Dynamic Pricing Engine - Data Processing Pipeline
# This notebook loads raw sales data, processes it, and creates Delta tables for analysis

# COMMAND ----------

# Install dependencies
%pip install prophet==1.1.5 scikit-learn==1.3.2

# COMMAND ----------

from pyspark.sql import functions as F
from src.data import OlistDataProcessor, FlipkartDataProcessor
from src.utils import logger, get_config
import pandas as pd

# COMMAND ----------

# Initialize configuration
config = get_config()
logger.info("Initialized configuration")

# COMMAND ----------

# Load Olist dataset
olist_processor = OlistDataProcessor()

# Path to raw Olist CSV (in Azure Blob Storage or Databricks volume)
olist_path = "/Volumes/pricing_engine/raw_data/olist_sales_dataset.csv"

# Process Olist data
print("Processing Olist dataset...")
olist_df = olist_processor.process_olist(olist_path)
olist_df.display()

# COMMAND ----------

# Load Flipkart dataset
flipkart_processor = FlipkartDataProcessor()

flipkart_path = "/Volumes/pricing_engine/raw_data/flipkart_sales_dataset.csv"

print("Processing Flipkart dataset...")
flipkart_df = flipkart_processor.process_flipkart(flipkart_path)
flipkart_df.display()

# COMMAND ----------

# Combine both datasets (add source column)
olist_df_with_source = olist_df.withColumn("source", F.lit("olist"))
flipkart_df_with_source = flipkart_df.withColumn("source", F.lit("flipkart"))

combined_df = olist_df_with_source.union(flipkart_df_with_source)

print(f"Combined dataset: {combined_df.count()} rows")
combined_df.display()

# COMMAND ----------

# Save to Delta table for fast analytics
delta_path = "/Volumes/pricing_engine/delta/sales_data"

combined_df.write.format("delta").mode("overwrite").save(delta_path)
print(f"✓ Saved combined data to Delta: {delta_path}")

# Create table for SQL queries
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS pricing_db.sales_data
    USING DELTA
    LOCATION '{delta_path}'
""")

# COMMAND ----------

# Create aggregated tables for faster queries
daily_sales = combined_df.groupBy("product_id", "date", "source").agg(
    F.sum("total_quantity").alias("quantity"),
    F.sum("revenue").alias("revenue"),
    F.avg("avg_price").alias("avg_price"),
    F.count("*").alias("transaction_count")
).orderBy("product_id", "date")

daily_sales_path = "/Volumes/pricing_engine/delta/daily_sales"
daily_sales.write.format("delta").mode("overwrite").save(daily_sales_path)

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS pricing_db.daily_sales
    USING DELTA
    LOCATION '{daily_sales_path}'
""")

print("✓ Created daily_sales aggregated table")

# COMMAND ----------

# Product summary statistics
product_stats = combined_df.groupBy("product_id").agg(
    F.count("*").alias("transaction_count"),
    F.sum("total_quantity").alias("total_units_sold"),
    F.sum("revenue").alias("total_revenue"),
    F.avg("avg_price").alias("avg_price"),
    F.min("min_price").alias("min_price"),
    F.max("max_price").alias("max_price"),
    F.stddev("avg_price").alias("price_std"),
    F.count(F.col("date")).alias("days_active")
).filter(F.col("total_units_sold") > 10)  # Filter for products with meaningful data

product_stats_path = "/Volumes/pricing_engine/delta/product_stats"
product_stats.write.format("delta").mode("overwrite").save(product_stats_path)

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS pricing_db.product_stats
    USING DELTA
    LOCATION '{product_stats_path}'
""")

print("✓ Created product_stats table")
product_stats.display()

# COMMAND ----------

print("✓ Data processing pipeline completed successfully!")
print(f"  - Total rows processed: {combined_df.count()}")
print(f"  - Unique products: {combined_df.select('product_id').distinct().count()}")
print(f"  - Date range: {combined_df.agg(F.min('date'), F.max('date')).collect()}")
