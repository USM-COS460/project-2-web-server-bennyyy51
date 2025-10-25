#Benjamin Franklin, COS460, Assignment2, Prof. Houser
#self made comments to understand the code better
#AI assisted

import socket
import os
import mimetypes
import datetime
import threading

#host = localhost, port = user entered, root = user entered
HOST, PORT = "0.0.0.0", int(input('port number: '))
WEB_ROOT = input('file directory: ') #./www

#return the date in the correct format
def http_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")

def handle_client(client_socket, addr):
    print(f"{addr} connected")
    data = b""
    #while not 2 consecutive new lines, keep receiving data
    while b"\r\n\r\n" not in data:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk

    #decode the request data fron bytes to string
    request = data.decode("utf-8", errors="ignore")
    if not request.strip():
        return
    print("request from", addr, ":\n", request)

    #parse the request
    lines = request.splitlines()
    request_line = lines[0].strip() if lines else ""
    parts = request_line.split()
    path = parts[1]

    #redirect original url to the index page
    if path == "/":
        path = "/index.html"

    #get the full file path
    file_path = os.path.join(WEB_ROOT, path.lstrip("/"))

    if os.path.isfile(file_path):
        #guess the mime file type
        mime_type,_ = mimetypes.guess_type(file_path)
        #if mime type is none, set it to text/plain
        mime_type = mime_type or "text/plain"
        #with open to save memory, read the file if it exists
        with open(file_path, "rb") as f:
            body = f.read()
        status_line = "HTTP/1.1 200 OK"
    else:
        body = b"<h1>404 Not Found</h1>"
        mime_type = "text/html"
        status_line = "HTTP/1.1 404 Not Found"

    #the response as required along with two new lines
    headers = [status_line,
        f"Date: {http_date()}",
        "Server: HTTPserver/2.1",
        f"Content-Type: {mime_type}",
        f"Content-Length: {len(body)}",
        "",
        ""]
    
    #send the response and close the connection
    response = "\r\n".join(headers).encode("utf-8") + body
    client_socket.sendall(response)
    client_socket.close()
    print(f"{addr} disconnected")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #allow reuse of address for testing
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"{HOST}:{PORT} active")

    #make new thread for each connection
    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.daemon = True 
        thread.start()

if __name__ == "__main__":
    main()