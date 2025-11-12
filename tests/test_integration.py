"""
Integration test example - demonstrates how to use the client.

Note: This test requires network access to the Statistics Canada API.
It is provided as an example and may fail in restricted environments.
"""

from statcan_webservice import StatCanClient


def test_integration():
    """Test basic integration with Statistics Canada API."""
    
    print("Testing Statistics Canada Web Service Client Integration")
    print("-" * 60)
    
    # Create client using context manager
    with StatCanClient(timeout=30) as client:
        
        # Test 1: Try to get a list of cubes
        print("\n1. Testing get_all_cubes_list_lite()...")
        try:
            cubes = client.get_all_cubes_list_lite()
            if cubes:
                print(f"   ✓ Successfully retrieved {len(cubes)} cubes")
                print(f"   Example cube: {cubes[0].get('productId')}")
            else:
                print("   ! No cubes returned")
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
        
        # Test 2: Try to get metadata for a known cube (CPI)
        print("\n2. Testing get_cube_metadata(18100004)...")
        try:
            metadata = client.get_cube_metadata(18100004)
            if metadata:
                print(f"   ✓ Retrieved metadata for: {metadata.get('cubeTitleEn', 'N/A')[:50]}")
            else:
                print("   ! No metadata returned")
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
        
        # Test 3: Try to get vector info
        print("\n3. Testing get_series_info_from_vector('v41690973')...")
        try:
            info = client.get_series_info_from_vector("v41690973")
            if info:
                print(f"   ✓ Retrieved series info")
            else:
                print("   ! No info returned")
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
        
        # Test 4: Try to get latest data
        print("\n4. Testing get_data_from_vectors_and_latest_n_periods()...")
        try:
            data = client.get_data_from_vectors_and_latest_n_periods(
                ["v41690973"], 
                5
            )
            if data:
                print(f"   ✓ Retrieved {len(data)} data points")
            else:
                print("   ! No data returned")
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
    
    print("\n" + "-" * 60)
    print("Integration test completed!")


if __name__ == "__main__":
    test_integration()
