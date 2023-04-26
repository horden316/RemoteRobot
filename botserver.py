# -*- coding: utf-8 -*-
import os
import socket
from time import sleep


AuthenticationList = [[23019, 32037], [32037, 29295],
                      [18789, 13603], [16443, 29533], [18189, 21952]]

DataList = []

ContiMoveFowardCount = 0

# 0 means the user haven't done anything
# 1 means got the CLIENT_USERNAME
# 2 means got the CLIENT_KEY_ID
# 3 means successful login
# 4 means finish


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
        c.settimeout(1.5)
        try:

            LoginStatus = 0
            UserName = ""
            KeyID = -1
            dir = 2
            lastPos = [100, 100]
            Inimove = 0  # first time to move

            while LoginStatus == 0:
                UserName, LoginStatus = RecieveUserName1(
                    c, UserName, LoginStatus)

            while LoginStatus == 1:
                data = RecieveData(c)
                data = int(data)
                KeyID = data
                if KeyID > 4:
                    c.send("303 KEY OUT OF RANGE\a\b".encode())
                    LoginStatus = 4
                NameASCI = [ord(char) for char in UserName]
                print("Name Ascii is : " + str(NameASCI))
                ResultHash = (sum(NameASCI)*1000 %
                              65536 + int(AuthenticationList[KeyID][0])) % 65536
                print("hash: " + str(ResultHash))
                # Sending SERVER_CONFIRMATION
                print("Server Conformation send")
                c.send((str(ResultHash)+"\a\b").encode())
                LoginStatus = 2

            while LoginStatus == 2:
                data = RecieveData(c)
                data = int(data)
                NameASCI = [ord(char) for char in UserName]
                print("Name Ascii is : " + str(NameASCI))
                ResultHash = (sum(NameASCI)*1000 %
                              65536 + int(AuthenticationList[KeyID][1])) % 65536
                print("hash: " + str(ResultHash))
                if (data == ResultHash):
                    # Sending SERVER_CONFIRMATION
                    c.send("200 OK\a\b".encode())
                    MoveFoward(c)
                    LoginStatus = 3
                elif (data != ResultHash):
                    # Sending SERVER_CONFIRMATION
                    c.send("300 LOGIN FAILED\a\b".encode())
                    LoginStatus = 4

            while LoginStatus == 3:  # Successful Login
                data = RecieveData(c)
                LoginStatus, lastPos, Inimove = Navi(
                    data, c, LoginStatus, lastPos, Inimove)

            c.close()
            break  # child executes only one cycle

        except socket.timeout as e:  # if timeout occurs
            print("Timeout!")
            c.close()


def RecieveUserName1(c, UserName, LoginStatus):
    UserName = RecieveData(c)
    print("Username is: "+str(UserName))
    if (len(UserName) > 18) or ('\a\b' in UserName):
        c.send("301 SYNTAX ERROR\a\b".encode())
        LoginStatus = 4
    else:
        LoginStatus = 1
        c.send("107 KEY REQUEST\a\b".encode())

    return UserName, LoginStatus


def MoveFoward(c):
    global ContiMoveFowardCount
    c.send("102 MOVE\a\b".encode())
    ContiMoveFowardCount += 1


def TurnLeft(c):
    global ContiMoveFowardCount
    c.send("103 TURN LEFT\a\b".encode())
    ContiMoveFowardCount = 0


def TurnRight(c):
    global ContiMoveFowardCount
    c.send("104 TURN RIGHT\a\b".encode())
    ContiMoveFowardCount = 0


