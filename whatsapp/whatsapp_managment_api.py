from pprint import pprint
import logging, sys, base64, time
from enum import Enum
import urllib.parse, traceback
from typing import Dict, Any, Optional, Union
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from scheduler.wrappers import delete_scheduled_job
from web_server.Web_API_Wrappers import get_data, update_data, send_whatsapp
from utills.utils import is_contains_hebrew

GENERIC_WHATSAPP_ERROR_MESSAGE = 'There is a system problem, please contect your admin'
DELIMITER = '$$'

class chatType(Enum):
    USER        = 1
    GROUP       = 2

class MessageHandler():
    def chat_type(chat_id: str) -> chatType: 
        if len(chat_id) > 17:
            return chatType.GROUP
        else:
            return chatType.USER
    
    def extract_phone_from_chat_id(chat_id: str):
        chat_type = MessageHandler.chat_type(chat_id)
        if chat_type == chatType.USER:
            return chat_id[0:12]
        else:
            return chat_id
    
    def is_group(chat_id:str) -> bool:
        return len(chat_id) > 17

    def authorizations(chat_id) -> dict:
        '''
        return a dict  of booleans with the authorizations of the user.
        If user is not known 'data' will only contain False.
        '''
        user_phone_number = MessageHandler.extract_phone_from_chat_id(chat_id)
        data = get_data(f"SELECT id FROM users WHERE phone_number='{user_phone_number}'", dictionary=True)
        if data['status']:
            if len(data['data']) > 0:
                id = data['data'][0]['id']
                data = get_data(f"SELECT * FROM authorization WHERE user_id='{id}'", dictionary=True)
                data['data'] = data['data'][0]
            else:
                logging.info(f"Unknown user reacted with bot")
                data['data'] = False
        else:
            logging.critical(f"\n\t[authorizations] {data}")
        return data
    
