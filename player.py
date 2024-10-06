import socket
import threading
import sys

# Checks if the player started the program with the correct parameters.
if len(sys.argv) != 5:
    print("Invalid command! Usage: <tracker_ip> <tracker_port> <t_port> <p_port>")
    sys.exit()

# Command-line arguments for the tracker and player ports
tracker_ip = sys.argv[1]
tracker_port = int(sys.argv[2])
t_port = int(sys.argv[3])
p_port = int(sys.argv[4])

# Get the player's local IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Create a UDP socket for communicating with the tracker
sock_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_tracker.bind((ip_address, t_port))

# Create a UDP socket for communicating with other players
sock_player = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_player.bind((ip_address, p_port))


# Function to listen for incoming messages from other players
def listen_to_players():
    while True:
        try:
            message, addr = sock_player.recvfrom(1024)
            message = message.decode('utf-8')
            print(f"Received from {addr}: {message}")
            # Here you can handle game-specific logic (e.g., card draws, moves)
        except Exception as e:
            print(f"Error receiving message: {e}")


# Start a thread to listen for player messages
player_thread = threading.Thread(target=listen_to_players)
player_thread.daemon = True  # This will ensure the thread closes when the main program exits
player_thread.start()

# Main loop for sending commands to the tracker and receiving messages
while True:
    command = input("Enter your command here: ")
    sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))

    # Receive and print the response from the tracker
    message, addr = sock_tracker.recvfrom(1024)
    message = message.decode('utf-8')
    print(f"Tracker response: {message}")

    # Handle any specific game-related messages from the tracker
    if message.startswith("SUCCESS"):  # Example case, adjust as needed
        print("Game started successfully! Waiting for further instructions...")
        # You can add additional logic here for when the game starts

# Additional logic can be added for game-specific commands, moves, etc.
