from pprint import pprint
from datetime import datetime, timedelta
import logging, traceback, sys
from whatsapp_managment import send_whatsapp, contact_basic_info, get_group_info, get_message_info, get_message_by_id
from database import SQLiteWrapper
NOTIFY_GROUP = '120363344992442907@g.us'

class whatsappMsg(object):
    def __init__(self, chat_id: str, msg_id: str, body: str, db: SQLiteWrapper,
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
        self.db = db
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
        return send_whatsapp(msg, self.db.db_cofig[''])
    
    
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

        return self.db.free_query(query)
    
    @staticmethod
    def get_name_from_chat(chat_id: str, domain: str):
        contact_info = contact_basic_info(chat_id, domain)
        if contact_info['isMyContact']:
            return contact_info['name']
        else: 
            return contact_info['number'] + ' ' + contact_info['pushname']

    def get_user_id_from_group_msg(self):
        logging.info(f"\n\n\n{get_message_info(self.chat_id, self.msg_id, self.db.whatsapp_cofig['child_url'])}\n\n\n")

    def __set_msg_details(self):
        if '@c.us' in self.chat_id: # Treat as Group
            self.user_name = self.get_name_from_chat(self.chat_id, self.db.whatsapp_cofig['child_url'])
            self.is_group = False
            self.group_name = None
        elif '@g.us' in self.chat_id: # Treat as Chat
            self.user_name = self.get_name_from_chat(self.get_user_id_from_group_msg(), self.db.whatsapp_cofig['child_url'])
            self.is_group = True
            group_details = get_group_info(self.chat_id, self.db.whatsapp_cofig['child_url'])
            self.group_name = group_details['name']
            self.is_archived = group_details['archived']
        # print(self.user_name)
            
    def is_time_to_delete(self):
        current_time = datetime.now()
        time_difference = current_time - self.timestamp
        return time_difference >= timedelta(days=2)
                
    def delete_me(self, table_name) -> bool:
        return self.db.delete(table_name, 'msg_id', self.msg_id)



if '__main__' == __name__:
    data = """
    CREATE TABLE IF NOT EXISTS saved_messages (
        chat_id VARCHAR(255),
        msg_id VARCHAR(255),
        body TEXT,
        is_group tinyint(1),
        group_name VARCHAR(255),
        user_name VARCHAR(255),
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    db = SQLiteWrapper()
    db.free_query(data)
    db.whatsapp_cofig['child_url'] = 'http://192.168.2.10:5000'
    msg_id = 'false_972547200478-1416170171@g.us_3AB141AA14CCAA7C7F1D_972525610018@c.us'
    chat_id = '972547200478-1416170171@g.us'
    data = get_message_by_id(chat_id, msg_id, db.whatsapp_cofig['child_url']).json()
    # pprint(data)
    message = data['_data']
    msg = whatsappMsg(chat_id, msg_id, message['body'], db)
