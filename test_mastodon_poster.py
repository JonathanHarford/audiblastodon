import pytest
import requests
from audiblastodon.mastodon_poster import post_to_mastodon

def test_post_to_mastodon(mocker):
    """
    Tests that the post_to_mastodon function sends the correct
    request to the Mastodon API.
    """
    # Mock the requests.post call
    mock_post = mocker.patch('requests.post')
    
    # Define test data
    instance_url = "https://mastodon.social"
    access_token = "test_access_token"
    message = "Hello, Mastodon!"
    
    # Call the function
    post_to_mastodon(instance_url, access_token, message)
    
    # Assert that requests.post was called correctly
    expected_url = f"{instance_url}/api/v1/statuses"
    expected_headers = {
        "Authorization": f"Bearer {access_token}",
    }
    expected_data = {
        "status": message,
        "visibility": "public",
    }
    
    mock_post.assert_called_once_with(
        expected_url,
        headers=expected_headers,
        json=expected_data
    )
