# -*- coding: utf-8 -*-
import os
import socket
from time import sleep


AuthenticationList = [[23019, 32037], [32037, 29295],
                      [18789, 13603], [16443, 29533], [18189, 21952]]


LoginStatus = 0
# 0 means the user haven't done anything
# 1 means got the CLIENT_USERNAME
# 2 means got the CLIENT_KEY_ID
# 4 means successful login

UserName = ""


def ServerStart():
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

        print("Address is " + str(address))
        c.settimeout(10)
        try:
            # recv gets sequence of bytes -> decoding into string
            data = c.recv(1024).decode()
            if '\a\b' in data:
                print("legal data")
                data = data[:-2]
                Stringhandle(data, c)

            c.close()
            break  # child executes only one cycle

        except socket.timeout as e:  # if timeout occurs
            print("Timeout!")
            c.close()


def Stringhandle(data, c):
    print("Full data is : "+data)
    global LoginStatus
    global AuthenticationList
    if LoginStatus == 0:
        UserName = data
        print("UserName is:" + UserName)
        c.send("107 KEY REQUEST\a\b".encode())  # Sending SERVER_KEY_REQUEST
        LoginStatus = 1
    if LoginStatus == 1:  # handle with the CLIENT_KEY_ID
        data = c.recv(1024).decode()
        if '\a\b' in data:
            print("legal data")
            data = data[:-2]
            data = int(data)
        print("innnnnn")
        NameASCI = [ord(char) for char in UserName]
        print("Name Ascii is : " + str(NameASCI))
        ResultHash = (sum(NameASCI)*1000 %
                      65536 + int(AuthenticationList[data][0])) % 65536
        print("hash: " + str(ResultHash))
        # Sending SERVER_CONFIRMATION
        c.send((str(ResultHash)+"\a\b").encode())


if __name__ == '__main__':
    ServerStart()
