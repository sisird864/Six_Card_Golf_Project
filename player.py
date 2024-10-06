import socket
import threading
import sys

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

sock_tracker = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)  # Creates a UDP socket for communicating with the tracker
sock_tracker.bind((ip_address, t_port))  # Assigns port for the socket

sock_player = socket.socket(socket.AF_INET,
                            socket.SOCK_DGRAM)  # Creates a UDP socket for communicating with other players
sock_player.bind((ip_address, p_port))  # Assigns port for the socket

# Store player information after starting the game
players_info = []


def receive_messages():
    while True:
        message, addr = sock_player.recvfrom(1024)
        message = message.decode('utf-8')
        print(f"Received from {addr}: {message}")


# Start the thread for receiving messages from other players
threading.Thread(target=receive_messages, daemon=True).start()

# Main loop for user to send the messages to the tracker or other players.
while True:
    command = input("Enter your command here: ")

    # Check if it's a command for the tracker
    if command.startswith("start") or command == "query players" or command == "query games" or command.startswith("de-register") or command.startswith("start") or command.startswith("end"):
        sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
        message, addr = sock_tracker.recvfrom(1024)
        message = message.decode('utf-8')
        print(message)

        # If the game starts successfully, receive the players' information
        if message.startswith("SUCCESS"):
            players_info = message.splitlines()[1:]  # Assuming player info starts from the second line
            print("Players in the game:")
            for player in players_info:
                print(player)

    else:
        # If the game has started, allow interaction with other players
        for player in players_info:
            player_info = player.split()
            player_ip = player_info[1]
            player_port = int(player_info[2])
            sock_player.sendto(command.encode('utf-8'), (player_ip, player_port))
