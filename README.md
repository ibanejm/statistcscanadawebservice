# Statistics Canada Web Data Service - Python Client

A Python client library for accessing Statistics Canada's Web Data Service (WDS) API. This library provides a simple and intuitive interface to retrieve public statistical data from Statistics Canada for use in data analysis, machine learning models, and research.

## Features

- **Easy-to-use Python interface** to Statistics Canada's REST API
- **Comprehensive endpoint coverage** including:
  - Browse and search data cubes (tables)
  - Retrieve cube metadata and descriptions
  - Fetch time series data by vector IDs
  - Download data for specific date ranges
  - Track recently updated datasets
  - Download full tables as CSV
- **Error handling** with informative messages
- **Session management** for efficient HTTP connections
- **Type hints** for better IDE support

## Installation

### From source:

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```python
from statcan_webservice import StatCanClient

# Create a client
client = StatCanClient()

# Get list of available data cubes
cubes = client.get_all_cubes_list_lite()
print(f"Found {len(cubes)} data cubes")

# Get metadata for a specific cube (e.g., Consumer Price Index)
metadata = client.get_cube_metadata(18100004)
print(f"Table: {metadata['cubeTitleEn']}")

# Get the latest 10 data points for a vector
vector_id = "v41690973"  # CPI All-items index
data = client.get_data_from_vectors_and_latest_n_periods([vector_id], 10)
for point in data:
    print(f"{point['refPer']}: {point['value']}")

# Close the client when done
client.close()
```

## Usage Examples

### Using as a Context Manager

```python
from statcan_webservice import StatCanClient

with StatCanClient() as client:
    # Get data for a specific date range
    data = client.get_data_from_vector_by_reference_period_range(
        "v41690973",
        "2023-01-01",
        "2023-12-31"
    )
    print(f"Retrieved {len(data)} data points")
```

### Getting Information About a Time Series

```python
client = StatCanClient()

# Get detailed information about a vector
info = client.get_series_info_from_vector("v41690973")
print(f"Title: {info['SeriesTitle']}")
print(f"Frequency: {info['frequencyCode']}")
```

### Fetching Multiple Vectors at Once

```python
client = StatCanClient()

# Get data for multiple vectors
vectors = ["v41690973", "v41690974", "v41690975"]
data = client.get_data_from_vectors_and_latest_n_periods(vectors, 12)

# Data is returned for all vectors
for point in data:
    print(f"Vector {point['vectorId']}: {point['refPer']} = {point['value']}")
```

### Downloading a Complete Table

```python
client = StatCanClient()

# Download a full table as CSV
csv_data = client.get_full_table_download_csv(
    product_id=18100004,
    output_path="cpi_table.csv"
)
print("Table downloaded successfully")
```

### Finding Recently Updated Data

```python
client = StatCanClient()

# Get list of cubes updated on a specific date
changed = client.get_changed_cube_list("2024-01-15")
for cube in changed:
    print(f"Product ID: {cube['productId']}, Released: {cube['releaseTime']}")
```

## API Methods

### Cube Discovery and Metadata

- `get_all_cubes_list()` - Get complete list of all data cubes
- `get_all_cubes_list_lite()` - Get lightweight list of cubes (faster)
- `get_cube_metadata(product_id)` - Get detailed metadata for a cube
- `get_changed_cube_list(date)` - Get cubes updated on a specific date

### Time Series Data

- `get_series_info_from_vector(vector_id)` - Get metadata for a time series
- `get_data_from_vectors_and_latest_n_periods(vector_ids, n_periods)` - Get latest N periods
- `get_data_from_vector_by_reference_period_range(vector_id, start, end)` - Get data for date range
- `get_bulk_vector_data_by_range(vector_ids, start, end)` - Bulk data for multiple vectors
- `get_changed_series_data_from_vector(vector_id, date)` - Get changed data for a vector

### Data Downloads

- `get_full_table_download_csv(product_id, output_path)` - Download complete table as CSV

### Reference Data

- `get_code_sets()` - Get enumeration values and codes used in metadata

## Understanding Statistics Canada Data

### Product IDs and Cubes

Statistics Canada organizes data into **cubes** (also called tables), each identified by a **Product ID**. For example:
- `18100004` - Consumer Price Index (CPI)
- `14100287` - Labour Force Survey
- `36100434` - Gross Domestic Product

### Vector IDs

Within each cube, individual time series are identified by **Vector IDs** (e.g., `v41690973`). Each vector represents a specific data series with its own characteristics (geographic area, measurement type, etc.).

### Reference Periods

Data points are associated with **reference periods** in the format `YYYY-MM-DD`, representing when the data was measured or compiled.

## Rate Limits

The Statistics Canada API has the following rate limits:
- **Server-wide**: 50 requests per second
- **Per IP address**: 25 requests per second

The client handles individual requests but does not automatically throttle. For bulk operations, consider adding delays between requests.

## Examples

Run the included example script to see the client in action:

```bash
python example.py
```

This demonstrates:
- Listing available cubes
- Retrieving cube metadata
- Fetching time series data
- Getting data for specific date ranges
- Finding recently updated datasets

## Use Cases for Machine Learning

This client is ideal for:

1. **Feature Engineering**: Retrieve economic indicators (CPI, GDP, employment) as features for predictive models
2. **Time Series Forecasting**: Access historical data for training forecasting models
3. **Data Enrichment**: Augment datasets with official Canadian statistics
4. **Research**: Conduct empirical studies using reliable government data
5. **Automated Pipelines**: Build data pipelines that automatically fetch updated statistics

## Resources

- [Statistics Canada WDS User Guide](https://www.statcan.gc.ca/en/developers/wds/user-guide)
- [Statistics Canada WDS Homepage](https://www.statcan.gc.ca/en/developers/wds)
- [API Documentation](https://www.statcan.gc.ca/en/developers/wds/user-guide)

## Requirements

- Python 3.7+
- requests >= 2.31.0

## License

This project is provided as-is for accessing public data from Statistics Canada. Please refer to [Statistics Canada's Terms and Conditions](https://www.statcan.gc.ca/en/reference/terms-conditions) for data usage policies.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues related to:
- **This client library**: Open an issue on GitHub
- **Statistics Canada API**: Consult the [official documentation](https://www.statcan.gc.ca/en/developers/wds/user-guide)
- **Data questions**: Contact Statistics Canada through their [official channels](https://www.statcan.gc.ca/en/help/contact)
