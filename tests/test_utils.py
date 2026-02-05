"""
Tests for utility functions.
"""
import pytest
from unittest.mock import Mock, patch
from utils import AIWorker


@pytest.mark.unit
class TestAIWorker:
    """Tests for AIWorker class."""
    
    @patch('utils.client')
    def test_ai_worker_success(self, mock_client, qtbot):
        """Test successful AI request."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create worker and connect signal
        worker = AIWorker("Test prompt")
        response_received = []
        
        def handle_response(response):
            response_received.append(response)
        
        worker.finished.connect(handle_response)
        
        # Run the worker
        worker.run()
        
        # Wait for signal (in real test, qtbot would handle this)
        # For unit test, we can check the mock was called
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('utils.client')
    def test_ai_worker_error(self, mock_client):
        """Test AI request error handling."""
        # Mock an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        worker = AIWorker("Test prompt")
        error_received = []
        
        def handle_error(error):
            error_received.append(error)
        
        worker.error.connect(handle_error)
        
        # Run the worker
        worker.run()
        
        # Check error was emitted
        assert len(error_received) > 0
        assert "Error" in error_received[0]

    @patch('utils.client')
    def test_ai_worker_empty_prompt(self, mock_client):
        """Test with empty prompt - API is still called, behavior depends on OpenAI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response

        worker = AIWorker("")
        response_received = []

        def handle_response(response):
            response_received.append(response)

        worker.finished.connect(handle_response)
        worker.run()

        # API should still be called (empty string is valid input)
        mock_client.chat.completions.create.assert_called_once()
