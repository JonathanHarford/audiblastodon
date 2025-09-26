import requests

def post_to_mastodon(instance_url, access_token, message):
    """
    Posts a message to a Mastodon instance.

    Args:
        instance_url: The URL of the Mastodon instance.
        access_token: The access token for authentication.
        message: The message to post.
    """
    url = f"{instance_url}/api/v1/statuses"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    data = {
        "status": message,
        "visibility": "public",
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