def Navi(data, c, LoginStatus, lastPos, Inimove):

    position = GetPosition(data)
    print("position"+str(position))
    print("lastPos"+str(lastPos))

    if Inimove == 0:  # move the robot to guess the robot position
        lastPos = position
        MoveFoward(c)
        Inimove = 1
        return LoginStatus, lastPos, Inimove

    if (position == lastPos):  # obstactle solve
        global ContiMoveFowardCount
        if ContiMoveFowardCount > 3:
            #data = RecieveData(c)
            TurnRight(c)
            data = RecieveData(c)
            MoveFoward(c)
            data = RecieveData(c)

            TurnLeft(c)
            data = RecieveData(c)
            MoveFoward(c)
            data = RecieveData(c)
            MoveFoward(c)
            data = RecieveData(c)

            TurnLeft(c)
            data = RecieveData(c)
            MoveFoward(c)
            data = RecieveData(c)

            TurnRight(c)
            data = RecieveData(c)
            position = GetPosition(data)
            lastPos = position
            MoveFoward(c)

            # data = RecieveData(c)
            # position = GetPosition(data)
            # lastPos = position
            # MoveFoward(c)

            return(LoginStatus, lastPos, Inimove)

    if (position[0] == 0 and position[1] == 0):
        print("get message!!!")
        c.send("105 GET MESSAGE\a\b".encode())
        data = RecieveData(c)
        print(data)
        c.send("106 LOGOUT\a\b".encode())

        LoginStatus = 4
        # recieve message

    elif position[0] == 0:  # pos on the y-asis
        if (position[0]-lastPos[0] != 0):
            # while robot first arrive the y-asis turn right whatever
            TurnRight(c)
            data = RecieveData(c)
            lastPos = position
            MoveFoward(c)
        if (abs(lastPos[1])-abs(position[1]) == 1):
            lastPos = position
            MoveFoward(c)

        elif (abs(lastPos[1])-abs(position[1]) == -1):
            lastPos = position
            TurnRight(c)
            data = RecieveData(c)
            TurnRight(c)
            data = RecieveData(c)
            lastPos = GetPosition(data)
            MoveFoward(c)
        # else:
        #     lastPos = position
        #     MoveFoward(c)

    elif position[1] == 0:  # pos on the x-asis
        if (position[1]-lastPos[1] != 0):
            # while robot first arrive the x-asis turn right whatever
            TurnRight(c)
            data = RecieveData(c)
            lastPos = position
            MoveFoward(c)
        if (abs(lastPos[0])-abs(position[0]) == 1):
            lastPos = position
            MoveFoward(c)

        elif (abs(lastPos[0])-abs(position[0]) == -1):
            lastPos = position
            TurnRight(c)
            data = RecieveData(c)
            TurnRight(c)
            data = RecieveData(c)
            lastPos = GetPosition(data)
            MoveFoward(c)
        # else:
        #     lastPos = position
        #     MoveFoward(c)

    else:  # pos not on the x or y-asis
        if (abs(lastPos[0])-abs(position[0]) == -1):
            lastPos = position
            TurnRight(c)
            data = RecieveData(c)
            TurnRight(c)
            data = RecieveData(c)
            MoveFoward(c)
        elif (abs(lastPos[0])-abs(position[0]) == 1):
            lastPos = position
            MoveFoward(c)

        elif (abs(lastPos[1])-abs(position[1]) == 1):
            lastPos = position
            MoveFoward(c)

        elif (abs(lastPos[1])-abs(position[1]) == -1):
            lastPos = position
            TurnRight(c)
            data = RecieveData(c)
            TurnRight(c)
            data = RecieveData(c)
            lastPos = GetPosition(data)
            MoveFoward(c)
        # else:
        #     lastPos = position
        #     MoveFoward(c)

    return(LoginStatus, lastPos, Inimove)


def RecieveData(c):
    global DataList

    #print("len is :"+str(len(DataList)))
    #print("datalist is :" + str(DataList))
    if len(DataList) < 1:
        data = c.recv(1024).decode()
        T_data = data
        print("data is: "+str(T_data))
        while T_data[-2:] != '\a\b':
            data = c.recv(1024).decode()
            T_data += data

        if '\a\b' in T_data:
            #print("legal data")
            T_data = T_data[:-2]

        DataList.extend(T_data.split('\a\b'))

    returnData = DataList[0]

    DataList.pop(0)

    DataList = DataList[0:]
    # sleep(1)
    #print("Reteun data is :" + str(returnData))
    return returnData


def GetPosition(data):
    input = data.split()
    position = [int(input[i]) for i in range(1, len(input))]
    print(position)
    return position


if __name__ == '__main__':
    ServerStart()
