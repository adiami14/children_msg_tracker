from pprint import pprint
import logging, sys
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from utills.utils import correct_misspellings
from whatsapp.whatsapp_managment_api import user_entity, MessageHandler
from birthdays.birthday_parser import parser as birthdays_parser_text
from whatsapp.web_parser import is_web_parser, web_parser
from whatsapp.phone_book_parser import phone_book_parser, is_phone_book_parser
from whatsapp.remainders_parser import remiders_parser, find_uuids_in_string, is_reminder_request
from whatsapp.scheduler_parser import is_scheduler, scheduler_parser
from whatsapp.wahaget_parser import is_wahaget, waha_get_parser
from web_server.Web_API_Wrappers import ADMIN_PHONE
from whatsapp.calendar_parser import calendar_parser, is_calendar, find_calendar_uuid
from sync_work_calander.calendar_wrappers import delete_event
from wahaget.deleted_messages import NOTIFY_GROUP

class ExecutionType:
    GET_BIRTHDAY                = 0
    PUT_BIRTHDAY                = 1
    REMINDER                    = 2
    GET_CONNECTED_GUEST_NOW     = 3
    GET_CONNECTED_GUEST_TODAY   = 4

def text_to_command(text: str, chat_id: str, debug=False, respelled = False):
    '''
    The function get a free text and from it's key words returns a dict with:
    {function : ExecutionType, kwargs : {args}}
    '''
    db_error_response = {'status' : False, 'data' : f'There is a critical Error in datebase', 'phone' : ADMIN_PHONE, 'play_dead' : True}
    unknwon_user_response = {'status' : False, 'data' : f'unknown user try to react with sergei phone {chat_id}', 'phone' : ADMIN_PHONE, 'play_dead' : True, 'notify' : True}
    if chat_id == NOTIFY_GROUP:
        return {'play_dead' : True, 'notify' : False}
    data = user_entity.get_user_by_chat_id(chat_id)
    if not data['status']:
        return db_error_response
    if not data['data']:
        return unknwon_user_response
    else:
        user = data['data']

    auth = MessageHandler.authorizations(chat_id)
    if not auth['status']:
        return db_error_response
    if not auth['data']:
        return unknwon_user_response
    else:
        authorizations = auth['data']
    
    response_to_user = {'status' : False, 'play_dead' : False, 'multi': False}
    response_to_user['respelled'] = respelled
    response_to_user['phone'] = user.phone_number
    response_to_user['data'] = "אני לא מצליח להבין את הבקשה שלך... בוא ננסה שוב בנוסח אחר"
    if user.is_group:
        return {'status': False, 'data' : f"not a user -> group {user.name}", 'play_dead' : True}
    
    text = text.replace('\xa0', ' ') # normalize text from WhatsApp, replace \xa0 with a regular space 

    # Find UUIDs in text to delete reminder.
    res_uuid_reminder = find_uuids_in_string(text)
    res_uuid_calendar = find_calendar_uuid(text)
    if res_uuid_reminder:
        res = user.delete_reminder(res_uuid_reminder[0])
        response_to_user['status'] = res['status']
        if 'Canceled task' in res['data']:
            response_to_user['data'] = 'תזכורת נמחקה בהצלחה :)'
        else:
            response_to_user['data'] = res['data']

    # Find UUIDs in text to delete event.
    elif res_uuid_calendar:
        res = delete_event(user.calendar_id, res_uuid_calendar[0])
        if res['status']:
            response_to_user['data'] = 'אירוע נמחק בהצלחה'
            response_to_user['status'] = True
        else:
            response_to_user['data'] = res['data']
            response_to_user['status'] = False            
    
    elif is_scheduler(text):
        logging.info(f"\t\tReminder Auth:{authorizations['reminders']}")
        if not authorizations['reminders']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות תזכורות"
            logging.error(f"User {user.name},tried to access unauthorized server (reminders)")
            response_to_user['data'] = err_msg
            response_to_user['job_id'] = False
        else:
            res = scheduler_parser(text, user)
            response_to_user['status'] = res['status']
            response_to_user['data'] = res['data']
            response_to_user['job_id'] = False
            response_to_user['multi'] = res['multi']
            
    elif is_reminder_request(text):
        logging.info(f"\t\tReminder Auth:{authorizations['reminders']}")
        if not authorizations['reminders']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות תזכורות"
            logging.error(f"User {user.name},tried to access unauthorized server (reminders)")
            response_to_user['data'] = err_msg
            response_to_user['job_id'] = False
        else:
            res = remiders_parser(text, user, debug=True)
            response_to_user['status'] = res['status']
            response_to_user['data'] = res['data']
            response_to_user['job_id'] = res['job_id']
    
    elif is_phone_book_parser(text):
        if not authorizations['reminders']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות תזכורות"
            logging.error(f"User {user.name},tried to access unauthorized server (reminders)")
            response_to_user['data'] = err_msg
        else:
            res = phone_book_parser(text, user)
            response_to_user['status'] = res['status']
            response_to_user['data'] = res['data']

    elif is_calendar(text):
        if not authorizations['calendar']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות קביעת אירועים"
            logging.error(f"User {user.name},tried to access unauthorized server (calendar)")
            response_to_user['data'] = err_msg
        else:
            res = calendar_parser(text, user)
            response_to_user['status'] = res['status']
            response_to_user['data'] = res['data']
            response_to_user['event_id'] = res['event_id']
            response_to_user['job_id'] = res['job_id']
    
    elif is_web_parser(text):
        res = web_parser(text, user)
        response_to_user['status'] = res['status']
        response_to_user['data'] = res['data']

    elif is_wahaget(text):
        if not authorizations['deleted_messages']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות זה"
            logging.error(f"User {user.name},tried to access unauthorized server (deleted messages)")
            response_to_user['data'] = err_msg
        else:
            res = waha_get_parser(text, user)
            response_to_user['status'] = res['status']
            response_to_user['data'] = None

    elif 'הולדת' in text:
        if not authorizations['birthdays']:
            err_msg = f"היי {user.heb_name} לצערי אין לך הרשאות לשימוש בשירות ימי הולדת"
            logging.error(f"User {user.name},tried to access unauthorized server (birthdays)")
            response_to_user['data'] = err_msg
        else:
            res = birthdays_parser_text(text, user)
            response_to_user['status'] = res['status']
            response_to_user['data'] = res['data']
    
    pprint(response_to_user)
    if not any([response_to_user['status'], response_to_user['respelled']]):
        text = correct_misspellings(text, [
            'הולדת', # Birthdays
            'תזכיר', 'הזכר', # Reminders
            'פגישה', 'אירוע', 'ליומן', 'ביומן', 'לוז', 'לו"ז', # Calendar
            'ספר טלפונים', 'לספר טלפונים', 'לספר הטלפונים', 'את הטלפון' # Phone Book
            ])

        response_to_user = text_to_command(text, chat_id, respelled=True)
    return response_to_user
        
    
    


if '__main__' == __name__:
    # logging.basicConfig(level=logging.INFO)
    pprint(text_to_command('רשימת משימות', '972549747174@c.us', debug=True))
    # print(find_calendar_uuid('3e2c9f6f2c7e4992939f4dbd8006dba0'))
