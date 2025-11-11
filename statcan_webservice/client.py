"""
Statistics Canada Web Data Service API Client

This module provides a comprehensive Python client for interacting with 
Statistics Canada's Web Data Service (WDS) REST API.
"""

import requests
from typing import List, Dict, Any, Optional
import time


class StatCanClient:
    """
    A client for interacting with Statistics Canada's Web Data Service API.
    
    The API provides access to Canadian statistical data and metadata through
    RESTful endpoints. This client handles request formatting, error checking,
    and response parsing.
    
    Base URL: https://www150.statcan.gc.ca/t1/wds/rest
    
    Rate Limits:
    - Server-wide: 50 requests/second
    - Per-IP: 25 requests/second
    """
    
    BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the Statistics Canada API client.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a request to the Statistics Canada API.
        
        Args:
            endpoint: The API endpoint path (without base URL)
            
        Returns:
            Parsed JSON response
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the API returns an error status
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check API status in response
            if data.get("status") == "ERROR":
                raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")
                
            return data
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch data from {url}: {str(e)}")
    
    def get_all_cubes_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available data cubes (tables).
        
        Returns:
            List of cube metadata dictionaries containing product IDs and descriptions
            
        Example:
            >>> client = StatCanClient()
            >>> cubes = client.get_all_cubes_list()
            >>> print(cubes[0]['productId'])
        """
        response = self._make_request("getAllCubesList")
        return response.get("object", [])
    
    def get_all_cubes_list_lite(self) -> List[Dict[str, Any]]:
        """
        Get a lightweight list of all available data cubes.
        
        Returns fewer details than get_all_cubes_list() for faster performance.
        
        Returns:
            Lightweight list of cube metadata
        """
        response = self._make_request("getAllCubesListLite")
        return response.get("object", [])
    
    def get_cube_metadata(self, product_id: int) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific data cube.
        
        Args:
            product_id: The product ID of the cube (e.g., 35100157)
            
        Returns:
            Cube metadata including dimensions, members, and descriptions
            
        Example:
            >>> client = StatCanClient()
            >>> metadata = client.get_cube_metadata(35100157)
            >>> print(metadata['cubeTitleEn'])
        """
        response = self._make_request(f"getCubeMetadata/{product_id}")
        return response.get("object", {})
    
    def get_changed_cube_list(self, date: str) -> List[Dict[str, Any]]:
        """
        Get list of cubes that have been updated on a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (e.g., "2023-12-01")
            
        Returns:
            List of changed cubes with product IDs and release times
            
        Example:
            >>> client = StatCanClient()
            >>> changes = client.get_changed_cube_list("2023-12-01")
        """
        response = self._make_request(f"getChangedCubeList/{date}")
        return response.get("object", [])
    
    def get_series_info_from_vector(self, vector_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific time series using its vector ID.
        
        Args:
            vector_id: Vector identifier (e.g., "v41690973")
            
        Returns:
            Series metadata including description, frequency, and dimensions
            
        Example:
            >>> client = StatCanClient()
            >>> info = client.get_series_info_from_vector("v41690973")
            >>> print(info['SeriesTitle'])
        """
        response = self._make_request(f"getSeriesInfoFromVector/{vector_id}")
        return response.get("object", {})
    
    def get_data_from_vectors_and_latest_n_periods(
        self, 
        vector_ids: List[str], 
        n_periods: int
    ) -> List[Dict[str, Any]]:
        """
        Get the latest N periods of data for one or more time series.
        
        Args:
            vector_ids: List of vector IDs to fetch data for
            n_periods: Number of most recent periods to retrieve
            
        Returns:
            List of data points for each vector
            
        Example:
            >>> client = StatCanClient()
            >>> data = client.get_data_from_vectors_and_latest_n_periods(
            ...     ["v41690973", "v41690974"], 
            ...     10
            ... )
        """
        vectors_param = ",".join(vector_ids)
        endpoint = f"getDataFromVectorsAndLatestNPeriods/{vectors_param}/{n_periods}"
        response = self._make_request(endpoint)
        return response.get("object", [])
    
    def get_data_from_vector_by_reference_period_range(
        self,
        vector_id: str,
        start_period: str,
        end_period: str
    ) -> List[Dict[str, Any]]:
        """
        Get data for a vector within a specific reference period range.
        
        Args:
            vector_id: Vector identifier
            start_period: Start date in YYYY-MM-DD format
            end_period: End date in YYYY-MM-DD format
            
        Returns:
            List of data points within the specified period
            
        Example:
            >>> client = StatCanClient()
            >>> data = client.get_data_from_vector_by_reference_period_range(
            ...     "v41690973",
            ...     "2020-01-01",
            ...     "2023-12-31"
            ... )
        """
        endpoint = f"getDataFromVectorByReferencePeriodRange/{vector_id}/{start_period}/{end_period}"
        response = self._make_request(endpoint)
        return response.get("object", [])
    
    def get_bulk_vector_data_by_range(
        self,
        vector_ids: List[str],
        start_period: str,
        end_period: str
    ) -> List[Dict[str, Any]]:
        """
        Get bulk data for multiple vectors within a period range.
        
        Args:
            vector_ids: List of vector IDs
            start_period: Start date in YYYY-MM-DD format
            end_period: End date in YYYY-MM-DD format
            
        Returns:
            Bulk data for all specified vectors
            
        Example:
            >>> client = StatCanClient()
            >>> data = client.get_bulk_vector_data_by_range(
            ...     ["v41690973", "v41690974"],
            ...     "2020-01-01",
            ...     "2023-12-31"
            ... )
        """
        vectors_param = ",".join(vector_ids)
        endpoint = f"getBulkVectorDataByRange/{vectors_param}/{start_period}/{end_period}"
        response = self._make_request(endpoint)
        return response.get("object", [])
    
    def get_changed_series_data_from_vector(
        self,
        vector_id: str,
        date: str
    ) -> List[Dict[str, Any]]:
        """
        Get changed data for a specific vector on a given date.
        
        Args:
            vector_id: Vector identifier
            date: Date in YYYY-MM-DD format
            
        Returns:
            Changed data points for the vector
        """
        endpoint = f"getChangedSeriesDataFromVector/{vector_id}/{date}"
        response = self._make_request(endpoint)
        return response.get("object", [])
    
    def get_code_sets(self) -> List[Dict[str, Any]]:
        """
        Get enumeration values (code sets) used in tables and metadata.
        
        Returns:
            List of code sets and their values
            
        Example:
            >>> client = StatCanClient()
            >>> codes = client.get_code_sets()
        """
        response = self._make_request("getCodeSets")
        return response.get("object", [])
    
    def get_full_table_download_csv(
        self,
        product_id: int,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Download the entire table as CSV.
        
        Args:
            product_id: The product ID of the cube
            output_path: Optional path to save the CSV file
            
        Returns:
            CSV data as bytes
            
        Example:
            >>> client = StatCanClient()
            >>> csv_data = client.get_full_table_download_csv(35100157, "table.csv")
        """
        url = f"{self.BASE_URL}/getFullTableDownloadCSV/{product_id}"
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(response.content)
        
        return response.content
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
