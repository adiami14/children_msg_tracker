import os, logging, requests, traceback
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from whatsapp_msg_handler import whatsappMsg
from datetime import datetime

from database import SQLiteWrapper

app = FastAPI()
DATABASE_DIR = './data/database.db'
MOTHER_URL = 'asdasd.asdasd:5000'

# Initialize the database
def init_db() -> SQLiteWrapper:
    if not os.path.exists('./data'):
        os.makedirs('./data')
    return SQLiteWrapper()

@app.get("/child/check_deleted")
async def check_for_deleted_messages(query_param):
    db = app.state.db
    table_name = query_param.get('table_name')
    if not table_name:
        logging.error("[check_for_deleted_messages] no parameters")
        return {'status' : False}
    
    messages = db.fetch_all(table_name)
    try:
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
        return {'status' : True}
    except Exception as e:
        logging.error(f"[check_for_deleted_messages] error: {str(e)}\n{traceback.format_exc()}")
        return {'status' : False, 'error' : e}


@app.post("/mother/get_new_command")
async def get_new_command(post_data):
    db = app.state.db
    last_msg_from_me = db.last_msg_from_me
    try:
        event = post_data.get('event')
        if event == 'message':
            payload = post_data.get('payload')
            chat_id = payload["from"]
            msg_id = payload['id']
            fromMe = payload['fromMe']
            body = payload['body']
            hasMedia = payload['hasMedia']
        if chat_id == last_msg_from_me:
            logging.info("msg from bot")
            return {"status": "drop", 'data': 'bot'}   
        if chat_id != db.whatsapp_config['notification_group_id']:
            return {"status": "drop", 'data': ''}   
        
        logging.info(f"Event: {event}")
        logging.info(f"chat_id: {chat_id}")
        logging.info(f"message_id: {msg_id}")

    except Exception as e:
        logging.error(f"Error processing whatsapp event: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}


@app.post("/child/save_new_message")
async def save_new_message(post_data):
    db = app.state.db
    last_msg_from_me = app.state.db.last_msg_from_me
    try:
        event = post_data.get('event')
        if event == 'message':
            payload = post_data.get('payload')
            chat_id = payload["from"]
            msg_id = payload['id']
            fromMe = payload['fromMe']
            body = payload['body']
            hasMedia = payload['hasMedia']
            if chat_id == last_msg_from_me:
                logging.info("msg from bot")
                return {"status": "drop", 'data': 'bot'}   
            if chat_id == 'status@broadcast':
                logging.info("broadcast")
                return {"status": "drop", 'data': 'broadcast'}   
            if hasMedia and len(body) <= 1:
                return {"status": "drop", 'data': 'hasMedia'}

        logging.info(f"Event: {event}")
        logging.info(f"chat_id: {chat_id}")
        logging.info(f"message_id: {msg_id}")
        logging.info(f"body: {body}")
        
        msg = whatsappMsg(chat_id, msg_id, body, db, hasMedia=hasMedia)

    except Exception as e:
        logging.error(f"Error processing whatsapp event: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}




if __name__ == "__main__":
    import uvicorn
    app.state.db = init_db()
    uvicorn.run(app, host="0.0.0.0", port=80)
