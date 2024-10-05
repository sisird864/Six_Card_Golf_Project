import socket
import threading
import sys
import random

players = [] # list of tuples to store player information
games = [] # list of tuples to store game information

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


sock1.bind((ip_address, 40100)) # Uses port 40100 for the socket

# Function to register a player.
# Adds the player to the players list and returns SUCCESS to the player if the player is not already registered.
# Otherwise, returns FAILURE to the player if the player is already registered
def register_func(command, addr):
    list1 = command.split(" ")
    for i in players:
        if list1[1] == i[0]:
            sock1.sendto("FAILURE".encode('utf-8'), (addr[0], addr[1]))
            return
    tup1 = (list1[1], list1[2], list1[3], list1[4])
    players.append(tup1)
    sock1.sendto("SUCCESS".encode('utf-8'), (addr[0], addr[1]))
    return

# Function to de-register a player.
# Removes the player from the players list and returns SUCCESS to the player if the player is registered.
# Otherwise, returns FAILURE to the player if the player is not registered
def deregister_func(command, addr):
    list1 = command.split(" ")
    for i in range(len(players)):
        if players[i][0] == list1[1]:
            players.pop(i)
            sock1.sendto("SUCCESS".encode('utf-8'), (addr[0], addr[1]))
            return
    sock1.sendto("FAILURE".encode('utf-8'), (addr[0], addr[1]))
    return

# Returns the amount of registered players as well as each registered player's information to the player.
def query_players(addr):
    players_str = '\n'.join([' '.join(player) for player in players])
    ret_str = f"{len(players)}\n{players_str}"
    sock1.sendto(ret_str.encode('utf-8'), (addr[0], addr[1]))
    return

# Returns the amount of games as well as each games' information to the player
def query_games(addr):
    games_str = '\n'.join([' '.join(game) for game in games])
    ret_str = f"{len(games)}\n{games_str}"
    sock1.sendto(ret_str.encode('utf-8'), (addr[0], addr[1]))
    return

def start_game(command, addr):
    dealer_tuple = ()
    list1 = command.split(" ")
    for i in players:
        if i[0] == list1[2]:
            dealer_tuple = i
    if dealer_tuple == ():
        sock1.sendto("FAILURE".encode('utf-8'), (addr[0], addr[1]))
        return
    while True:
        game_id = random.randint(0, 999)
        unique = True
        for i in games:
            if i[0] == game_id:
                unique = False
                break
        if unique:
            games.append((game_id, list1[2], list1[3], list1[4]))
            sock1.sendto("SUCCESS".encode('utf-8'), (addr[0], addr[1]))
            return



# Main loop to receive messages from players and calls the appropriate functions for each command that was received from the player
while True:
    command, addr = sock1.recvfrom(1024)
    command = command.decode('utf-8')
    if command.startswith("register"): register_func(command, addr)
    elif command == "query players": query_players(addr)
    elif command == "query games": query_games(addr)
    elif command.startswith("de-register"): deregister_func(command, addr)
    elif command.startswith("start"): start_game(command, addr)
    else: sock1.sendto("Invalid Command!".encode('utf-8'), (addr[0], addr[1]))
