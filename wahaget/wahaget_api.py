import requests, logging, sys
from pprint import pprint
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')

WAHAGET_URL =   "http://192.168.2.10:5000"
WAHA_URL    =   "http://192.168.2.9:3000"

BUILDING_GROUP_ID = '972547200478-1416170171@g.us'
session = 'default'

def _send_get_request(endpoint: str, data: dict):
    try:
        response = requests.get(WAHAGET_URL + endpoint, params=data)
        response.raise_for_status()
        return {'status': True, 'data' : response.json()}
    except requests.exceptions.HTTPError as http_err:
        return {'status': False, 'data': f'HTTP error occurred: {http_err}'}
    except requests.exceptions.ConnectionError as conn_err:
        return {'status': False, 'data': f'Connection error occurred: {conn_err}'}
    except requests.exceptions.Timeout as timeout_err:
        return {'status': False, 'data': f'Timeout error occurred: {timeout_err}'}
    except requests.exceptions.RequestException as req_err:
        return {'status': False, 'data': f'An error occurred: {req_err}'}

def _send_put_request(endpoint: str, data: dict):
    try:
        response = requests.put(WAHAGET_URL + endpoint, params=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {'status': False, 'data': f'HTTP error occurred: {http_err}'}
    except requests.exceptions.ConnectionError as conn_err:
        return {'status': False, 'data': f'Connection error occurred: {conn_err}'}
    except requests.exceptions.Timeout as timeout_err:
        return {'status': False, 'data': f'Timeout error occurred: {timeout_err}'}
    except requests.exceptions.RequestException as req_err:
        return {'status': False, 'data': f'An error occurred: {req_err}'}

def _send_post_request(url, endpoint: str, data: dict):
    try:
        response = requests.post(url + endpoint, params=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {'status': False, 'data': f'HTTP error occurred: {http_err}'}
    except requests.exceptions.ConnectionError as conn_err:
        return {'status': False, 'data': f'Connection error occurred: {conn_err}'}
    except requests.exceptions.Timeout as timeout_err:
        return {'status': False, 'data': f'Timeout error occurred: {timeout_err}'}
    except requests.exceptions.RequestException as req_err:
        return {'status': False, 'data': f'An error occurred: {req_err}'}

# /api/{session}/groups/{id}/participants
def is_member_of_building_group(phone_number: str) -> bool :
    participants = _send_get_request(f'/api/{session}/chats', None)
    for member in participants:
        if member['id']['user'] == phone_number:
            return True
    return False

def get_message_by_id(chat_id: str, msg_id: str):
    response = _send_get_request(f"/api/{session}/chats/{chat_id}/messages/{msg_id}", None)
    
    return response


def get_last_messeges(limit: int) -> bool :
    messages = _send_get_request(f'/api/{session}/chats?sortBy=conversationTimestamp&limit={str(limit)}&sortOrder=asc', None)
    pprint(messages)
    # for member in participants:
    #     if member['id']['user'] == phone_number:
    #         return True
    # return False

def get_sessio():
    return _send_get_request('/api/sessions/default', None)

def update_session(data):
    
    return _send_put_request('/api/sessions/default', data)

def restart_session(url, data):
    endpoint = '/api/sessions/default/restart'
    return _send_post_request(url, endpoint, data)

wahaget_data = {
        "webhooks": [
    {
    "url": "http://192.168.10.2/wahaGet/deleted_messages/get",
    "events": [
        "message"
    ],
    }
]
    }

waha_data = {
            "webhooks": [
                {
                    "url": "http://192.168.10.2/whatsapp/event",
                    "events": ["message"]
                }
            ]
        }

def restart_wahaget():
    return restart_session(WAHAGET_URL, wahaget_data)

def restart_waha():
    return restart_session(WAHA_URL, waha_data)

if '__main__' == __name__:
    print(restart_session(WAHAGET_URL, wahaget_data))
    # print(restart_session(WAHA_URL, waha_data))