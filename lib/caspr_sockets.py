# Sockets library for communications within the CASPR application.
import struct
import socket

def send_data(socket, data):
    # Prefix each message with a 4-byte length (network byte order)
    data = struct.pack('>I', len(data)) + data
    socket.sendall(data)

def recv_data(socket):
    # Read data length and unpack it into an int
    raw_datalen = recvall(socket, 4)
    if not raw_datalen:
        return None
    datalen = struct.unpack('>I', raw_datalen)[0]
    # Read the data
    return recvall(socket, datalen)

def recvall(socket, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = socket.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
