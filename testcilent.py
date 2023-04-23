import socket
import sys
from time import sleep

AuthenticationList = [[23019, 32037], [32037, 29295],
                      [18789, 13603], [16443, 29533], [18189, 21952]]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('localhost', 6667))

s.send(sys.argv[1].encode())

print(s.recv(1024).decode())

s.close()
