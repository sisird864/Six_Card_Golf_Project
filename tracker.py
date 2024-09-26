import socket
import threading
import sys

players = []
games = []

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


sock1.bind((ip_address, 40100))

def register_func(command, addr):
    list1 = command.split(" ")
    for i in players:
        if list1[1] == i[0]:
            print("FAILURE")
            return
    tup1 = (list1[1], list1[2], list1[3], list1[4])
    players.append(tup1)

def deregister_func(command, addr):
    list1 = command.split(" ")
    for i in range(len(players)):
        if players[i][0] == list1[1]:
            players.pop(i)
            return
    print("FAILURE")
    return

def query_players(addr):
    players_str = '\n'.join([' '.join(player) for player in players])
    sock1.sendto(players_str.encode('utf-8'), (addr[0], addr[1]))
    return

def query_games(addr):
    games_str = '\n'.join(games)
    sock1.sendto(games_str.encode('utf-8'), (addr[0], addr[1]))
    return

while True:
    command, addr = sock1.recvfrom(1024)
    command = command.decode('utf-8')
    if command.startswith("register"): register_func(command, addr)
    elif command == "query players": query_players(addr)
    elif command == "query games": query_games(addr)
    elif command.startswith("de-register"): deregister_func(command, addr)
    else: print("Invalid Command!")
