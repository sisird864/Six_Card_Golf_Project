import socket
import threading
import sys
import random
from threading import Event
import ast

# ... (keep the initial setup code unchanged)

players_info = []
am_I_dealer = False
game_started = False
my_turn = False
game_end = False

def receive_messages():
    global players_info, cards, cards_facing_up, game_started, my_turn, game_end, discard_pile, deck
    while not game_end:
        message, addr = sock_player.recvfrom(1024)
        message = message.decode('utf-8')

        if message.startswith("PLAYER_INFO"):
            cards_facing_up = set()
            cards = [[], []]
            players_info = message.splitlines()[1:]
            print("\nNew Game Started!\nPlayers in the game:")
            for player in players_info:
                print(player)
            game_started = True

        elif message.startswith("New Card:"):
            new_card = message.splitlines()[1]
            if len(cards[0]) == 3:
                cards[1].append(new_card)
            else:
                cards[0].append(new_card)
            if len(cards[1]) == 3:
                while len(cards_facing_up) < 2:
                    c = cards[random.randint(0,1)][random.randint(0,2)]
                    if c not in cards_facing_up:
                        cards_facing_up.add(c)
                display_cards()

        elif message.startswith("Top of Discard Pile"):
            print(message)

        elif message.startswith("Your Turn"):
            my_turn = True
            lines = message.splitlines()
            discard_pile = ast.literal_eval(lines[1])
            deck = ast.literal_eval(lines[2])
            print(f"\nIt's Your Turn!\n")
            display_cards()
            if len(discard_pile) == 0:
                print("Discard Pile is Empty")
            else:
                print(f"Top of Discard Pile: {discard_pile[-1]}")

            for player in players_info:
                player_info = player.split()
                if player_info[0] != players_info[0].split()[0]:  # Don't send to dealer
                    player_ip = player_info[1]
                    player_port = int(player_info[2])
                    turn_info = f"\nIt's {players_info[0].split()[0]}'s turn:\n"
                    turn_info += get_card_display() + "\n"
                    turn_info += f"Top of Discard Pile: {discard_pile[-1] if discard_pile else 'Empty'}\n"
                    sock_player.sendto(turn_info.encode('utf-8'), (player_ip, player_port))

        elif message.startswith("\nIt's"):
            print(message)

        elif message.startswith("GAME_END"):
            game_end = True
            print("Game has ended.")

        else:
            print(message)

def display_cards():
    print(get_card_display())

def get_card_display():
    row1 = " ".join([f" {card} " if card in cards_facing_up else "*** " for card in cards[0]])
    row2 = " ".join([f" {card} " if card in cards_facing_up else "*** " for card in cards[1]])
    return f"{row1}\n{row2}"

def handle_turn():
    global my_turn, discard_pile, deck, cards, cards_facing_up
    
    from_deck = input("Pick from discard pile or deck: ") != "discard pile"
    my_card = deck.pop() if from_deck else discard_pile.pop()
    print(f"New Card: {my_card}\n")
    
    if from_deck:
        position = input("Enter position of card to replace, or discard: ")
    else:
        position = input("Enter position of card to replace: ")
    
    if position == "discard":
        discard_pile.append(my_card)
    else:
        row_of_card, column_of_card = map(int, position)
        cards[row_of_card][column_of_card] = my_card
        cards_facing_up.add(my_card)
    
    display_cards()
    my_turn = False
    
    # Send updated game state to dealer
    dealer_info = players_info[0].split()
    dealer_ip, dealer_port = dealer_info[1], int(dealer_info[2])
    update_message = f"TURN_COMPLETE\n{discard_pile}\n{deck}"
    sock_player.sendto(update_message.encode('utf-8'), (dealer_ip, dealer_port))

# Start a thread for receiving messages from other players
threading.Thread(target=receive_messages, daemon=True).start()

# Main loop for sending messages to the tracker or other players.
while not game_end:
    if my_turn:
        handle_turn()
    else:
        command = input("Enter your command here: ")

        if command.startswith("register") or command == "query players" or command == "query games" or command.startswith("de-register") or command.startswith("start") or command.startswith("end"):
            sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
            message, addr = sock_tracker.recvfrom(1024)
            message = message.decode('utf-8')
            print(message)

            if command.startswith("start"):
                players_info = message.splitlines()[2:]
                am_I_dealer = True
                game_started = True
                deck = [f'{rank}{suit}' for rank in ['1','2','3','4','5','6','7','8','9','10','J','Q','K'] for suit in ['H','D','C','S']]
                random.shuffle(deck)
                discard_pile = []

                player_list_message = "PLAYER_INFO\n" + "\n".join(players_info)
                for player in players_info[1:]:
                    player_info = player.split()
                    player_ip, player_port = player_info[1], int(player_info[2])
                    sock_player.sendto(player_list_message.encode('utf-8'), (player_ip, player_port))

                for _ in range(6):
                    for player in players_info:
                        player_info = player.split()
                        player_ip, player_port = player_info[1], int(player_info[2])
                        given_card = deck.pop()
                        sock_player.sendto(f"New Card:\n{given_card}".encode('utf-8'), (player_ip, player_port))

                discard_pile.append(deck.pop())
                give_discard_pile = f"\nTop of Discard Pile: {discard_pile[-1]}\n"
                for player in players_info:
                    player_info = player.split()
                    player_ip, player_port = player_info[1], int(player_info[2])
                    sock_player.sendto(give_discard_pile.encode('utf-8'), (player_ip, player_port))

                command_list = command.split(" ")
                num_holes = int(command_list[4])
                for _ in range(num_holes):
                    for player in players_info:
                        player_info = player.split()
                        player_ip, player_port = player_info[1], int(player_info[2])
                        turn_message = f"Your Turn\n{discard_pile}\n{deck}\n{player_info[0]}\n"
                        sock_player.sendto(turn_message.encode('utf-8'), (player_ip, player_port))
                        update_message, _ = sock_player.recvfrom(1024)
                        update_lines = update_message.decode('utf-8').splitlines()
                        if update_lines[0] == "TURN_COMPLETE":
                            discard_pile = ast.literal_eval(update_lines[1])
                            deck = ast.literal_eval(update_lines[2])

                # End the game after all rounds
                for player in players_info:
                    player_info = player.split()
                    player_ip, player_port = player_info[1], int(player_info[2])
                    sock_player.sendto("GAME_END".encode('utf-8'), (player_ip, player_port))
                game_end = True

        elif game_started:
            print("Game is in progress. Please wait for your turn.")
        else:
            for player in players_info:
                player_info = player.split()
                player_ip = player_info[1]
                player_port = int(player_info[2])
                sock_player.sendto(command.encode('utf-8'), (player_ip, player_port))

print("Game has ended. Exiting...")