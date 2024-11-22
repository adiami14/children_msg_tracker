import requests, sys, time, traceback, logging
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from whatsapp.whatsapp_api import *
from wahaget.deleted_messages import NOTIFY_GROUP, whatsappMsg
from whatsapp.whatsapp_managment_api import DELIMITER
from web_server.Web_API_Wrappers import send_whatsapp, update_data

WAHAGET_URL = "http://192.168.2.10:5000"
BUILDING_GROUP_ID = '972547200478-1416170171@g.us'
BASE_URL = '192.168.10.2:3000'
SERGEI_CHAT_ID = '972524561028@c.us'

def save_new_message(query_params, post_data):
    # Extract relevant data from the post_data
    try:
        event = post_data.get('event')
        if event == 'message':
            payload = post_data.get('payload')
            chat_id = payload["from"]
            msg_id = payload['id']
            fromMe = payload['fromMe']
            body = payload['body']
            hasMedia = payload['hasMedia']
            if fromMe or chat_id == NOTIFY_GROUP or chat_id == SERGEI_CHAT_ID:
                logging.info("fromMe")
                return {"status": "drop", 'data': 'fromMe'}   
            if chat_id == 'status@broadcast':
                logging.info("broadcast")
                return {"status": "drop", 'data': 'broadcast'}   
            if hasMedia and len(body) <= 1:
                return {"status": "drop", 'data': 'hasMedia'}

        logging.info(f"Event: {event}")
        logging.info(f"chat_id: {chat_id}")
        logging.info(f"message_id: {msg_id}")
        logging.info(f"body: {body}")
        
        msg = whatsappMsg(chat_id, msg_id, body, hasMedia=hasMedia)

    except Exception as e:
        logging.error(f"Error processing whatsapp event: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

def wahaGet_send_whatsapp(query_params):
    """
    Send message to chat_id.
    :param chat_id: Phone number + "@c.us" suffix - 1231231231@c.us
    :param text: Message for the recipient
    """
    msg = query_params.get('msg', [None])[0]
    phone = query_params.get('phone', [None])[0]
    try:
        if phone and msg:
            logging.info(f"sending message to: {phone} -> {msg}")
            request = f"{WAHAGET_URL}/api/sendText"
            json = {
                "chatId": phone,
                "text": msg,
                "session": "default",
                }
            print(request,json)
            response = requests.post(request, json=json)
            response.raise_for_status()
            if response.status_code != 201:
                return {'status': False, 'data': response.text, 'status_code' : response.status_code}
            else:
                return {'status': True}
        else:
            logging.error(f"Invalid paramers {query_params}")
            return {
                'status'    : False,
                'error'     : 'Invalid parameters',
                'param'     : query_params
                }
    except Exception as e:
        error_message = "[waha_Get-send_whatsapp] " + str(e)
        logging.error(error_message)
        return {'status': False, 'error': error_message}

def get_messages_from_chat(chat_id, limit=10):
    response = requests.get(
        f"http://{BASE_URL}/api/default/chats/{chat_id}/messages?limit=10&downloadMedia=false"
    )
    response.raise_for_status()
    return response.json()

def get_all_chat(session='default'):
    response = requests.get(
        f"http://{BASE_URL}/api/{session}/chats"
    )
    response.raise_for_status()
    return response.json()

def send_reaction(message_id, success=True):
    if success:
        reaction = "👍"
    else:
        reaction = "👎"
    response = requests.put(
        f"http://{BASE_URL}/api/reaction",
        json={
            "messageId": message_id,
            "reaction": reaction,
            "session": "default"
        })

def delete_message(chat_id, message_id):
    try:
        response = requests.delete(
            f"http://{BASE_URL}/api/default/chats/{chat_id}/messages/{message_id}"
        )

        return True, response
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 500:
            return False, 'Message Do not exist'
    except Exception as e:
        return False, str(e)

def delete_chat(chat_id):
    try:
        response = requests.delete(
            f"http://{BASE_URL}/api/default/chats/{chat_id}/messages"
        )

        return True, response
    except requests.exceptions.HTTPError as http_err:
        return False, str(http_err)
    except Exception as e:
        return False, str(e)

def send_seen(chat_id, message_id, participant):
    response = requests.post(
        f"http://{BASE_URL}/api/sendSeen",
        json={
            "session": "default",
            "chatId": chat_id,
            "messageId": message_id,
            "participant": participant,
        },
    )
    response.raise_for_status()
    return response


################################################ WEB ################################################
def delete_chat_by_id(query_params):
    pass 


def send_whatsapp_text(query_params):
    """
    Send message to chat_id.
    :param chat_id: Phone number + "@c.us" suffix - 1231231231@c.us
    :param text: Message for the recipient
    """
    msg = query_params.get('msg', [None])[0]
    phone = query_params.get('phone', [None])[0]
    user = query_params.get('user', [None])[0]
    try:
        if user:
            phone = user
        if phone and msg:
            logging.info(f"sending message to: {phone} -> {msg}")
            response = requests.post(
            f"http://{BASE_URL}/api/sendText",
            json={
                "chatId": phone,
                "text": msg,
                "session": "default",
            },
        )
            response.raise_for_status()
            if response.status_code != 201:
                return {'status': False, 'data': response.text, 'status_code' : response.status_code}
            else:
                return {'status': True}
        else:
            logging.error(f"Invalid paramers {query_params}")
            return {
                'status'    : False,
                'error'     : 'Invalid parameters',
                'param'     : query_params
                }
    except Exception as e:
        error_message = "[send_whatsapp] " + str(e)
        logging.error(error_message)
        return {'status': False, 'error': error_message}

def send_multipile_messages(msg: str, phone: str):
    messages = msg.split(DELIMITER)
    messages = [message.strip() for message in messages if message.strip()]
    for i, msg in enumerate(messages):
        logging.info(f"sending msg {i+1} to {phone}")
        send_whatsapp(msg=msg, phone=phone)
        time.sleep(0.5)

def whatsapp_event(query_params, post_data):
    # Extract relevant data from the post_data
    try:
        event = post_data.get('event')
        if event == 'message':
            payload = post_data.get('payload')
            participant = payload.get('participant')
            chat_id = payload["from"]
            message_id = payload['id']
            fromMe = payload['fromMe']
            text = payload['body']
            if fromMe:
                logging.info("fromMe")
                return {"status": "success", 'data': 'fromMe'}
        
        logging.info(f"Event: {event}")
        logging.info(f"chat_id: {chat_id}")
        logging.info(f"message_id: {message_id}")
        
        # Mark the message as seen (example logic)
        if event == "message":
            logging.info(f"\n\n[whatsapp_event #1] {text}, {chat_id}")
            response = text_to_command(text, chat_id, debug=True)
            if response:
                if response['play_dead']:
                    if response['notify']:
                        send_whatsapp(msg=response['data'], phone=response['phone'])    
                        return {"status": "success"}
                    else:
                        return {"status": "success"}
                send_seen(chat_id, message_id, participant)  
                if response['status']:
                    send_reaction(message_id)
                else:
                    send_reaction(message_id, success=False)
                
                logging.info(f"[whatsapp_event] {response}")
                if response['multi']:
                    logging.info(f"Sending multipile messages to {response['phone']}")
                    send_multipile_messages(msg=response['data'], phone=response['phone'])
                elif response['data']:
                    send_whatsapp(msg=response['data'], phone=response['phone'])    
                if 'job_id' in response and response['job_id']:
                    msg = f"מזהה למחיקת תזכורת: {response['job_id']}"
                    send_whatsapp(msg=msg, phone=response['phone'])    
                if 'event_id' in response and response['event_id']:
                    msg = f"מזהה למחיקת אירוע: {response['event_id']}"
                    send_whatsapp(msg=msg, phone=response['phone'])    
                    
                # delete_message(chat_id, message_id)
            
            else:
                send_reaction(message_id, success=False)
                logging.info(f"[whatsapp_event] parsed unsuccessfullyי")

        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error processing whatsapp event: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}


def delete_all_chats(garbege):
    data = get_all_chat()
    for item in data:
        chat_id = item['id']['_serialized']
        logging.info(f"Deleting chat: {chat_id}")
        res = delete_chat(chat_id)
        if not res[0]:
            logging.error(f"[delete_all_chats] {res[1]}")


if '__main__' == __name__:
    chat_id = '972549747174@c.us'
    message_id = 'false_972549747174@c.us_C3B71B1BF98E9D00D7'
    # print(delete_message(chat_id, message_id))
    # print(delete_chat(chat_id))
    # print(delete_all_chats(None))
    wahaGet_send_whatsapp({'phone' : '972549747174', 'msg' : 'test'})