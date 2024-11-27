import requests, logging, yaml
from pprint import pprint
from time import sleep

# Load the YAML configuration file
def load_config(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def get_message_by_id(chat_id: str, msg_id: str, domain:str):
    response = requests.get(f"{domain}/api/default/chats/{chat_id}/messages/{msg_id}", None)
    return response

def send_whatsapp(chat_id: str, msg: str, domain:str):
    try:
        logging.info(f"sending message to: {chat_id} -> {msg}")
        response = requests.post(
        f"{domain}/api/sendText",
        json={
            "chatId": chat_id,
            "text": msg,
            "session": "default",
        },
        )
        response.raise_for_status()
        if response.status_code != 201:
            return {'status': False, 'data': response.json(), 'status_code' : response.status_code}
        else:
            return {'status': True, 'data': response.json(), 'status_code' : response.status_code}
    except Exception as e:
        error_message = "[send_whatsapp] " + str(e)
        logging.error(error_message)
        return {'status': False, 'error': error_message}

def check_for_deleted_mesagges(domain):
    return requests.get(f'{domain}/child/check_deleted', None)
    
def is_my_contact(phone_number:str, domain:str):
    response = requests.get(f"{domain}/api/contacts/check-exists", params={'phone': phone_number, 'session': 'default'}).json()
    return response

def contact_basic_info(phone_number:str, domain:str):
    response = requests.get(f"{domain}/api/contacts", params={'contactId': phone_number, 'session': 'default'}).json()
    return response

def get_group_info(id :str, domain:str):
    response = requests.get(f"{domain}/api/default/groups/{id}").json()
    return response

def get_chat_info(id :str, domain:str):
    response = requests.get(f"{domain}/api/default/chats/{id}").json()
    return response

def get_message_info(chatId :str, messageId: str, domain:str):
    response = requests.get(f"{domain}/api/default/chats/{chatId}/messages/{messageId}").json()
    return response

def delete_all_messages_from_chat(chat_id :str, domain:str):
    response = requests.delete(f"{domain}/api/default/chats/{chat_id}/messages").json()
    return response

def restart_waha_session(domain:str, web_hook_url: str, events: list):
    data = {
            "webhooks": [
                {
                    "url": web_hook_url,
                    "events": events
                }
            ]
        }
    response = requests.post(url=f'{domain}/api/sessions/default/restart', json=data)
    return response

def start_waha_session(domain:str, web_hook_url: str, events: list):
    data = {
            "webhooks": [
                {
                    "url": web_hook_url,
                    "events": events
                }
            ]
        }
    response = requests.post(url=f'{domain}/api/sessions/default/start', json=data)
    return response.json()


def create_new_group(group_name: str, domain: str):
    data = {
        "name": group_name,
        "participants": [
            {
            "id": "972549747174@c.us"
            }
        ]
        }
    response = requests.post(url=f'{domain}/api/default/groups', json=data)
    if response.status_code == 201:
        return response.json()['gid']['_serialized']

def update_waha_session(domain: str, web_hook_url: str, events: list):
    data = {
        "webhooks": [
            {
                "url": web_hook_url,
                "events": events
            }
        ]
    }
    try:
        response = requests.put(url=f'{domain}/api/sessions/default', json=data)
        response_data = response.json()
        if response.status_code == 200:
            print(f"Webhook updated successfully: {response_data}")
        else:
            print(f"Failed to update webhook: {response.status_code} - {response.text}")
        return response_data
    except requests.RequestException as e:
        print(f"Error during API call: {e}")
        return None
    
def get_session_detatils(domain: str):
    try:
        response = requests.get(url=f'{domain}/api/sessions/default')
        response_data = response.json()
        if response.status_code == 200:
            pprint(f"Webhook updated successfully: {response_data}")
        else:
            print(f"Failed to update webhook: {response.status_code} - {response.text}")
        return response_data
    except requests.RequestException as e:
        print(f"Error during API call: {e}")
        return None
if '__main__' == __name__:
    domain = 'http://child.child_tracker:5000'
    web_hook_url = 'http://handler.child_tracker/child/save_new_message'
    events = "message.any"

    # Update session
    # session_update = update_waha_session(domain, web_hook_url, events)
    # pprint(session_update)
    get_session_detatils(domain)

    