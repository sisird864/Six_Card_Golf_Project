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

sock_tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket for communicating with the tracker
sock_tracker.bind((ip_address, t_port)) # Assigns port for the socket

sock_player = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket for communicating with other players
sock_player.bind((ip_address, p_port)) # Assigns port for the socket

# Main loop for user to send the messages to the tracker.
# Receives and outputs the messages from the tracker.
while True:
    command = input("Enter your command here: ")
    sent = sock_tracker.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
    message, addr = sock_tracker.recvfrom(1024)
    message = message.decode('utf-8')
    print(message)