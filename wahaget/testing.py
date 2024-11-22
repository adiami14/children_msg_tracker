from pprint import pprint
import requests

URL = "http://192.168.2.10:4000"
BUILDING_GROUP_ID = '972547200478-1416170171@g.us'

def send_get_request_(endpoint: str, data: dict):
    try:
        response = requests.get(URL + endpoint, params=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {'status': False, 'error': f'HTTP error occurred: {http_err}'}
    except requests.exceptions.ConnectionError as conn_err:
        return {'status': False, 'error': f'Connection error occurred: {conn_err}'}
    except requests.exceptions.Timeout as timeout_err:
        return {'status': False, 'error': f'Timeout error occurred: {timeout_err}'}
    except requests.exceptions.RequestException as req_err:
        return {'status': False, 'error': f'An error occurred: {req_err}'}

# /api/{session}/groups/{id}/participants
def is_member_of_building_group(phone_number: str) -> bool :
    participants = send_get_request(f'/api/default/groups/{BUILDING_GROUP_ID}/participants', None)
    for member in participants:
        if member['id']['user'] == phone_number:
            return True
    return False

pprint(is_member_of_building_group('972525757870'))
# for item in data:
#     if 'F הבניין שלנו☺' == item['name']:
#         pprint(item)
    