import socket
import datetime
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 15004        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    startTime = datetime.datetime.now()
    for i in range(1000):
        s.sendall(b'X')
        data = s.recv(1024)
        # print(data)
    endTime = datetime.datetime.now()

print((endTime-startTime).total_seconds()*1000)  # in miliseconds
