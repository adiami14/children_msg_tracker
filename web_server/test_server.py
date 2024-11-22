from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys, requests

sys.path.append('/src/')
sys.path.append('/home/adiami/sergei/src/')

from utills.logging_utils import setup_logging

setup_logging("Web Server for testing")
port = 8000

# Create the server
server_address = ('', port)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

# Start the server
print(f"Serving at port {port}")
httpd.serve_forever()


res = requests.get('asdasd', proxies=)