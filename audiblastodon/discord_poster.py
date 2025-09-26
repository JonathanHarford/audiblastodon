import requests

def post_to_discord(webhook_url, message):
    """
    Posts a message to a Discord webhook.

    Args:
        webhook_url: The Discord webhook URL.
        message: The message to post.
    """
    data = {
        "content": message,
    }
    response = requests.post(webhook_url, json=data)
    response.raise_for_status()
