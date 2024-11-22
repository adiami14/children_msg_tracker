from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import sys, logging, json, argparse, traceback, requests
sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')
from db_server.web_api import *
from birthdays.web_api import send_comming_birthdays_over_whatsapp, add_birthday, get_birthday_by_name
from plant_server.web_api import *
from whatsapp.web_api import send_whatsapp_text, whatsapp_event, delete_all_chats, save_new_message, wahaGet_send_whatsapp
from network_scanner.local_network_scanner import last_network_scan
from web_server.Web_API_Wrappers import send_whatsapp
from scheduler.web_api import cancel_scheduler_task, get_job_list
from sync_work_calander.web_api import delete_calendar_event, calendar_get_event_by_id, create_calendar_event
from wahaget.deleted_messages import check_for_deleted_messages
from utills.utils import convert_dates_to_strings

def get_web_links(query_params):
    res = get_data("select * from links;", True)
    if not res['status']:
        return res
    links = {}
    for items in res['data']:
        links[items['serve']] = {'id' : items['id'], 'link' : items['link']}
    return links

def testing_services(query_params):
    return "success!!"

def handle_not_found(query_params, garbege=None):
        return "Endpoint not found"

def get_last_netscan(query_params):
    try:
        return last_network_scan('/log/network_scanner.log')
    except Exception as e:
        return str(e)

def on_my_way_home(query_params):
    msg = "היי ירדן, כאן סרגיי.\nעדי ביקש שאעדכן אותך שהוא בדרך הביתה. יצא עכשיו מתחנת ת''א סבידור מרכז"
    return {'status-yarden' : send_whatsapp(msg, '972523752473'), 'status-adi': send_whatsapp('היי עדי, כאן סרגיי\nבדיוק עדכנתי את ירדן שאתה בדרך הביתה', '972549747174')}

def is_urgent(query_params):
    msg = "היי ירדן, כאן סרגי\nהטלפון של עדי על שקט במידה ותרצי להוציא את הטלפון שלו משקט תלחצי על הקשירו הבא:\nאנא השתמשי בשיקול דעת שלא תעשי לו פאדיחות!\n\n"
    url = "https://trigger.macrodroid.com/08d284a9-d91b-4f99-8ed2-76fe4b4e1c60/wife-urgent"
    try:
        err1 = send_whatsapp(msg + url, '972549747174')
        # err2 = send_whatsapp('עדי היקר, כאן סרגי\nירדן מחפשת אותך בדחיפות', 'adi')
        logging.info(f"Sending wife option to declare urgent {err1}")
        # logging.info(f"Sending Adi Yarden is looking form him ugently {err2}")
        return {'status-yarden' : err1}
    except Exception as e:
        logging.error(f"faild to send wife {str(e)}")
        return {'status' : False, 'error' : str(e) }

class MyRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.endpoints = {
            '/'                                 : '/index.html'                         ,
            '/plants_app.html'                  : '/plants_app.html'                    ,
            '/links'                            : get_web_links                         ,
            '/test'                             : testing_services                      ,
            '/send_whatsapp'                    : send_whatsapp_text                    ,
            
            '/birthdays/get'                    : send_comming_birthdays_over_whatsapp,
            '/birthdays/update'                 : add_birthday                          ,
            '/birthdays/get_by_name'            : get_birthday_by_name                  ,
            
            '/plants/add_measure'               : update_new_measure                    ,
            '/plants/get_sleep_time'            : get_sleep_time                        ,
            '/plants/get_measurments'           : get_measurments                       ,
            '/plants/reset_error_flags'         : reset_error_flags                     ,
            '/plants/reset_notify_flags'        : reset_notify_flags                    ,
            '/plants/get'                       : get_plant_details                     ,
            '/plants/update'                    : update_plant_details                  ,
            
            '/database/get'                     : database_get_data                     ,
            '/database/update'                  : database_update_data                  ,
            '/database/backup'                  : database_backup                       ,
            '/database/is_alive'                : database_is_alive                     ,
            '/database/last_modified'           : database_when_was_last_modified       ,
            
            '/notify_wife/way_home'             : on_my_way_home                        ,
            '/notify_wife/urgent'               : is_urgent                             ,
            
            '/network_scanner/get_last_netscan' : get_last_netscan                      ,
            
            '/whatsapp/event'                   : whatsapp_event                        ,
            '/whatsapp/delete/all'              : delete_all_chats                      , 
            '/wahaGet/deleted_messages/get'     : save_new_message                      ,
            '/wahaGet/send_whatsapp'            : wahaGet_send_whatsapp                 ,
            '/wahaGet/check_deleted'            : check_for_deleted_messages            ,     
            
            '/scheduler/delete'                 : cancel_scheduler_task                 ,
            '/scheduler/getjob'                 : get_job_list                          ,
            
            '/calendar/delete'                  : delete_calendar_event                 ,          
            '/calendar/create'                  : create_calendar_event                 ,         
            '/calendar/get'                     : calendar_get_event_by_id              ,

        }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        handler_function = self.endpoints.get(path, handle_not_found)
        if path in ['/index.html', '/plants_app.html']:
            try:
                with open(f'/src/web_server{path}', 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            except IOError as e:
                logging.error(f"Failed to read file {path}: {e}")
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"404 Not Found")
            return
            # self.path = '/index.html'
            # with open('/src/web_server/index.html', 'rb') as file:
            #     content = file.read()
            # self.send_response(200)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()
            # self.wfile.write(content)
            # return
        
        logging.debug(f"Get Request received for {path} with params {query_params} calling {str(handler_function)}")
        logging.info(f"Get Request received for {path}")
        try:
            response = handler_function(query_params)
            self.send_response(200)
            self.send_header('Content-type', 'application/json') 
            self.end_headers()
            response = {'response': response}
            logging.debug(f"success: {response}")
            self.wfile.write(json.dumps(response).encode())

        except TypeError as e:
            logging.error(f"Write failed with error: {e}\nStarting to serialize")
            response_serializable = convert_dates_to_strings(response)
            logging.debug(f"success: {response_serializable}")
            self.wfile.write(json.dumps(response_serializable).encode())
        except (IOError, OSError) as e:
            logging.error(f"Write failed with error: {e}\n{traceback.format_exc()}")
            response = {'response': f"Write failed: {str(e)}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
            response = {'response': f"Unexpected error: {str(e)}"}
    
    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        handler_function = self.endpoints.get(path, handle_not_found)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data.decode('utf-8'))

        logging.debug(f"POST request received for {path} with params {query_params} and data {post_data} calling {str(handler_function)}")
        try:
            response = handler_function(query_params, post_data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json') 
            self.end_headers()
            response = {'response': response}
            logging.debug(f"success: {response}")
            self.wfile.write(json.dumps(response).encode())

        except (IOError, OSError, TypeError) as e:
            logging.error(f"Write failed with error: {e}\n{traceback.format_exc()}")
            response = {'response': f"Write failed: {str(e)}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
            response = {'response': f"Unexpected error: {str(e)}"}

def start_server():
    server_address = ('', 80)
    httpd = ThreadingHTTPServer(server_address, MyRequestHandler)
    logging.debug("logging in debug mode!")
    logging.info('\n\n\t\tStarting server...\n\n\n')
    httpd.serve_forever()

if __name__ == '__main__':
    from utills.logging_utils import setup_logging
    
    setup_logging("Logging for my Web server")

    start_server()