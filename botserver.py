# -*- coding: utf-8 -*-
import os
import socket
from time import sleep


AuthenticationList = [[23019, 32037], [32037, 29295],
                      [18789, 13603], [16443, 29533], [18189, 21952]]


# 0 means the user haven't done anything
# 1 means got the CLIENT_USERNAME
# 2 means got the CLIENT_KEY_ID
# 4 means successful login


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

            LoginStatus = 0
            UserName = ""
            KeyID = 5

            while LoginStatus < 5:
                data = c.recv(1024).decode()
                if '\a\b' in data:
                    print("legal data")
                    data = data[:-2]
                    LoginStatus, UserName, KeyID = Login(
                        data, c, LoginStatus, UserName, KeyID)

            c.close()
            break  # child executes only one cycle

        except socket.timeout as e:  # if timeout occurs
            print("Timeout!")
            c.close()


def Login(data, c, LoginStatus, UserName, KeyID):
    print("Full data is : "+data)
    global AuthenticationList
    if LoginStatus == 0:
        UserName = data
        print("UserName is:" + UserName)
        c.send("107 KEY REQUEST\a\b".encode())  # Sending SERVER_KEY_REQUEST
        return 1, UserName, KeyID

    elif LoginStatus == 1:  # handle with CLIENT_KEY_ID
        data = int(data)
        KeyID = data
        NameASCI = [ord(char) for char in UserName]
        print("Name Ascii is : " + str(NameASCI))
        ResultHash = (sum(NameASCI)*1000 %
                      65536 + int(AuthenticationList[KeyID][0])) % 65536
        print("hash: " + str(ResultHash))
        # Sending SERVER_CONFIRMATION
        c.send((str(ResultHash)+"\a\b").encode())
        return 2, UserName, KeyID

    elif LoginStatus == 2:  # handle with CLIENT_CONFIRMATION
        data = int(data)
        NameASCI = [ord(char) for char in UserName]
        print("Name Ascii is : " + str(NameASCI))
        ResultHash = (sum(NameASCI)*1000 %
                      65536 + int(AuthenticationList[KeyID][1])) % 65536
        print("hash: " + str(ResultHash))
        if (data == ResultHash):
            # Sending SERVER_CONFIRMATION
            c.send("200 OK\a\b".encode())
        elif (data != ResultHash):
            # Sending SERVER_CONFIRMATION
            c.send("300 LOGIN FAILED\a\b".encode())

        return 3, UserName, KeyID

    return 5, UserName, KeyID


if __name__ == '__main__':
    ServerStart()