class user_entity(object):
    def __init__(self, id, phone_number, name, heb_name, common_name, phone_book_table=None, birthday_table=None, calendar_id=None) -> None:
        self.id = id
        self.phone_number = phone_number
        self.name = name
        self.heb_name = heb_name
        self.common_name = common_name
        self.phone_book_table = phone_book_table
        self.birthday_table = birthday_table
        self.is_group = None
        self.calendar_id = calendar_id
    
    @staticmethod
    def get_user_by_chat_id(chat_id: str) -> Dict[str, Union[bool, 'user_entity', None]]:
        """
        Extracts user data from the database based on the provided chat ID.

        Args:
            chat_id (str): The chat ID used to extract the user's phone number.

        Returns:
            dict: A dictionary containing:
                - 'status' (bool): Indicates whether the operation was successful.
                - 'data' (user_entity | None): The user_entity object if the user exists, otherwise None.
        """
        user_phone_number = MessageHandler.extract_phone_from_chat_id(chat_id)
        query = f"SELECT * FROM users WHERE phone_number='{user_phone_number}'"
        data = get_data(query, dictionary=True)
        logging.info(f"[get_user_by_phone_number] {data}")
        if data['status']:
            if len(data['data']) > 0:
                params = data['data'][0]
                user = user_entity(id=params['id'], 
                                phone_number=params['phone_number'], 
                                name=params['name'], 
                                heb_name=params['hebrew_name'], 
                                common_name=params['common_name'], 
                                phone_book_table=params['phone_book_table'], 
                                birthday_table=params['birthday_table'],
                                calendar_id=params['calendar_id']
                                )
                user.is_group = MessageHandler.is_group(chat_id)
                data['data'] = user
            else:
                logging.critical(f"/n/t[get_user_by_chat_id] Error in DB {data}")
                data['status'] = True
                data['data'] = False
        
        return data        

    def update_birthday_table_entry(self, user_id_to_join: int) -> dict:
        query = f"UPDATE users SET birthday_table=birthdays_{user_id_to_join} WHERE id='{self.id}';"
        return update_data(query)
    
    def update_phone_book_table_entry(self, user_id_to_join: int) -> dict:
        query = f"UPDATE users SET phone_book_table=phone_book_{user_id_to_join} WHERE id='{self.id}';"
        return update_data(query)
    
    def update_user_home(self, is_home: bool) -> dict:
        query = f"UPDATE users SET is_home={is_home} WHERE id='{self.id}';"
        return update_data(query)
    ###################################### BIRTHDAYS ######################################  
    def is_name_in_birthdays(self, name: str):
        res = self.get_birthday_by_name(name)
        if res['status']:
            if len(res['data']) > 0:
                return True
            else:
                return False
        logging.error(f"[birthdays - is_name_exist] {res}")
        return False

    def add_birthday(self, name: str, date: str) -> dict:
        if self.is_name_in_birthdays(name):
            return {'status': True, 'data' : False}
        based_name = base64.b64encode(name.encode()).decode()
        query = f"INSERT INTO {self.birthday_table} (name,date) VALUES ('{based_name}', '{date}');"
        return update_data(query)
    
    def delete_birthday(self, name: str) -> dict:
        try:
            based_name = base64.b64encode(name.encode()).decode()   
            query = f"DELETE FROM {self.birthday_table} WHERE name='{based_name}';"
            return update_data(query)
        except Exception as e:
            logging.error(f"Faild to delete {name}\n{str(e)}\n{traceback.format_exc()}")
    
    def get_birthday_by_name(self, name:str):
        based_name = base64.b64encode(name.encode()).decode()
        query = f"SELECT * FROM {self.birthday_table} WHERE name='{based_name}';"
        return get_data(query, dictionary=True)
        
    def update_birthdays_usage(self):
        res = update_data(f"UPDATE general_usage SET birthday_usage = birthday_usage + 1 WHERE user_id={self.id}")
        if res['status'] and res['data'] > 0:
            return
        else:
            logging.error(f"[update_birthdays_usage] {res}")
    
    ###################################### PHONE BOOKE ######################################
    def add_phone(self, name: str, phone_number: str) -> dict:
        if is_contains_hebrew(name):
            column_name = 'heb_name'
        else:
            column_name = 'name'
        query = f"INSERT INTO {self.phone_book_table} ({column_name},phone_number) VALUES ('{name}', '{phone_number}');"
        return update_data(query)
    
    def delete_phone_number_by_name(self, name: str) -> dict:
        query = f"DELETE FROM {self.phone_book_table} WHERE name='{name}' OR heb_name='{name}';"
        return update_data(query)
    
    def delete_phone_number_by_number(self, phone_number: str) -> dict:
        query = f"DELETE FROM {self.phone_book_table} WHERE phone_number='{phone_number}';"
        return update_data(query)
    
    def update_reminders_usage(self):
        res = update_data(f"UPDATE general_usage SET reminders_usage = reminders_usage + 1 WHERE user_id={self.id}")
        if res['status'] and res['data'] > 0:
            return
        else:
            logging.error(f"[update_reminders_usage] {res}")
    def update_reminders_token_used(self, token_used: int):
        res = update_data(f"UPDATE general_usage SET reminders_usage_by_tokens = reminders_usage_by_tokens + {token_used} WHERE user_id={self.id}")
        if res['status'] and res['data'] > 0:
            logging.info(f"\n\nuser: {self.id, self.common_name} used: {token_used} tokens")
            return
        else:
            logging.critical(f"[update_reminders_usage] {res}")
            send_whatsapp(msg=f"Pricing process is borken!!! user: {self.heb_name}, token used: {token_used}", phone='972549747174')

    
    def get_phone_by_name(self, name:str) -> dict:
        res = get_data(f"SELECT phone_number FROM {self.phone_book_table} WHERE name='{name}' OR heb_name='{name}';")
        logging.debug(f"{res}")
        if not res['status']:
            return res
        elif len(res['data']) > 1:
            err_msg = f"there is a conflict with users naming {name} got {len(res['data'])} users\nfor user {self.name}"
            logging.critical(err_msg)
            send_whatsapp(msg=err_msg, phone=user.phone_number)
            return {'status' : False, 'data' : err_msg}
        elif len(res['data']) < 1:
            res['data'] = False
            return res

        res['data'] = res['data'][0][0]
        return res
    
    def is_phone_exist(self, phone_number: str) -> dict:
        '''
            if exist will return a list of names following that number
            if not will return False
        '''
        res = get_data(f"SELECT name,heb_name FROM {self.phone_book_table} WHERE phone_number='{phone_number}';")
        if res['status']:
            if len(res['data']) > 0:
                res['data'] = res['data'][0]
            else:
                res['data'] = False        
        return res

    def get_phone_book(self) -> dict:
        return get_data(f"SELECT heb_name,phone_number FROM {self.phone_book_table};")
    
    def get_email_by_name(self, name) -> dict:
        res = get_data(f"SELECT email FROM {self.phone_book_table} WHERE name='{name}' OR heb_name='{name}';")
        if res and len(res['data']) > 0:
            res['data'] = res['data'][0][0]
        return res
    
    def delete_reminder(self, job_id) -> dict:
        res = delete_scheduled_job(job_id)
        logging.info(f"[delete_reminder]\tuser: {self.name}\n\tresults: {res}")
        return res['response']
    
    ###################################### calendar ######################################

    def get_calendar_id(self) -> dict:
        res = get_data(f"SELECT calendar_id FROM users where id={self.id}")
        if res and len(res['data']) > 0:
            res['data'] = res['data'][0][0]
        return res
        
    def update_calendar_usage(self):
        res = update_data(f"UPDATE general_usage SET calendar_usage = calendar_usage + 1 WHERE user_id={self.id}")
        if res['status'] and res['data'] > 0:
            return
        else:
            logging.error(f"[update_reminders_usage] {res}")
    
    def update_calendar_token_used(self, token_used: int):
        res = update_data(f"UPDATE general_usage SET calendar_tokens = calendar_tokens + {token_used} WHERE user_id={self.id}")
        if res['status'] and res['data'] > 0:
            logging.info(f"\n\nuser: {self.id, self.common_name} used: {token_used} tokens")
            return
        else:
            logging.critical(f"[update_reminders_usage] {res}")
            send_whatsapp(msg=f"Pricing process is borken!!! user: {self.heb_name}, token used: {token_used}", phone='972549747174')

if '__main__' == __name__:

    # logging.basicConfig(level=logging.DEBUG)
    data = user_entity.get_user_by_chat_id('972549744174@c.us')
    # print(user.get_phone_book())
    print(data)