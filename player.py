import socket
import threading
import sys
import random
from threading import Event
import ast
import time


# Checks if the player started the program with the correct parameters.
if len(sys.argv) != 5:
    print("invalid command!")
    sys.exit()


# The parameters that need to be provided are the tracker's ip address and the port number that the tracker uses.
tracker_ip = sys.argv[1]
tracker_port = int(sys.argv[2])
t_port = int(sys.argv[3])
p_port = int(sys.argv[4])


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


sock_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket for tracker communication
sock_tracker.bind((ip_address, t_port))  # Assigns port for the socket


sock_player = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket for peer-to-peer communication
sock_player.bind((ip_address, p_port))  # Assigns port for the socket


# Store player information after starting the game
players_info = []
am_I_dealer = False
game_started = False
print_ready = Event()
turn_ready = Event()
my_turn = Event()
cards_up_event = Event()


def receive_messages():
    #global print_ready, game_started
    while True:
        message, addr = sock_player.recvfrom(1024)
        message = message.decode('utf-8')
        #print(f"Received from {addr}: {message}")


        # Check if the message contains player information (broadcasted by the dealer)
        if message.startswith("PLAYER_INFO"):
            global players_info
            global cards
            global cards_facing_up
            cards_facing_up = set()
            cards = [[], []]
            players_info = message.splitlines()[1:]  # Store player information from the broadcast
            print("\nNew Game Started!\nPlayers in the game:")
            for player in players_info:
                print(player)
            game_started = True
            print_ready.set()
        elif message.startswith("New Card:"):
            new_card = message.splitlines()[1]
            if len(cards[0]) == 3:
                cards[1].append(new_card)
            else: cards[0].append(new_card)
            if len(cards[1]) == 3:
                while True:
                    c = cards[random.randint(0,1)][random.randint(0,2)]
                    if c in cards_facing_up:
                        continue
                    cards_facing_up.add(c)
                    if len(cards_facing_up) == 2: break
                row1 = ""
                for card in cards[0]:
                    if card not in cards_facing_up: row1 += "*** "
                    else:
                        if len(card) == 2: row1 += f" {card} "
                        else: row1 += f"{card} "
                row2 = ""
                for card in cards[1]:
                    if card not in cards_facing_up:
                        row2 += "*** "
                    else:
                        if len(card) == 2:
                            row2 += f" {card} "
                        else:
                            row2 += f"{card} "
                print(row1)
                print(row2)
        elif message.startswith("Top of Discard Pile"):
            print(message)
            print_ready.set()
       
        elif message.startswith("Your Turn"):
            my_turn.set()
            my_name = message.splitlines()[3]
            discard_pile = message.splitlines()[1]
            discard_pile = ast.literal_eval(discard_pile)
            deck = message.splitlines()[2]
            deck = ast.literal_eval(deck)
            print(deck)
            print(discard_pile)
            if len(discard_pile) == 0: discard_pile_top = "Discard Pile is Empty"
            else: discard_pile_top = f"Top of Discard Pile: {discard_pile[-1]}"
            print(f"\nIt's Your Turn!\n")
            row1 = ""
            for card in cards[0]:
                if card not in cards_facing_up: row1 += "*** "
                else:
                    if len(card) == 2: row1 += f" {card} "
                    else: row1 += f"{card} "
            row2 = ""
            for card in cards[1]:
                if card not in cards_facing_up:
                    row2 += "*** "
                else:
                    if len(card) == 2:
                        row2 += f" {card} "
                    else:
                        row2 += f"{card} "
            print(row1)
            print(row2)
            print(discard_pile_top)
            for player in players_info:
                player_info = player.split()
                if player_info[0] == my_name: continue
                player_ip = player_info[1]
                player_port = int(player_info[2])
                sock_player.sendto(f"\nIt's {my_name}'s turn:\n{row1}\n{row2}\n{discard_pile_top}\n".encode('utf-8'), (player_ip, player_port))
           
            from_deck = False
            c = input("Pick from discard pile or deck: ")
            if c == "discard pile": my_card = discard_pile.pop()
            else:
                my_card = deck.pop()
                from_deck = True
            print(f"New Card: {my_card}\n")
            if from_deck: position = input("Enter position of card to replace, or discard: ")
            else: position = input("Enter position of card to replace: ")
            if position == "discard":
                discard_pile.append(my_card)
            else:
                row_of_card = int(position[0])
                column_of_card = int(position[1])
                cards[row_of_card][column_of_card] = my_card
                cards_facing_up.add(cards[row_of_card][column_of_card])
           
            row1 = ""
            for card in cards[0]:
                if card not in cards_facing_up: row1 += "*** "
                else:
                    if len(card) == 2: row1 += f" {card} "
                    else: row1 += f"{card} "
            row2 = ""
            for card in cards[1]:
                if card not in cards_facing_up:
                    row2 += "*** "
                else:
                    if len(card) == 2:
                        row2 += f" {card} "
                    else:
                        row2 += f"{card} "
            print(row1)
            print(row2)

            player_info_d = players_info[0].split()
            player_ip_d = player_info_d[1]
            player_port_d = int(player_info_d[2])
            sock_player.sendto(f"Turn Finished\n{deck}\n{discard_pile}".encode('utf-8'), (player_ip_d, player_port_d))

            #turn_ready.set()
            my_turn.clear()
            print_ready.set()
        elif message.startswith("\nIt's"):
            print(message)
        elif message.startswith("Turn Finished"):
            deck = ast.literal_eval(message.splitlines()[1])
            discard_pile = ast.literal_eval(message.splitlines()[2])
            print(deck)
            print(discard_pile)
            global send_deck
            send_deck = list(deck)
            global send_discard_pile
            send_discard_pile = list(discard_pile)
            #turn_ready.set()
            cards_up_event.set()
        elif message == "Cards Up":
            player_info_d = players_info[0].split()
            player_ip_d = player_info_d[1]
            player_port_d = int(player_info_d[2])
            sock_player.sendto((f"Num_Up\n{my_name}\n"+str(len(cards_facing_up))).encode('utf-8'), (player_ip_d, player_port_d))
        elif message.startswith("Num_Up"):
            cards_up_dict[message.splitlines()[1]] = message.splitlines()[2]
            turn_ready.set()
        else:
            print(message)
            print_ready.set()




