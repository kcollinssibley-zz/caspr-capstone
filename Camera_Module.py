#!/usr/bin/env python
# This will be used to send images to the control node for testing
# using http
# send face and body image to control node

import argparse
import base64
import lib.caspr_ip as caspr_ip
import lib.caspr_lights as caspr_lights
import lib.caspr_sockets as caspr_sockets
import httplib
import numpy as np
import picamera
import picamera.array
import pickle
import os
import socket
import sys
import time
import uuid
from blinkt import set_pixel, set_brightness, show, clear
from multiprocessing import Process, Pipe

# Receive imaging response from the server.
def receive_response(server_name, lights_process):
    module_address = caspr_ip.get_ip_address('wlan0')
    if module_address is None:
        module_address = caspr_ip.get_ip.address('eth0')
    elif module_address is None:
        print "Not connected"
        return 0

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((module_address, 65000))
    server_sock.listen(5)

    response = False
    while response == False:
        client_sock, address = server_sock.accept()
        data_buffer = caspr_sockets.recv_data(client_sock)

        if data_buffer:
            response = True
            lights_process.terminate()
            data = pickle.loads(data_buffer)

            if data['req_type'] == 'rec_rsl':
                if data['face_found'] == True:
                    if data['name'] is not None:
                        print "CM: %s detected." % (data['name'])
                        print "CM: Banned?", data['banned']
                        if data['banned'] == True:
                            caspr_lights.set_all('red')
                        else:
                            caspr_lights.set_all('green')
                    else:
                        print "CM: Face not recognized."
                        caspr_lights.set_all('yellow')
                else:
                    print "CM: No face detected."
                    caspr_lights.set_all('red')

            elif data['req_type'] == 'enr_rsl':
                if data['person_created'] == True:
                    print "CM: %s %s enrolled" % (data['first_name'], data['last_name'])
                    caspr_lights.set_all('green')
                else:
                    print "CM: No person created."
                    caspr_lights.set_all('red')
            show()
            time.sleep(1)
    return 0


def main(args):
    try:
        hw_id = 194
        server_name = args.server_name
        port_num = args.port_num

        print "CM: Camera Module."
        print "Hit Ctrl-C to quit."

        # Establish connection
        clear()
        caspr_lights.set_led(0, 'red')
        connection = httplib.HTTPConnection(server_name, port_num)
        caspr_lights.set_led(0, 'blue')
        print "CM: Connection to server established."
    
        # Initialize Camera
        caspr_lights.set_led(1, 'red')
        camera = picamera.PiCamera()
        camera.resolution = (736, 640)
        camera.framerate = 24
        camera.rotation = 270
        caspr_lights.set_led(1, 'blue')
        print "CM: Camera initialized."
        
        while True:
            mode_input = raw_input("CM: Press [0] for enrollment mode."+
                "\nCM: Press [1] for security mode.\n")

            if mode_input == '0':
                mode = 'enrollment' 
                break
            if mode_input == '1':
                mode = 'security'  
                break


        while True:
            # Show blue light to show camera is ready.
            caspr_lights.set_all('blue')
            print "CM: Mode: " + mode
            input_ = raw_input("CM: Press Enter to take picture." +
                "\nCM: Press Any other key to switch modes.\n")

            # If the user presses enter, take and send picture
            if input_ == "":
                if mode == 'enrollment':
                    route = '/enroll'
                    first_name = raw_input("Enter First name: ")
                    last_name = raw_input("Enter Last name: ")
                    banned = input("Banned? [1]yes/[0]no.")
                    headers = { 'Content-type': 'image/png',
                            'first_name': first_name,
                            'last_name': last_name,
                            'banned': banned }
                if mode == 'security':
                    route = '/upload'
                    GUID = str(uuid.uuid4())
                    headers = { 'Content-type': 'image/png',
                            'GUID': GUID,
                            'hw_id': hw_id,
                            'time_stamp': time.time() }

                # Camera flash
                caspr_lights.flash()

                # Take picture
                image = picamera.array.PiRGBArray(camera)
                camera.capture(image, 'rgb')

                # Clear flash
                lights_process = Process(target=caspr_lights.rand_rainbow)
                lights_process.start()

                if image is not None:
                    _buffer = pickle.dumps(image.array)
                    print "CM: Image buffer created."

                    # Send image
                    try:
                        connection.request('POST', route, _buffer, headers)
                        print "CM: Image sent."

                        # Get response
                        response = connection.getresponse()
                        if response.status == 200:
                            print "CM: Image received by server."
                            receive_response(server_name, lights_process)

                    except Exception as e:
                        print str(e)
                else:
                    print('CM: [Error]: image not valid')
            else:
                if mode == 'enrollment':
                    mode = 'security'
                    continue
                if mode == 'security':
                    mode = 'enrollment'
                    continue

    except KeyboardInterrupt:
        print "\nCM: Shutting down..."
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send image to control node')
    parser.add_argument('server_name', type=str, help='Name of server to connect to.')
    parser.add_argument('port_num', type=int, help='Port number of server.')
    args = parser.parse_args()

    main(args)
