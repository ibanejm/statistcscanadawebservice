"""
Example usage of the Statistics Canada Web Data Service client.

This script demonstrates how to use the client to retrieve data from
Statistics Canada's API.
"""

from statcan_webservice import StatCanClient


def main():
    # Create a client instance
    client = StatCanClient()
    
    print("=" * 60)
    print("Statistics Canada Web Data Service - Example Usage")
    print("=" * 60)
    
    # Example 1: Get list of available cubes (first 5)
    print("\n1. Getting first 5 available data cubes...")
    try:
        cubes = client.get_all_cubes_list_lite()
        for cube in cubes[:5]:
            print(f"   - Product ID: {cube.get('productId')}")
            print(f"     Title (EN): {cube.get('cubeTitleEn', 'N/A')[:60]}...")
            print()
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Get metadata for a specific cube
    print("\n2. Getting metadata for a specific cube (e.g., 18100004)...")
    try:
        # Using a common table: Consumer Price Index
        product_id = 18100004
        metadata = client.get_cube_metadata(product_id)
        print(f"   Title: {metadata.get('cubeTitleEn', 'N/A')}")
        print(f"   Start: {metadata.get('cubeStartDate', 'N/A')}")
        print(f"   End: {metadata.get('cubeEndDate', 'N/A')}")
        print(f"   Frequency: {metadata.get('frequencyCode', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Get information about a specific vector
    print("\n3. Getting series information for a vector...")
    try:
        # Example vector ID (Consumer Price Index - All items)
        vector_id = "v41690973"
        info = client.get_series_info_from_vector(vector_id)
        if info:
            print(f"   Vector: {vector_id}")
            print(f"   Title: {info.get('SeriesTitle', 'N/A')[:60]}...")
            print(f"   Product ID: {info.get('productId', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 4: Get latest data points for vectors
    print("\n4. Getting latest 5 data points for a vector...")
    try:
        vector_ids = ["v41690973"]  # CPI All items
        data = client.get_data_from_vectors_and_latest_n_periods(vector_ids, 5)
        
        if data:
            for point in data[:5]:
                ref_period = point.get('refPer', 'N/A')
                value = point.get('value', 'N/A')
                print(f"   {ref_period}: {value}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 5: Get data for a specific date range
    print("\n5. Getting data for a specific date range...")
    try:
        vector_id = "v41690973"
        start_date = "2023-01-01"
        end_date = "2023-06-30"
        data = client.get_data_from_vector_by_reference_period_range(
            vector_id, 
            start_date, 
            end_date
        )
        
        print(f"   Retrieved {len(data)} data points from {start_date} to {end_date}")
        if data:
            print(f"   First point: {data[0].get('refPer')} = {data[0].get('value')}")
            print(f"   Last point: {data[-1].get('refPer')} = {data[-1].get('value')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 6: Get changed cubes for a recent date
    print("\n6. Getting recently changed cubes...")
    try:
        # Use a recent date (you may want to adjust this)
        date = "2024-01-15"
        changed = client.get_changed_cube_list(date)
        print(f"   Found {len(changed)} changed cubes on {date}")
        if changed:
            for cube in changed[:3]:
                print(f"   - Product ID: {cube.get('productId')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    # Close the client
    client.close()


if __name__ == "__main__":
    main()