# Start a thread for receiving messages from other players
threading.Thread(target=receive_messages, daemon=True).start()


# Main loop for sending messages to the tracker or other players.
while True:
    if game_started:
        print_ready.wait()
        print_ready.clear()
    if my_turn.is_set():
        time.sleep(20)
        #turn_ready.set()
    command = input("Enter your command here: ")


    # Check if it's a command for the tracker
    if command.startswith("register") or command == "query players" or command == "query games" or command.startswith("de-register") or command.startswith("start") or command.startswith("end"):
        sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
        message, addr = sock_tracker.recvfrom(1024)
        message = message.decode('utf-8')
        print(message)


        # If the game starts successfully and you're the dealer
        if command.startswith("start"):
            players_info = message.splitlines()[2:]  # Assume player info starts from the second line
            am_I_dealer = True
            game_started = True
            global deck
            global cards
            global discard_pile
            discard_pile = []
            global cards_facing_up
            cards_facing_up = set()
            cards = [[],[]]
            ranks = ['1','2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            suits = ['H', 'D', 'C', 'S']
            # Create the deck by combining each rank with each suit
            deck = [f'{rank}{suit}' for rank in ranks for suit in suits]
            # Shuffles the deck
            random.shuffle(deck)


            # Broadcast player information to all other players
            player_list_message = "PLAYER_INFO\n" + "\n".join(players_info)
            for player in players_info[1:]:  # Skip the first entry (dealer)
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
            give_discard_pile = f"\nTop of Discard Pile: {discard_pile[-1]}\n"
            for player in players_info:
                player_info = player.split()
                player_ip = player_info[1]
                player_port = int(player_info[2])
                sock_player.sendto(give_discard_pile.encode('utf-8'), (player_ip, player_port))
            command_list = command.split(" ")
            num_holes = int(command_list[4])
            all_cards_are_up = False
            cards_up_dict = dict()
            for i in range(num_holes):
                while all_cards_are_up == False:
                    player_info = players_info[-1].split()
                    player_ip = player_info[1]
                    player_port = int(player_info[2])
                    sock_player.sendto(f"Your Turn\n{discard_pile}\n{deck}\n{player_info[0]}\n".encode('utf-8'), (player_ip, player_port))
                    cards_up_event.wait()
                    cards_up_event.clear()
                    sock_player.sendto("Cards Up".encode('utf-8'), (player_ip, player_port))
                    turn_ready.wait()
                    turn_ready.clear()
                    for j in range(len(players_info)-1):
                        player_info2 = players_info[j].split()
                        player_ip2 = player_info2[1]
                        player_port2 = int(player_info2[2])
                        sock_player.sendto(f"Your Turn\n{send_discard_pile}\n{send_deck}\n{player_info2[0]}\n".encode('utf-8'), (player_ip2, player_port2))
                        cards_up_event.wait()
                        cards_up_event.clear()
                        sock_player.sendto("Cards Up".encode('utf-8'), (player_ip2, player_port2))
                        turn_ready.wait()
                        turn_ready.clear()
                    if all(val == "6" for val in cards_up_dict.values()):
                        all_cards_are_up = True
                    else:
                        all_cards_are_up = False




   
    else:
        # If the game has started, allow interaction with other players
        for player in players_info:
            player_info = player.split()
            player_ip = player_info[1]
            player_port = int(player_info[2])
            sock_player.sendto(command.encode('utf-8'), (player_ip, player_port))