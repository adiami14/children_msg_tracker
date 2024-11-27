import requests
from database import SQLiteWrapper
from whatsapp_managment import delete_all_messages_from_chat, check_for_deleted_mesagges

def correct_misspellings(text, keywords):
    import difflib
    """
    Replaces misspelled words in the text with the closest match from keywords.
    
    Parameters:
    - text (str): The input text to process.
    - keywords (list): List of correctly spelled keywords for the bot.

    Returns:
    - str: Text with corrected keywords.
    """
    words = text.split()  # Split text into individual words
    corrected_words = []

    for word in words:
        # Find the closest match from the keywords list
        match = difflib.get_close_matches(word, keywords, n=1, cutoff=0.8)
        if match:
            # If a close match is found, use the matched keyword
            corrected_words.append(match[0])
        else:
            # If no close match is found, keep the original word
            corrected_words.append(word)

    return ' '.join(corrected_words)

def is_check_for_deleted(text: str)-> bool:
    keywords = ['מחק', 'מחוק']
    for word in keywords:
        if word in text:
            return True
    return False

def is_delete_group_msgs(text:str) -> bool:
    keywords = ['סרוק', 'סריקה']
    for word in keywords:
        if word in text:
            return True
    return False


def text_to_command(text: str, db: SQLiteWrapper, respelled=False) -> dict:
    response_to_user = {'status' : False, 'play_dead' : False, 'multi': False, 'data': None, 'respelled' : respelled}
    response_to_user['phone'] = db.whatsapp_config['notification_group_id']
    
    if is_check_for_deleted(text):
        res = check_for_deleted_mesagges(db.whatsapp_cofig['child_url'])
        if res['status']:
            return {'status' : True,  'play_dead' : False, 'data': 'סריקת הודעות מחוקות התבצעה בהצלחה'}
        else:
            return {'status' : False, 'play_dead' : False, 'data': 'סריקה נכשלה'}

    elif is_delete_group_msgs(text):
        res = delete_all_messages_from_chat(db.whatsapp_cofig['notification_group_id'], db.whatsapp_cofig['mother_url'])

    if not any([response_to_user['status'], response_to_user['respelled']]):
        text = correct_misspellings(text, [
            'מחק', 'מחוק', 'סרוק', 'סריקה'
            ])

        response_to_user = text_to_command(text, db, respelled=True)
    return response_to_user