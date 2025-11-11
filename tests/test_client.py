"""Unit tests for the Statistics Canada Web Data Service client."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from statcan_webservice import StatCanClient
import requests


class TestStatCanClient(unittest.TestCase):
    """Test cases for StatCanClient."""
    
    def setUp(self):
        """Set up test client."""
        self.client = StatCanClient()
    
    def tearDown(self):
        """Clean up after tests."""
        self.client.close()
    
    @patch('statcan_webservice.client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test that client initializes with correct defaults."""
        client = StatCanClient(timeout=60)
        self.assertEqual(client.timeout, 60)
        self.assertEqual(client.BASE_URL, "https://www150.statcan.gc.ca/t1/wds/rest")
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [{"test": "data"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client._make_request("test/endpoint")
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("object", result)
        mock_get.assert_called_once()
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_make_request_api_error(self, mock_get):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ERROR",
            "message": "Test error message"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.client._make_request("test/endpoint")
        
        self.assertIn("Test error message", str(context.exception))
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_make_request_network_error(self, mock_get):
        """Test network error handling."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(requests.RequestException) as context:
            self.client._make_request("test/endpoint")
        
        self.assertIn("Failed to fetch data", str(context.exception))
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_all_cubes_list(self, mock_get):
        """Test getting all cubes list."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [
                {"productId": 123, "cubeTitleEn": "Test Cube 1"},
                {"productId": 456, "cubeTitleEn": "Test Cube 2"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_all_cubes_list()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["productId"], 123)
        mock_get.assert_called_once()
        self.assertIn("getAllCubesList", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_cube_metadata(self, mock_get):
        """Test getting cube metadata."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": {
                "productId": 18100004,
                "cubeTitleEn": "Consumer Price Index",
                "cubeStartDate": "1914-01-01"
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_cube_metadata(18100004)
        
        self.assertEqual(result["productId"], 18100004)
        self.assertIn("Consumer Price Index", result["cubeTitleEn"])
        self.assertIn("getCubeMetadata/18100004", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_changed_cube_list(self, mock_get):
        """Test getting changed cube list."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [
                {"productId": 123, "releaseTime": "2024-01-15T08:35"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_changed_cube_list("2024-01-15")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["productId"], 123)
        self.assertIn("getChangedCubeList/2024-01-15", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_series_info_from_vector(self, mock_get):
        """Test getting series info from vector."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": {
                "vectorId": "v41690973",
                "SeriesTitle": "Test Series",
                "productId": 18100004
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_series_info_from_vector("v41690973")
        
        self.assertEqual(result["vectorId"], "v41690973")
        self.assertIn("getSeriesInfoFromVector/v41690973", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_data_from_vectors_and_latest_n_periods(self, mock_get):
        """Test getting latest N periods of data."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [
                {"vectorId": "v41690973", "refPer": "2024-01", "value": 100.5},
                {"vectorId": "v41690973", "refPer": "2024-02", "value": 101.2}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_data_from_vectors_and_latest_n_periods(
            ["v41690973", "v41690974"], 
            10
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["vectorId"], "v41690973")
        self.assertIn("getDataFromVectorsAndLatestNPeriods", mock_get.call_args[0][0])
        self.assertIn("v41690973,v41690974", mock_get.call_args[0][0])
        self.assertIn("/10", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_data_from_vector_by_reference_period_range(self, mock_get):
        """Test getting data for a date range."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [
                {"refPer": "2023-01-01", "value": 100.0},
                {"refPer": "2023-06-30", "value": 102.5}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_data_from_vector_by_reference_period_range(
            "v41690973",
            "2023-01-01",
            "2023-06-30"
        )
        
        self.assertEqual(len(result), 2)
        self.assertIn("getDataFromVectorByReferencePeriodRange", mock_get.call_args[0][0])
        self.assertIn("2023-01-01", mock_get.call_args[0][0])
        self.assertIn("2023-06-30", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_bulk_vector_data_by_range(self, mock_get):
        """Test getting bulk data for multiple vectors."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [{"vectorId": "v41690973", "value": 100.0}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_bulk_vector_data_by_range(
            ["v41690973", "v41690974"],
            "2023-01-01",
            "2023-12-31"
        )
        
        self.assertIsInstance(result, list)
        self.assertIn("getBulkVectorDataByRange", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_code_sets(self, mock_get):
        """Test getting code sets."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "object": [{"codeSetId": 1, "codeSetName": "Test"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_code_sets()
        
        self.assertIsInstance(result, list)
        self.assertIn("getCodeSets", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    def test_get_full_table_download_csv(self, mock_get):
        """Test downloading full table as CSV."""
        mock_response = Mock()
        mock_response.content = b"col1,col2\nval1,val2"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_full_table_download_csv(18100004)
        
        self.assertIsInstance(result, bytes)
        self.assertIn(b"col1,col2", result)
        self.assertIn("getFullTableDownloadCSV/18100004", mock_get.call_args[0][0])
    
    @patch('statcan_webservice.client.requests.Session.get')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_get_full_table_download_csv_with_output(self, mock_open, mock_get):
        """Test downloading full table with output file."""
        mock_response = Mock()
        mock_response.content = b"csv,data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.get_full_table_download_csv(
            18100004, 
            "/tmp/test.csv"
        )
        
        mock_open.assert_called_once_with("/tmp/test.csv", 'wb')
        mock_open().write.assert_called_once_with(b"csv,data")
    
    def test_context_manager(self):
        """Test using client as context manager."""
        with StatCanClient() as client:
            self.assertIsInstance(client, StatCanClient)
        # Client should be closed after exiting context


if __name__ == '__main__':
    unittest.main()
