import requests
from loadconfig import load_config

def send(message,config):
    """
    Get group message history
    
    Args:
        group_id: Group ID
        count: Number of messages to fetch
        config: Configuration dictionary
    """
    api_config = config.get('api', {})
    base_url = api_config.get('base_url', 'http://localhost:3000')
    token = api_config.get('token', '1145141919810')
    timeout = api_config.get('timeout', 10)
    
    url = f"{base_url}/send_forward_msg"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = {
        "group_id": config.get('send_id'),
        "user_id": "textValue",
        "messages": [      {
                "type": "text",
                "data": {
                "text": message
                }
            }],
        "news": [],
        "prompt": "textValue",
        "summary": "textValue",
        "source": "textValue"
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed for group {config.get('send_id')}: {e}")
        return None


# if __name__ == "__main__":
#     send("test",load_config())