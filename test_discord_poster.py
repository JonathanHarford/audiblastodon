import pytest
from audiblastodon.discord_poster import post_to_discord

def test_post_to_discord(mocker):
    """
    Tests that the post_to_discord function sends the correct
    request to the Discord webhook URL.
    """
    # Mock the requests.post call
    mock_post = mocker.patch('audiblastodon.discord_poster.requests.post')
    
    # Define test data
    webhook_url = "https://discord.com/api/webhooks/123/abc"
    message = "Hello, Discord!"
    
    # Call the function
    post_to_discord(webhook_url, message)
    
    # Assert that requests.post was called correctly
    expected_data = {
        "content": message,
    }
    
    mock_post.assert_called_once_with(
        webhook_url,
        json=expected_data
    )
