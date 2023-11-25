import json
import socket
import urllib.parse
import pathlib
from datetime import datetime

BASE_DIR = pathlib.Path()


def save_data_to_json(data):
    cleaned_data = urllib.parse.unquote_plus(data)
    data_parse = {key: value for key, value in [el.split('=') for el in cleaned_data.split('&')]}
    data_dir = BASE_DIR.joinpath('storage')
    data_dir.mkdir(parents=True, exist_ok=True)

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    new_entry = {current_time: {"username": data_parse.get('username', ''), "message": data_parse.get('message', '')}}

    existing_data = {}
    data_file_path = data_dir.joinpath('data.json')
    if data_file_path.exists():
        with open(data_file_path, 'r') as file:
            existing_data = json.load(file)

    print("New Entry:", new_entry)

    existing_data.update(new_entry)

    with open(data_file_path, 'w') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=2)


def run_socket_server():
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(10000)

    try:
        while True:
            conn, address = server_socket.accept()
            data = conn.recv(1024)  # Adjust the buffer size as needed
            if not data:
                break

            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"Error decoding data: {e}")
                continue

            save_data_to_json(data)
            conn.close()

    except KeyboardInterrupt:
        print("Server is shutting down...")

    finally:
        server_socket.close()


if __name__ == "__main__":
    run_socket_server()
