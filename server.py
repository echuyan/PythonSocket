import socket
from http import HTTPStatus
import re
from datetime import datetime


def parse_headers(header_lines):
    headers = {}
    for line in header_lines:
        if line:
            parts = line.split(": ", 1)
            if len(parts) == 2:
                headers[parts[0]] = parts[1]
    return headers


def parser(request, client_address):
    lines = request.split('\r\n')
    request_line = lines[0]
    header_lines = lines[1:lines.index('')]
    request_status = re.search(r'status=(\d+)', request_line)

    if request_status:
        request_status_code = int(request_status.group(1))
        response_status = next(
            (f'{status.value} {status.phrase}' for status in HTTPStatus if status.value == request_status_code),
            '200 OK'
        )
    else:
        response_status = f'{HTTPStatus.OK} {HTTPStatus.OK.phrase}'

    method, path, version = request_line.split(' ')
    headers = parse_headers(header_lines)

    response_headers = [
        f"HTTP/1.1 {response_status} ",
        "Content-Type: text/plain; charset=utf-8",
        "",
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {response_status}",
        f"Date: {datetime.now()}\r\n",
    ]
    for header, value in headers.items():
        response_headers.append(f"{header}: {value}")

    response_body = "\r\n".join(response_headers)
    return response_body



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 8080))
server_socket.listen()

print("Server is listening on port 8080")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Incoming connection from {client_address}")
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Request data: {request_data}")
    response = parser(request_data, client_address)
    with open("server_log.log", "a") as file:
        print(response, file=file)
    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()
