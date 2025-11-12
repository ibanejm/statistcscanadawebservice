"""
Example: Using Statistics Canada data for machine learning feature engineering.

This example demonstrates how to retrieve economic indicators from Statistics Canada
and prepare them as features for a predictive model.
"""

from statcan_webservice import StatCanClient
import json
from datetime import datetime


def fetch_economic_indicators_as_features(start_date, end_date):
    """
    Fetch key Canadian economic indicators for use as ML features.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Dictionary of time series data suitable for ML feature engineering
    """
    
    # Initialize client
    client = StatCanClient()
    
    # Define key economic indicators (vector IDs)
    indicators = {
        'cpi_all_items': 'v41690973',           # Consumer Price Index - All items
        'unemployment_rate': 'v2062815',        # Unemployment rate
        'gdp': 'v65201210',                     # GDP at market prices
        'housing_starts': 'v735',               # Housing starts
        'retail_sales': 'v52367133',            # Retail trade sales
    }
    
    features = {}
    
    print("Fetching economic indicators from Statistics Canada...")
    print(f"Date range: {start_date} to {end_date}\n")
    
    for name, vector_id in indicators.items():
        try:
            print(f"Fetching {name} (vector: {vector_id})...")
            
            # Get series info first
            info = client.get_series_info_from_vector(vector_id)
            
            # Get data for the specified range
            data = client.get_data_from_vector_by_reference_period_range(
                vector_id,
                start_date,
                end_date
            )
            
            # Process data into feature format
            features[name] = {
                'description': info.get('SeriesTitle', 'N/A'),
                'frequency': info.get('frequencyCode', 'N/A'),
                'unit': info.get('scalarFactorDescEn', 'N/A'),
                'data_points': [
                    {
                        'date': point.get('refPer'),
                        'value': point.get('value')
                    }
                    for point in data
                ]
            }
            
            print(f"  ✓ Retrieved {len(data)} data points")
            
        except Exception as e:
            print(f"  ✗ Error fetching {name}: {str(e)[:80]}")
            features[name] = None
    
    client.close()
    return features


def prepare_feature_matrix(features_dict):
    """
    Convert time series features into a feature matrix suitable for ML models.
    
    Args:
        features_dict: Dictionary of features from fetch_economic_indicators_as_features
        
    Returns:
        Dictionary with aligned feature matrix (suitable for pandas DataFrame)
    """
    
    # In a real implementation, you would:
    # 1. Align all time series to common dates
    # 2. Handle missing values (interpolation, forward fill, etc.)
    # 3. Calculate derived features (moving averages, growth rates, etc.)
    # 4. Normalize/standardize values
    # 5. Create lag features for time series forecasting
    
    print("\nProcessing features for ML model...")
    print("This would typically include:")
    print("  - Aligning time series to common dates")
    print("  - Handling missing values")
    print("  - Creating lag features")
    print("  - Computing growth rates and moving averages")
    print("  - Normalizing/standardizing values")
    
    # Example structure (in practice, use pandas for this)
    feature_matrix = {}
    
    for name, feature_data in features_dict.items():
        if feature_data and feature_data.get('data_points'):
            # Extract just the values for simplicity
            values = [dp['value'] for dp in feature_data['data_points']]
            dates = [dp['date'] for dp in feature_data['data_points']]
            
            feature_matrix[name] = values
            if 'dates' not in feature_matrix:
                feature_matrix['dates'] = dates
    
    return feature_matrix


def example_ml_pipeline():
    """
    Demonstrate a complete ML pipeline using Statistics Canada data.
    """
    
    print("=" * 70)
    print("Machine Learning Pipeline Example: Economic Indicator Features")
    print("=" * 70)
    
    # Step 1: Fetch raw data from Statistics Canada
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    features = fetch_economic_indicators_as_features(start_date, end_date)
    
    # Step 2: Prepare feature matrix
    feature_matrix = prepare_feature_matrix(features)
    
    # Step 3: Example of what you could do next
    print("\n" + "=" * 70)
    print("Next Steps for Your ML Model:")
    print("=" * 70)
    print("""
1. Convert to pandas DataFrame:
   import pandas as pd
   df = pd.DataFrame(feature_matrix)
   
2. Handle missing values:
   df = df.fillna(method='ffill')  # Forward fill
   
3. Create lag features:
   for col in ['cpi_all_items', 'unemployment_rate']:
       df[f'{col}_lag1'] = df[col].shift(1)
       df[f'{col}_lag3'] = df[col].shift(3)
   
4. Calculate growth rates:
   df['cpi_growth'] = df['cpi_all_items'].pct_change()
   
5. Split into train/test:
   from sklearn.model_selection import train_test_split
   X_train, X_test, y_train, y_test = train_test_split(...)
   
6. Train your model:
   from sklearn.ensemble import RandomForestRegressor
   model = RandomForestRegressor()
   model.fit(X_train, y_train)
   
7. Make predictions:
   predictions = model.predict(X_test)
    """)
    
    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    example_ml_pipeline()
