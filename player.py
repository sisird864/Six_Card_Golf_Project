import socket
import threading
import sys
import random

# [Previous code remains the same up to the receive_messages function]

def receive_messages():
    while True:
        message, addr = sock_player.recvfrom(1024)
        message = message.decode('utf-8')

        if message.startswith("PLAYER_INFO"):
            global players_info
            global cards
            global cards_facing_up
            cards_facing_up = set()
            cards = [[], []]
            players_info = message.splitlines()[1:]
            print("\nNew Game Started!\nPlayers in the game:")
            for player in players_info:
                print(player)
            print()  # Add an extra newline for clarity
        elif message.startswith("New Card:"):
            new_card = message.splitlines()[1]
            if len(cards[0]) == 3:
                cards[1].append(new_card)
            else:
                cards[0].append(new_card)
            if len(cards[1]) == 3:
                while True:
                    c = cards[random.randint(0,1)][random.randint(0,2)]
                    if c in cards_facing_up:
                        continue
                    cards_facing_up.add(c)
                    if len(cards_facing_up) == 2:
                        break
                row1 = ""
                for card in cards[0]:
                    if card not in cards_facing_up:
                        row1 += "*** "
                    else:
                        if len(card) == 2:
                            row1 += f" {card} "
                        else:
                            row1 += f"{card} "
                row2 = ""
                for card in cards[1]:
                    if card not in cards_facing_up:
                        row2 += "*** "
                    else:
                        if len(card) == 2:
                            row2 += f" {card} "
                        else:
                            row2 += f"{card} "
                print("\nYour cards:")
                print(row1)
                print(row2)
                print()  # Add an extra newline for clarity
        elif message == "query discard pile":
            discard_pile_top = discard_pile[-1]
            sock_player.sendto(discard_pile_top.encode('utf-8'), (addr[0], addr[1]))
        else:
            print(message)
            print()  # Add an extra newline for clarity

# [Rest of the code remains the same]

# Modify the main loop to prevent "Enter your command here:" from appearing in unwanted places
while True:
    command = input("Enter your command here: ")

    if command.startswith("register") or command == "query players" or command == "query games" or command.startswith("de-register") or command.startswith("start") or command.startswith("end"):
        sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
        message, addr = sock_tracker.recvfrom(1024)
        message = message.decode('utf-8')
        print(message)
        print()  # Add an extra newline for clarity

        if command.startswith("start"):
            players_info = message.splitlines()[2:]
            am_I_dealer = True
            global deck
            global cards
            global discard_pile
            discard_pile = []
            global cards_facing_up
            cards_facing_up = set()
            cards = [[],[]]
            ranks = ['1','2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            suits = ['H', 'D', 'C', 'S']
            deck = [f'{rank}{suit}' for rank in ranks for suit in suits]
            random.shuffle(deck)

            player_list_message = "PLAYER_INFO\n" + "\n".join(players_info)
            for player in players_info[1:]:
                player_info = player.split()
                player_ip = player_info[1]
                player_port = int(player_info[2])
                sock_player.sendto(player_list_message.encode('utf-8'), (player_ip, player_port))
            for i in range(6):
                for player in players_info:
                    player_info = player.split()
                    player_ip = player_info[1]
                    player_port = int(player_info[2])
                    given_card = deck.pop()
                    sock_player.sendto(f"New Card:\n{given_card}".encode('utf-8'), (player_ip, player_port))
            discard_pile.append(deck.pop())

    elif command == "query discard pile":
        player = players_info[0]
        player_info = player.split()
        player_ip = player_info[1]
        player_port = int(player_info[2])
        sock_player.sendto(command.encode('utf-8'), (player_ip, player_port))
    
    else:
        for player in players_info:
            player_info = player.split()
            player_ip = player_info[1]
            player_port = int(player_info[2])
            sock_player.sendto(command.encode('utf-8'), (player_ip, player_port))