import socket
import threading
import sys
if len(sys.argv) != 5:
    print("invalid command!")
    sys.exit()
tracker_ip = sys.argv[1]
tracker_port = int(sys.argv[2])
player_to_tracker_port = int(sys.argv[3])
player_to_player_port = int(sys.argv[4])

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    sent = sock1.sendto(b'Hello', (tracker_ip, tracker_port))