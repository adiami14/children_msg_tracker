from pprint import pprint
from datetime import datetime, timedelta
import logging, traceback, sys
sys.path.append('/src/')
from web_server.Web_API_Wrappers import get_data, update_data, send_whatsapp, contact_basic_info, get_group_info, get_message_info
from wahaget.wahaget_api import get_message_by_id

NOTIFY_GROUP = '120363344992442907@g.us'

class whatsappMsg(object):
    def __init__(self, chat_id: str, msg_id: str, body: str, 
                 is_group: bool = None, user_name: str = None, group_name: str = None, timestamp: datetime=None, hasMedia: bool = False) -> None:
        self.chat_id = chat_id
        self.msg_id = msg_id
        self.body = body
        self.timestamp = timestamp
        self.user_name = user_name
        self.is_group = is_group
        self.group_name = group_name
        self.is_archived = False
        self.hasMedia = hasMedia
        if not timestamp:
            self.__set_msg_details()
            if not self.is_archived:
                self.__insert_new_msg()
    
    def is_deleted(self) -> dict:
        res = get_message_by_id(self.chat_id, self.msg_id)
        if res['status']: return {'status': True, 'data': False}
        elif not res['status'] and 'HTTP error occurred: 404 Client Error: Not Found' in res['data']: return {'status': True, 'data': True}
        else: return res
    
    def notify_deleted(self):
        msg = 'The following message was deleted:\n'
        msg += f'Recived from User: *{self.user_name}*\n'
        if self.is_group:
            msg += f'Group: *{self.group_name}*\n'
        msg += f"at:  {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')} \n"
        msg += f'with the following content:\n\n{self.body}'
        return send_whatsapp(msg, NOTIFY_GROUP)
    
    
    def __insert_new_msg(self):
        if self.is_group:
            is_group = 1
        else:
            is_group = 0

        if self.body:
            safe_body = self.body.replace("\\", "\\\\").replace("'", "\\'")
        else:
            self.body = "Empty message"
        if self.hasMedia:
            self.body += " and Contained Media (which is probably already deleted)"
        safe_user_name = self.user_name.replace("\\", "\\\\").replace("'", "\\'")
        safe_group_name = self.group_name.replace("\\", "\\\\").replace("'", "\\'")

        query = f"""
            INSERT INTO saved_messages (chat_id, msg_id, body, is_group, user_name, group_name) 
            VALUES ('{self.chat_id}', '{self.msg_id}', '{safe_body}', '{is_group}', '{safe_user_name}', '{safe_group_name}')
        """

        res = update_data(query)
        if not res['status']:
            logging.error(f'[save_new_message] {res["data"]}')
            return {"status": "error", "message": res["data"]}
        return {"status": "success"}
    
    @staticmethod
    def get_name_from_chat(chat_id):
        contact_info = contact_basic_info(chat_id)
        if contact_info['isMyContact']:
            return contact_info['name']
        else: 
            return contact_info['number'] + ' ' + contact_info['pushname']

    def get_user_id_from_group_msg(self):
        logging.info(f"\n\n\n{get_message_info(self.chat_id, self.msg_id)}\n\n\n")
        return get_message_info(self.chat_id, self.msg_id)['_data']['author']['user']

    def __set_msg_details(self):
        if '@c.us' in self.chat_id: # Treat as Group
            self.user_name = self.get_name_from_chat(self.chat_id)
            self.is_group = False
            self.group_name = None
        elif '@g.us' in self.chat_id: # Treat as Chat
            self.user_name = self.get_name_from_chat(self.get_user_id_from_group_msg())
            self.is_group = True
            group_details = get_group_info(self.chat_id)
            self.group_name = group_details['name']
            self.is_archived = group_details['archived']
        # print(self.user_name)
            
    def is_time_to_delete(self):
        current_time = datetime.now()
        time_difference = current_time - self.timestamp
        return time_difference >= timedelta(days=2)
                
    def delete_me(self) -> bool:
        query = f"DELETE FROM saved_messages WHERE msg_id='{self.msg_id}';"
        res = update_data(query)
        if not res['status']:
            logging.error(f"[delete_me - whatsappMsg] error from DB {res['data']}")
            return False
        return True
   
def check_for_deleted_messages(query_param):
    data = get_data(f"SELECT * FROM saved_messages;", True)
    if not data['status']:
        logging.error(f'[get_data] Failed to get data {data}')
        return data
    messages = data['data']
    for msg in messages:
        new_msg = whatsappMsg(chat_id=msg['chat_id'], msg_id=msg['msg_id'], body=msg['body'], 
                              timestamp=datetime.strptime(msg['time'], '%Y-%m-%dT%H:%M:%S'), 
                              is_group=msg['is_group'], user_name=msg['user_name'], group_name=msg['group_name'])
        res = new_msg.is_deleted()
        print(f"{new_msg.chat_id}, {new_msg.msg_id}, {new_msg.body}")
        if res['status'] and res['data'] == True:
            res = new_msg.notify_deleted()
            if 'response' in res and 'status' in res['response'] and res['response']['status']:
                new_msg.delete_me()
            else:
                logging.error(f"Problem with sending whatsapp")
            continue
        if new_msg.is_time_to_delete():
            new_msg.delete_me()                            
    return data['status']


if '__main__' == __name__:
    msg_id = 'false_972523752473-1551853360@g.us_18553E5AC1F7AD7A821F641104EA3DF0_972523861887@c.us'
    chat_id = '972523752473-1551853360@g.us'
    data = get_message_by_id(chat_id, msg_id)
    message = data['data']['_data']
    # pprint(data)
    msg = whatsappMsg(chat_id, msg_id, message['body'])
    # check_for_deleted_messages(None)
    # data = get_data("SELECT * FROM saved_messages;", True)
    # messages = data['data']
    # for message in messages:
    #     msg = whatsappMsg(message['chat_id'], message['msg_id'], message['body'], message['is_group'], message['user_name'], message['group_name'], message['time'])
    #     print(msg.is_group)
    #     print(msg.group_name)
    #     print(msg.user_name)
    #     print(msg.body)
    #     print()
