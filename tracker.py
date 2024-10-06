import socket
import threading
import sys
import random

players = [] # list of tuples to store player information
games = [] # list of tuples to store game information
free_players = set()

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
    free_players.add(tup1[0])
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
    free_players.remove(list1[1])
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
    games_str = '\n'.join([' '.join(map(str, game)) for game in games])
    ret_str = f"{len(games)}\n{games_str}"
    sock1.sendto(ret_str.encode('utf-8'), (addr[0], addr[1]))
    return

#Function to start a game, with the dealer and game id
def start_game(command, addr):
    dealer_tuple = ()
    list1 = command.split(" ")

    # Check if the dealer is registered
    for i in players:
        if i[0] == list1[2]:
            dealer_tuple = i

    # Validate the command's parameters
    if dealer_tuple == () or int(list1[3]) > len(free_players) or (int(list1[3]) < 2 or int(list1[3]) > 4) or (
            int(list1[4]) < 1 or int(list1[4]) > 9):
        sock1.sendto("FAILURE".encode('utf-8'), (addr[0], addr[1]))
        return

    # Generate a unique game ID
    while True:
        game_id = random.randint(0, 999)
        unique = True
        for i in games:
            if i[0] == game_id:
                unique = False
                break
        if unique:
            players_for_game = [dealer_tuple]
            free_players.remove(dealer_tuple[0])

            # Select n random players
            for i in range(int(list1[3])):
                temp = free_players.pop()
                for pl in players:
                    if pl[0] == temp:
                        players_for_game.append(pl)
                        break

            # Add the game to the list of games
            games.append((game_id, list1[2], list1[3], list1[4], players_for_game))

            # Prepare the response string with game ID and players
            response = f"SUCCESS\nGame ID: {game_id}\n"
            response += '\n'.join([f"{pl[0]} {pl[1]} {pl[2]}" for pl in players_for_game])

            # Send the response only to the dealer
            sock1.sendto(response.encode('utf-8'), (dealer_tuple[1], int(dealer_tuple[2])))
            print(free_players)
            return


#Ends a game, checks if there is a game with the game id and dealer in the games list, and removes it from the list if there is
#If the game is not in the list, it returns FAILURE
def end_game(command, addr):
    list1 = command.split(" ")
    for i in games:
        if str(i[0]) == list1[1] and i[1] == list1[2]:
            for p in i[4]:
                free_players.add(p[0])
            games.remove(i)
            sock1.sendto("SUCCESS".encode('utf-8'), (addr[0], addr[1]))
            print(free_players)
            return
    sock1.sendto("FAILURE".encode('utf-8'), (addr[0], addr[1]))
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
    elif command.startswith("end"): end_game(command, addr)
    else: sock1.sendto("Invalid Command!".encode('utf-8'), (addr[0], addr[1]))
