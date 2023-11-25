import mimetypes
import pathlib
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import socket
from json_handler import run_socket_server

BASE_DIR = pathlib.Path()


def send_data_via_socket(message):
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Ensure message is of type bytes
    if not isinstance(message, bytes):
        message = message.encode('utf-8')

    client_socket.sendall(message)

    client_socket.close()


class HttpHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        print(f"Received data: {data}")
        send_data_via_socket(data)
        self.send_response(303)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        path = pr_url.path
        if path == '/':
            self.send_html_file('index.html')
        elif path == "/message":
            self.send_html_file('message.html')
        else:
            if path:
                file = BASE_DIR.joinpath(path[1:])
                if file.exists():
                    self.send_static(file)
            self.send_html_file('error_page.html')

    def send_html_file(self, filename, status=200):
        with open(filename, 'rb') as fd:
            response_content = fd.read()
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(response_content)))
        self.end_headers()
        self.wfile.write(response_content)

    def send_static(self, file):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file, 'rb') as fd:
            self.wfile.write(fd.read())


def run_servers():
    # Start the socket server in a separate thread
    socket_server = Thread(target=run_socket_server)
    socket_server.start()

    # Start the HTTP server in the main thread
    server_address = ('', 3000)
    http = HTTPServer(server_address, HttpHandler)

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
    socket_server.join()


if __name__ == '__main__':
    run_servers()
