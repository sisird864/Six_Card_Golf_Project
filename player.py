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

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a UDP socket

# Main loop for user to send the messages to the tracker.
# Receives and outputs the messages from the tracker.
while True:
    command = input("Enter your command here: ")
    sent = sock1.sendto(command.encode('utf-8'), (tracker_ip, tracker_port))
    message, addr = sock1.recvfrom(1024)
    message = message.decode('utf-8')
    print(message)