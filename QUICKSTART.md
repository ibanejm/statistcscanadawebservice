# Quick Start Guide - Statistics Canada Web Service

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Basic Usage

### Import the client
```python
from statcan_webservice import StatCanClient
```

### Create a client
```python
# Simple initialization
client = StatCanClient()

# With custom timeout
client = StatCanClient(timeout=60)

# Using context manager (recommended)
with StatCanClient() as client:
    # Use client here
    pass
```

## Common Use Cases

### 1. Browse Available Data

```python
# Get all available data tables (lightweight)
cubes = client.get_all_cubes_list_lite()
for cube in cubes[:5]:
    print(f"{cube['productId']}: {cube['cubeTitleEn']}")
```

### 2. Get Table Metadata

```python
# Get detailed information about a table
metadata = client.get_cube_metadata(18100004)  # CPI table
print(f"Title: {metadata['cubeTitleEn']}")
print(f"Date range: {metadata['cubeStartDate']} to {metadata['cubeEndDate']}")
```

### 3. Get Time Series Data

```python
# Get latest 12 months of CPI data
vector_id = "v41690973"  # CPI All-items
data = client.get_data_from_vectors_and_latest_n_periods([vector_id], 12)

for point in data:
    print(f"{point['refPer']}: {point['value']}")
```

### 4. Get Data for Date Range

```python
# Get data for a specific period
data = client.get_data_from_vector_by_reference_period_range(
    "v41690973",
    "2023-01-01",
    "2023-12-31"
)
```

### 5. Get Multiple Indicators at Once

```python
# Get data for multiple economic indicators
vectors = [
    "v41690973",  # CPI All-items
    "v2062815",   # Unemployment rate
    "v65201210"   # GDP
]
data = client.get_data_from_vectors_and_latest_n_periods(vectors, 10)
```

### 6. Download Complete Table

```python
# Download full table as CSV
csv_data = client.get_full_table_download_csv(
    product_id=18100004,
    output_path="cpi_data.csv"
)
```

### 7. Track Recent Updates

```python
# Find tables updated on a specific date
changed = client.get_changed_cube_list("2024-01-15")
for cube in changed:
    print(f"Product {cube['productId']} updated at {cube['releaseTime']}")
```

## Common Vector IDs

Here are some commonly used vector IDs for Canadian economic indicators:

| Indicator | Vector ID | Description |
|-----------|-----------|-------------|
| CPI All Items | v41690973 | Consumer Price Index - All items |
| Unemployment Rate | v2062815 | Unemployment rate, Canada |
| GDP | v65201210 | Gross Domestic Product at market prices |
| Housing Starts | v735 | Housing starts, total units |
| Retail Sales | v52367133 | Retail trade sales |

## For Machine Learning

### Feature Engineering Example

```python
# Fetch economic indicators
indicators = {
    'cpi': 'v41690973',
    'unemployment': 'v2062815',
    'gdp': 'v65201210'
}

features = {}
for name, vector_id in indicators.items():
    data = client.get_data_from_vector_by_reference_period_range(
        vector_id,
        "2020-01-01",
        "2023-12-31"
    )
    features[name] = [point['value'] for point in data]

# Now convert to pandas DataFrame for ML
import pandas as pd
df = pd.DataFrame(features)

# Add lag features
df['cpi_lag1'] = df['cpi'].shift(1)
df['cpi_growth'] = df['cpi'].pct_change()

# Use in your model
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
# ... train your model
```

## Error Handling

```python
try:
    data = client.get_cube_metadata(18100004)
except requests.RequestException as e:
    print(f"Network error: {e}")
except ValueError as e:
    print(f"API error: {e}")
```

## Rate Limits

- Server-wide: 50 requests/second
- Per IP: 25 requests/second

For bulk operations, add delays:
```python
import time

for vector_id in vector_ids:
    data = client.get_series_info_from_vector(vector_id)
    time.sleep(0.05)  # 20 requests/second
```

## Resources

- Run `python example.py` - Basic usage examples
- Run `python example_ml_features.py` - ML pipeline example
- [Statistics Canada API Docs](https://www.statcan.gc.ca/en/developers/wds/user-guide)

## Tips

1. **Use context manager**: Always use `with StatCanClient() as client:` for automatic cleanup
2. **Cache metadata**: Cube metadata doesn't change often, cache it locally
3. **Batch requests**: Use bulk methods when fetching multiple vectors
4. **Handle dates carefully**: API expects YYYY-MM-DD format
5. **Check data frequency**: Some series are monthly, others quarterly or annual

## Need Help?

- Check the full README.md for detailed documentation
- View the example scripts for working code
- Consult Statistics Canada's official documentation
