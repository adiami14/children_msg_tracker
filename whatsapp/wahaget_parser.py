import re, logging, sys
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from web_server.Web_API_Wrappers import check_for_deleted_mesagges, delete_all_messages_from_chat
from whatsapp.whatsapp_managment_api import user_entity, GENERIC_WHATSAPP_ERROR_MESSAGE
from wahaget.deleted_messages import NOTIFY_GROUP
DELETE_FROM_UPDATE_GROUP = 'מחק עדכונים'
LIST_OF_TRIGGERS = ['בדוק מחוקות', 'שנמחקו', 'סרוק מחוקות', DELETE_FROM_UPDATE_GROUP]

def is_wahaget(text: str) -> bool:
    for phrase in LIST_OF_TRIGGERS:
        if phrase in text:
            return True
    return False

def waha_get_parser(text: str, user: user_entity) -> dict:
    return_message = {'status' : True}
    return_message['phone'] = user.phone_number
    if DELETE_FROM_UPDATE_GROUP in text:
        delete_all_messages_from_chat(NOTIFY_GROUP)
        return_message['data'] = 'כל ההודעות מקבוצת עדכונים נמחקו'
    else:
        logging.info("checking for deleted ")
        check_for_deleted_mesagges()
    
    return return_message