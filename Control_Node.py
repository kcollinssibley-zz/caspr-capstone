#!/usr/bin/env python
# Controls the flow of data from the module to the facial recognition software

import argparse
import lib.caspr_sockets as caspr_sockets
import cv2
import numpy as np
import os
import pickle
import socket
from bottle import Bottle, run, route, request
from multiprocessing import Process, Pipe

facial_rec_name = "localhost"
facial_rec_port = 12000

def enroll_person(sender_addr, first_name, last_name, banned, image_buffer):
    image = pickle.loads(image_buffer)

    data = dict(sender_addr=sender_addr,
        req_type='enr',
        first_name=first_name,
        last_name=last_name,
        banned=banned,
        image=image)
    data_string = pickle.dumps(data)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((facial_rec_name, facial_rec_port))
    except socket.error,e:
        print 'EP: Connection to %s on port %s failed: %s' % (facial_rec_name, facial_rec_port, e)
        return

    caspr_sockets.send_data(client_socket, data_string)
    print "EP: Enrollment data send to FRC."
    client_socket.close()
    return 0

# Control Child:
#   Child process to receive data from the main controller.
#   When data received:
#       Send data over local socket to Facial Recognition node.
def process_image(sender_addr, GUID, hw_id, timestamp, _buffer):
    # Recreate image here to avoid stringifying the stringified image.
    # This was causing issues with pickle...
    image = pickle.loads(_buffer)

    # Convert data to a dictionary object
    data = dict(sender_addr=sender_addr,
        req_type='req',
        guid=GUID,
        hwid=hw_id,
        timestamp=timestamp,
        image=image)
    # Convert to string buffer
    data_string = pickle.dumps(data)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((facial_rec_name, facial_rec_port))
    except socket.error,e:
        print 'PI: Connection to %s on port %s failed: %s' % (facial_rec_name, facial_rec_port, e)
        return

    print "PI: Sub-process connected to Facial Recognition Control Node via socket."

    caspr_sockets.send_data(client_socket, data_string)
    print "PI: Image data sent to FRC."
    client_socket.close()
    return



# Main Control Node:
#    Receives HTTP(s) posts from camera modules.
#    When a post is received:
#        Creates a process (control_child) and hands off the post data
#        Goes back to listening for HTTP(s)
def control_node(args):
    # Initialize Bottle server
    server_node = Bottle()

    # Grab server info from args
    host_name = args.host_name
    port_num = args.port_num

    # -------------------------Server Routes-----------------------------------
    @server_node.route('/upload', method='POST')
    def do_upload():
        # Grab data from HTTP request
        sender_addr = request.remote_addr
        GUID = request.headers['GUID']
        hw_id = request.headers['HW-ID']
        timestamp = request.headers['time-stamp']
        _buffer = request.body.read()

        print "CN: Image received from hw_id: ", hw_id
        
        # Create child process, send data, start process, go back to listening.
        p = Process(target=process_image, args=(sender_addr, GUID, hw_id, timestamp, _buffer))
        p.start()
        print "CN: Sub-process created. Listening for new connection..."

        # Return receipt of image... Can't wait to return response because
        # control node needs to continue listening.
        return "CN: Image Received. Processing..."

    @server_node.route('/enroll', method='POST')
    def enroll():
        sender_addr = request.remote_addr
        first_name = request.headers['first_name']
        last_name = request.headers['last_name']
        banned = request.headers['banned']
        _buffer = request.body.read()

        print "CN: Enrollment image recieved."

        p = Process(target=enroll_person, args=(sender_addr, first_name, last_name, banned, _buffer))
        p.start()
        print "CN: Sub-process created. Listening for new connection..."

        return "CN: Enrollment Received. Processing..."

    # Run server
    run(server_node, host=host_name, port=port_num, debug=True)
 


# Argument Parser:
#    Parses command line arguments to create Control Node.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control node for CASPR image processing server.')
    parser.add_argument('host_name', type=str, help='IP address for host.')
    parser.add_argument('port_num', type=int, help='Port number to listen on.')
    args = parser.parse_args()

    control_node(args)
