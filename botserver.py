# -*- coding: utf-8 -*-
import os
import socket
from time import sleep


AuthenticationList = [[23019, 32037], [32037, 29295],
                      [18789, 13603], [16443, 29533], [18189, 21952]]


# 0 means the user haven't done anything
# 1 means got the CLIENT_USERNAME
# 2 means got the CLIENT_KEY_ID
# 3 means successful login


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

            LoginStatus = 0
            UserName = ""
            KeyID = 5
            dir = 2
            lastPos = [100, 100]
            Inimove = 0  # first time to move

            while LoginStatus < 3:
                data = RecieveData(c)
                LoginStatus, UserName, KeyID = Login(
                    data, c, LoginStatus, UserName, KeyID)

            while LoginStatus == 3:  # Successful Login
                data = RecieveData(c)
                LoginStatus, lastPos, Inimove = Navi(
                    data, c, LoginStatus, lastPos, Inimove)

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
            c.send("102 MOVE\a\b".encode())
        elif (data != ResultHash):
            # Sending SERVER_CONFIRMATION
            c.send("300 LOGIN FAILED\a\b".encode())
            return 4, UserName, KeyID

        return 3, UserName, KeyID

    return 5, UserName, KeyID


def Navi(data, c, LoginStatus, lastPos, Inimove):

    position = GetPosition(data)

    if Inimove == 0:  # move the robot to guess the robot position
        print("hey1")
        lastPos = position
        c.send("102 MOVE\a\b".encode())
        Inimove = 1
        return LoginStatus, lastPos, Inimove

    if (position[0] == 0 and position[1] == 0):
        print("hey2")
        c.send("105 GET MESSAGE\a\b".encode())
        data = RecieveData(c)
        print(data)
        c.send("106 LOGOUT\a\b".encode())

        LoginStatus = 4
        # recieve message

    elif position[0] == 0:  # pos on the y-asis
        print("hey3")
        if (position[0]-lastPos[0] != 0):
            # while robot first arrive the y-asis turn right whatever
            c.send("104 TURN RIGHT\a\b".encode())
        if (abs(lastPos[1])-abs(position[1]) == 1):
            lastPos = position
            c.send("102 MOVE\a\b".encode())

        elif (abs(lastPos[1])-abs(position[1]) == -1):
            lastPos = position
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("102 MOVE\a\b".encode())

    elif position[1] == 0:  # pos on the x-asis
        print("hey4")
        print("position"+str(position))
        print("lastPos"+str(lastPos))
        if (position[1]-lastPos[1] != 0):
            # while robot first arrive the x-asis turn right whatever
            c.send("104 TURN RIGHT\a\b".encode())
        if (abs(lastPos[0])-abs(position[0]) == 1):
            lastPos = position
            c.send("102 MOVE\a\b".encode())

        elif (abs(lastPos[0])-abs(position[0]) == -1):
            lastPos = position
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("102 MOVE\a\b".encode())

    else:  # pos not on the x or y-asis
        if (abs(lastPos[0])-abs(position[0]) == -1):
            lastPos = position
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("102 MOVE\a\b".encode())
        elif (abs(lastPos[0])-abs(position[0]) == 1):
            lastPos = position
            c.send("102 MOVE\a\b".encode())

        elif (abs(lastPos[1])-abs(position[1]) == 1):
            lastPos = position
            c.send("102 MOVE\a\b".encode())

        elif (abs(lastPos[1])-abs(position[1]) == -1):
            lastPos = position
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("104 TURN RIGHT\a\b".encode())
            data = RecieveData(c)
            c.send("102 MOVE\a\b".encode())

    # if (position[0]-lastPos[0] == 0) and (position[1]-lastPos[1] == 0):  # obstactle solve
    #     lastPos = position
    #     c.send("104 TURN RIGHT\a\b".encode())
    #     data = RecieveData(c)
    #     c.send("103 TURN LEFT\a\b".encode())
    #     data = RecieveData(c)
    #     c.send("103 TURN LEFT\a\b".encode())
    #     data = RecieveData(c)
    #     c.send("104 TURN RIGHT\a\b".encode())
    #     data = RecieveData(c)
    #     c.send("102 MOVE\a\b".encode())

    return(LoginStatus, lastPos, Inimove)


def RecieveData(c):
    data = c.recv(1024).decode()
    if '\a\b' in data:
        print("legal data")
        data = data[:-2]
        print("data is: "+str(data))
    return data


def GetPosition(data):
    input = data.split()
    position = [int(input[i]) for i in range(1, len(input))]
    print(position)
    return position


if __name__ == '__main__':
    ServerStart()
