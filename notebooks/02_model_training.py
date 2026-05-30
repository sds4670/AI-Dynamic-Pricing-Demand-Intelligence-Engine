# Databricks notebook source
# AI Dynamic Pricing Engine - Model Training & Evaluation
# Trains forecasting and elasticity models on processed data

# COMMAND ----------

from src.models import DemandForecaster, PriceElasticityModel
from src.data import DataProcessor
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# COMMAND ----------

# Load processed data from Delta table
daily_sales_df = spark.table("pricing_db.daily_sales").toPandas()

print(f"Loaded {len(daily_sales_df)} records from daily_sales table")
print(daily_sales_df.head())

# COMMAND ----------

# Get unique products
products = daily_sales_df['product_id'].unique()
print(f"Total products: {len(products)}")

# COMMAND ----------

# Initialize forecaster
forecaster = DemandForecaster(forecast_horizon=30)

# Train forecasts for all products
forecasts = {}
for product_id in products[:10]:  # Sample 10 products for demo
    try:
        product_data = daily_sales_df[daily_sales_df['product_id'] == product_id].copy()
        product_data = product_data[['date', 'quantity']].rename(
            columns={'date': 'ds', 'quantity': 'y'}
        ).sort_values('ds')
        
        if len(product_data) >= 14:
            forecast_df = forecaster.forecast(product_data, product_id)
            forecasts[product_id] = forecast_df
            
            print(f"✓ Trained forecaster for {product_id}: {len(product_data)} historical records")
        else:
            print(f"⚠ Skipped {product_id}: insufficient data ({len(product_data)} records)")
    except Exception as e:
        print(f"✗ Error training {product_id}: {str(e)}")

# COMMAND ----------

# Save forecasts to Delta table
forecast_results = []
for product_id, forecast_df in forecasts.items():
    forecast_results.append(forecast_df)

combined_forecasts = pd.concat(forecast_results, ignore_index=True)
forecast_spark_df = spark.createDataFrame(combined_forecasts)

forecast_spark_df.write.format("delta").mode("overwrite").saveAsTable(
    "pricing_db.demand_forecasts"
)

print(f"✓ Saved forecasts for {len(forecasts)} products to Delta table")
forecast_spark_df.display()

# COMMAND ----------

# Initialize elasticity model
elasticity_model = PriceElasticityModel(method='linear')

# Train elasticity models
elasticity_results = {}
for product_id in products[:10]:
    try:
        product_data = daily_sales_df[daily_sales_df['product_id'] == product_id][
            ['price', 'quantity']
        ]
        
        if len(product_data) >= 10:
            elasticity = elasticity_model.estimate_elasticity(product_data, product_id)
            elasticity_results[product_id] = elasticity
            
            classification = elasticity_model.classify_elasticity(elasticity['elasticity'])
            print(f"✓ {product_id}: elasticity={elasticity['elasticity']:.3f} ({classification})")
        else:
            print(f"⚠ Skipped {product_id}: insufficient price variations")
    except Exception as e:
        print(f"✗ Error training {product_id}: {str(e)}")

# COMMAND ----------

# Save elasticity estimates to Delta table
elasticity_df = elasticity_model.get_all_elasticities()
elasticity_spark_df = spark.createDataFrame(elasticity_df)

elasticity_spark_df.write.format("delta").mode("overwrite").saveAsTable(
    "pricing_db.price_elasticity"
)

print(f"✓ Saved elasticity estimates for {len(elasticity_results)} products")
elasticity_spark_df.display()

# COMMAND ----------

# Model Performance Summary
print("=" * 60)
print("MODEL TRAINING SUMMARY")
print("=" * 60)
print(f"Demand Forecasting Models: {len(forecasts)} products")
print(f"Price Elasticity Models: {len(elasticity_results)} products")
print()
print("Elasticity Distribution:")
elasticity_df = elasticity_model.get_all_elasticities()
print(elasticity_df[['product_id', 'elasticity', 'r_squared', 'confidence']].describe())
print()
print("✓ Model training pipeline completed successfully!")
