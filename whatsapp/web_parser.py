import re, logging, sys
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from web_server.Web_API_Wrappers import get_web_links
from whatsapp.whatsapp_managment_api import user_entity, GENERIC_WHATSAPP_ERROR_MESSAGE

def is_inside(text: str, list_of_words: list) -> bool:
    for word in list_of_words:
        if word in text:
            return True
    return False

def is_web_parser(text: str) -> bool:
    if 'אתר פעולות' in text:
        return True
    return False

def web_parser(text: str, user: user_entity) -> dict:
    return_message = {'status' : True}
    return_message['phone'] = user.phone_number
    links = get_web_links()
    if is_inside(text, ['צמח', 'צמחים']):
        return_message['data'] = links['Plant Control Panel']['link']
    elif is_inside(text, ['בית חכם']):
        return_message['data'] = links['Home Assistant']['link']
    else:
        return_message['data'] = links['Control Panel']['link']
    
    return return_message