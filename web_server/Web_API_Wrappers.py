import requests, logging, sys, json, datetime
from pprint import pprint

WAHAGET_URL = "http://192.168.2.10:5000"
sys.path.append('/home/adiami/sergei/src/')
from utills.error_handling import error_logger, error_handler

def send_post_request(endpoint: str, data: dict, url=None, token=None):
    if not url:
        url = "http://web_server.sergei"
    
    headers = {
        "Content-Type": "application/json"
    }

    # Add Bearer token to the headers if provided
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print(f"URL: {url + endpoint}")
        pprint(f"data: {data}")
        pprint(f"heasers: {data}")
        response = requests.post(url + endpoint, json=data, headers=headers)
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

def send_get_request(endpoint: str, data: dict, url=None,token=None):
    if not url:
        url = "http://web_server.sergei"
    
    headers = {
        "Content-Type": "application/json"
    }

    # Add Bearer token to the headers if provided
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print(f"URL: {url + endpoint}")
        pprint(f"data: {data}")
        pprint(f"heasers: {data}")
        response = requests.get(url + endpoint, json=data, headers=headers)
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

ADMIN_PHONE='972549747174'
DEBUG_GROUP = '120363311022400580@g.us'
def send_whatsapp(msg: str, phone:str):
    return send_get_request('/send_whatsapp', {'msg' : msg, 'phone' : phone})

def wahaGet_send_whatsapp(msg: str, phone:str):
    return send_get_request('/wahaGet/send_whatsapp', {'msg' : msg, 'phone' : phone})

def delete_all_chats():
    return send_get_request('/whatsapp/delete/all', None)

def get_web_links():
    return send_get_request('/links', {})['response']

@error_handler
def web_handler(endpoint:str, params: dict):
    response = requests.get("http://web_server.sergei/" + endpoint, params=params).json()
    if response["response"]:
        return response["response"]
    else:
        logging.error(f"Faild to retrieve data from database")
        return None

@error_handler
def table_last_modified(table_name: str):
    """
    Fetches the last modified timestamp of a specified table from the database.
    
    Args:
        table_name (str): The name of the table to check the last modified timestamp for.

    Returns:
        dict: A dictionary containing the response status and data.

    Example Response:
    {
        'status': True,
        'data': '05/06/2024 06:36:58'
    }
    """
    response = requests.get("http://web_server.sergei/database/last_modified", params={"table": table_name}).json()
    return response["response"]

@error_handler
def get_data(query: str, dictionary=False):
    """
    Retrieves data from the database based on a query.

    Args:
        query (str): The SQL query to execute.

    Returns:
        dict: A dictionary containing the response status and data.

    Example Response:
    {
        'status': True,
        'data': [{'id': 1, 'name': 'John Doe', 'age': 30}, ...]
    }
    """
    response = requests.get("http://web_server.sergei/database/get", params={"query": query, "dictionary" : dictionary}).json()
    return response["response"]

@error_handler
def update_data(query: str):
    """
    Updates data in the database based on a query.

    Args:
        query (str): The SQL query to execute.

    Returns:
        dict: A dictionary containing the response status and data.

    Example Response:
    {
        'status': True,
        'data': 'number of rows affected'
    }
    """
    response = requests.get("http://web_server.sergei/database/update", params={"query": query}).json()
    return response["response"]

@error_handler
def is_db_alive() -> bool:
    """
    Checks if the database is alive.

    Returns:
        dict: A dictionary containing the response status and data.

    Example Response:
    {
        'status': True,
        'data': True
    }
    """
    response = requests.get("http://web_server.sergei/database/is_alive").json()
    return response["response"]

@error_handler
def database_backup() -> bool:
    """
    Initiates a database backup.

    Returns:
        dict: A dictionary containing the response status and data.

    Example Response:
    {
        'status': True,
        'data': True
    }
    """
    response = requests.get("http://web_server.sergei/database/backup").json()
    return response["response"]

def check_for_deleted_mesagges():
    return send_get_request('/wahaGet/check_deleted', None)
    
def is_my_contact(phone_number:str):
    response = requests.get(f"{WAHAGET_URL}/api/contacts/check-exists", params={'phone': phone_number, 'session': 'default'}).json()
    return response

def contact_basic_info(phone_number:str):
    response = requests.get(f"{WAHAGET_URL}/api/contacts", params={'contactId': phone_number, 'session': 'default'}).json()
    return response

def get_group_info(id :str):
    response = requests.get(f"{WAHAGET_URL}/api/default/groups/{id}").json()
    return response

def get_chat_info(id :str):
    response = requests.get(f"{WAHAGET_URL}/api/default/chats/{id}").json()
    return response

def get_message_info(chatId :str, messageId: str):
    response = requests.get(f"{WAHAGET_URL}/api/default/chats/{chatId}/messages/{messageId}").json()
    return response

def delete_all_messages_from_chat(chat_id :str):
    response = requests.delete(f"{WAHAGET_URL}/api/default/chats/{chat_id}/messages").json()
    return response

def restart_waha_session():
    data = {
            "webhooks": [
                {
                    "url": "http://192.168.10.2/whatsapp/event",
                    "events": ["message"]
                }
            ]
        }
    response = requests.post(url='http://192.168.2.9:4000/api/sessions/default/restart', json=data)
    return response

if '__main__' == __name__:
    pprint(send_whatsapp("test", '972549747174'))
    # pprint(get_group_info('972505689222-1625670098@g.us'))
    # pprint(restart_waha_session().text)
    # data = get_data("SELECT chat_id,msg_id FROM saved_messages;", True)
    # messages = data['data']
    # check_for_deleted_mesagges()
    # for message in messages:
    #     msg_info = get_message_info(message['chat_id'], message['msg_id'])
    #     # if msg_info['hasMedia']:
    #     #     print(f"{message['msg_id']} --> type: {msg_info['media']['mimetype']}")
    #     # else:
    #     #     print(f"{message['msg_id']} --> No Media!")
    #     pprint(msg_info)
    #     break
        