import sys
sys.path.append('/home/adiami/sergei/src/')
from web_server.Web_API_Wrappers import get_data, send_whatsapp, update_data
print(all((32, True, 'asd', True)))

print(f'return value from update_data: {update_data("asdasdasd")}')