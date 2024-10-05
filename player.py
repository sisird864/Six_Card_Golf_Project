import socket
import threading
import sys
# Checks if the player started the program with the correct parameters.
if len(sys.argv) != 3:
    print("invalid command!")
    sys.exit()

# The parameters that need to be provided are the tracker's ip address and the port number that the tracker uses.
tracker_ip = sys.argv[1]
tracker_port = int(sys.argv[2])

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

sock_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket for communicating with the tracker
sock_tracker.bind((ip_address, 40200)) # Uses port 40200 for the socket

sock_player = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket for communicating with other players
sock_player.bind((ip_address, 40300)) # Uses port 40300 for the socket

# Main loop for user to send the messages to the tracker.
# Receives and outputs the messages from the tracker.
while True:
    command = input("Enter your command here: ")
    sent = sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
    message, addr = sock_tracker.recvfrom(1024)
    message = message.decode('utf-8')
    print(message)