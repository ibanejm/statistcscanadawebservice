"""
Statistics Canada Web Data Service API Client

This module provides a comprehensive Python client for interacting with 
Statistics Canada's Web Data Service (WDS) REST API.
"""

import requests
from typing import List, Dict, Any, Optional, Union
import time
import logging
from datetime import datetime


# Set up logging
logger = logging.getLogger(__name__)


class StatCanAPIError(Exception):
    """Custom exception for Statistics Canada API errors."""
    pass


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
    
    Example:
        >>> with StatCanClient() as client:
        ...     cubes = client.get_all_cubes_list()
        ...     metadata = client.get_cube_metadata(35100157)
    """
    
    BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the Statistics Canada API client.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StatCanClient/1.0 (Python)'
        })
        
    def _make_request(self, endpoint: str, retry_count: int = 0) -> Dict[str, Any]:
        """
        Make a request to the Statistics Canada API with retry logic.
        
        Args:
            endpoint: The API endpoint path (without base URL)
            retry_count: Current retry attempt number
            
        Returns:
            Parsed JSON response
            
        Raises:
            StatCanAPIError: If the API returns an error status
            requests.RequestException: If the request fails after all retries
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check API status in response
            if isinstance(data, dict) and data.get("status") == "ERROR":
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"API Error: {error_msg}")
                raise StatCanAPIError(f"API Error: {error_msg}")
                
            return data
            
        except requests.exceptions.Timeout as e:
            logger.warning(f"Request timeout for {url}: {str(e)}")
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay * (retry_count + 1))
                return self._make_request(endpoint, retry_count + 1)
            raise
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and retry_count < self.max_retries:
                # Rate limit hit, wait longer before retry
                logger.warning(f"Rate limit hit, retrying after delay...")
                time.sleep(self.retry_delay * (retry_count + 1) * 2)
                return self._make_request(endpoint, retry_count + 1)
            raise
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay * (retry_count + 1))
                return self._make_request(endpoint, retry_count + 1)
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
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_all_cubes_list_lite(self) -> List[Dict[str, Any]]:
        """
        Get a lightweight list of all available data cubes.
        
        Returns fewer details than get_all_cubes_list() for faster performance.
        
        Returns:
            Lightweight list of cube metadata
        """
        response = self._make_request("getAllCubesListLite")
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_cube_metadata(self, product_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific data cube.
        
        Args:
            product_id: The product ID of the cube (e.g., 35100157 or "35100157")
            
        Returns:
            Cube metadata including dimensions, members, and descriptions
            
        Example:
            >>> client = StatCanClient()
            >>> metadata = client.get_cube_metadata(35100157)
            >>> print(metadata['cubeTitleEn'])
        """
        response = self._make_request(f"getCubeMetadata/{product_id}")
        return response.get("object", {}) if isinstance(response, dict) else {}
    
    def get_changed_cube_list(self, date: Union[str, datetime]) -> List[Dict[str, Any]]:
        """
        Get list of cubes that have been updated on a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (e.g., "2023-12-01") or datetime object
            
        Returns:
            List of changed cubes with product IDs and release times
            
        Example:
            >>> client = StatCanClient()
            >>> changes = client.get_changed_cube_list("2023-12-01")
        """
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        
        response = self._make_request(f"getChangedCubeList/{date}")
        return response.get("object", []) if isinstance(response, dict) else []
    
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
            >>> print(info.get('SeriesTitle'))
        """
        # Ensure vector_id has 'v' prefix
        if not vector_id.lower().startswith('v'):
            vector_id = f"v{vector_id}"
            
        response = self._make_request(f"getSeriesInfoFromVector/{vector_id}")
        return response.get("object", {}) if isinstance(response, dict) else {}
    
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
        if not vector_ids:
            raise ValueError("vector_ids cannot be empty")
        
        if n_periods <= 0:
            raise ValueError("n_periods must be positive")
        
        # Ensure all vector IDs have 'v' prefix
        vector_ids = [v if v.lower().startswith('v') else f"v{v}" for v in vector_ids]
        
        vectors_param = ",".join(vector_ids)
        endpoint = f"getDataFromVectorsAndLatestNPeriods/{vectors_param}/{n_periods}"
        response = self._make_request(endpoint)
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_data_from_vector_by_reference_period_range(
        self,
        vector_id: str,
        start_period: Union[str, datetime],
        end_period: Union[str, datetime]
    ) -> List[Dict[str, Any]]:
        """
        Get data for a vector within a specific reference period range.
        
        Args:
            vector_id: Vector identifier
            start_period: Start date in YYYY-MM-DD format or datetime object
            end_period: End date in YYYY-MM-DD format or datetime object
            
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
        # Ensure vector_id has 'v' prefix
        if not vector_id.lower().startswith('v'):
            vector_id = f"v{vector_id}"
        
        # Convert datetime to string if needed
        if isinstance(start_period, datetime):
            start_period = start_period.strftime("%Y-%m-%d")
        if isinstance(end_period, datetime):
            end_period = end_period.strftime("%Y-%m-%d")
            
        endpoint = f"getDataFromVectorByReferencePeriodRange/{vector_id}/{start_period}/{end_period}"
        response = self._make_request(endpoint)
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_bulk_vector_data_by_range(
        self,
        vector_ids: List[str],
        start_period: Union[str, datetime],
        end_period: Union[str, datetime]
    ) -> List[Dict[str, Any]]:
        """
        Get bulk data for multiple vectors within a period range.
        
        Args:
            vector_ids: List of vector IDs
            start_period: Start date in YYYY-MM-DD format or datetime object
            end_period: End date in YYYY-MM-DD format or datetime object
            
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
        if not vector_ids:
            raise ValueError("vector_ids cannot be empty")
        
        # Ensure all vector IDs have 'v' prefix
        vector_ids = [v if v.lower().startswith('v') else f"v{v}" for v in vector_ids]
        
        # Convert datetime to string if needed
        if isinstance(start_period, datetime):
            start_period = start_period.strftime("%Y-%m-%d")
        if isinstance(end_period, datetime):
            end_period = end_period.strftime("%Y-%m-%d")
        
        vectors_param = ",".join(vector_ids)
        endpoint = f"getBulkVectorDataByRange/{vectors_param}/{start_period}/{end_period}"
        response = self._make_request(endpoint)
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_changed_series_data_from_vector(
        self,
        vector_id: str,
        date: Union[str, datetime]
    ) -> List[Dict[str, Any]]:
        """
        Get changed data for a specific vector on a given date.
        
        Args:
            vector_id: Vector identifier
            date: Date in YYYY-MM-DD format or datetime object
            
        Returns:
            Changed data points for the vector
        """
        # Ensure vector_id has 'v' prefix
        if not vector_id.lower().startswith('v'):
            vector_id = f"v{vector_id}"
        
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
            
        endpoint = f"getChangedSeriesDataFromVector/{vector_id}/{date}"
        response = self._make_request(endpoint)
        return response.get("object", []) if isinstance(response, dict) else []
    
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
        return response.get("object", []) if isinstance(response, dict) else []
    
    def get_full_table_download_csv(
        self,
        product_id: Union[int, str],
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
        
        logger.debug(f"Downloading full table CSV from: {url}")
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Table saved to: {output_path}")
        
        return response.content
    
    def search_cubes_by_keyword(self, keyword: str, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Search for cubes containing a specific keyword in their title or description.
        
        Args:
            keyword: Search term to look for
            language: Language code ('en' or 'fr')
            
        Returns:
            List of matching cubes
            
        Example:
            >>> client = StatCanClient()
            >>> income_cubes = client.search_cubes_by_keyword("income")
        """
        cubes = self.get_all_cubes_list()
        keyword_lower = keyword.lower()
        
        title_field = 'cubeTitleEn' if language == 'en' else 'cubeTitleFr'
        
        matching_cubes = [
            cube for cube in cubes
            if keyword_lower in cube.get(title_field, '').lower()
        ]
        
        return matching_cubes
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        logger.debug("Session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self):
        """String representation of the client."""
        return f"StatCanClient(base_url='{self.BASE_URL}', timeout={self.timeout})"
