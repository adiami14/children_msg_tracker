import json
import requests
from pprint import pprint

def test_whatsapp_event():
    url = 'https://6fb8-81-199-124-183.ngrok-free.app/whatsapp/event'
    headers = {'Content-Type': 'application/json'}
    data = {
        "event": "message",
        "session": "default",
        "engine": "WEBJS",
        "environment": {
            "tier": "PLUS",
            "version": "2023.10.12"
        },
        "me": {
            "id": "71111111111@c.us",
            "pushName": "~"
        },
        "payload": {}
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    try:
        response_content = response.json()  # Try to parse JSON response
    except json.JSONDecodeError:
        response_content = response.text  # Fallback to plain text if not JSON

    pprint(response_content)

if __name__ == '__main__':
    test_whatsapp_event()
