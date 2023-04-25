import os
import socket
from time import sleep


# socket creation: ip/tcp
l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# binding the socket to this device, port number 6666
l.bind(('localhost', 6667))
l.listen(10)  # number of clients

while True:

    c, address = l.accept()  # accept returns newly created socket and address of the client

    child_pid = os.fork()  # fork returns process id of the child - stored in the parent

    if child_pid != 0:  # we are in the parent thread
        c.close()
        continue

    l.close()

    print(address)
    c.settimeout(10)
    try:
        # recv gets sequence of bytes -> decoding into string
        data = c.recv(1024).decode()

        print(data)

        sleep(10)  # 10 seconds

        c.send("Hello client!".encode())

        c.close()
        break  # child executes only one cycle

    except socket.timeout as e:  # if timeout occurs
        print("Timeout!")
        c.close()
