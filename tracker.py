import socket
import threading
import sys

players = {}
games = {}

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


sock1.bind((ip_address, 40100))

while True:
    data, addr = sock1.recvfrom(1024)
    print(data, " ::: ", addr)
