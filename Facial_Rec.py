#!/usr/bin/env python
# Facial Recognition Control and Processing nodes.
import argparse
import lib.caspr_db as caspr_db
import lib.caspr_sockets as caspr_sockets
import cv2
import numpy as np
import os
import pickle
import socket
import struct
import sys
from multiprocessing import Process, Pipe
import Queue

q = Queue.Queue()
server_name = "localhost"
server_port = 12000

image_path = "/home/kofi/Capstone/capstone/images"

# Helper function to send a response to the camera module.
def send_response(data):
    data_string = pickle.dumps(data)
    sender_addr = data['sender_addr']
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((sender_addr, 65000))
    except socket.error,e:
        print 'FRC: Connection to %s on port %s failed: %s' % (sender_addr, 65000, e)
        return

    caspr_sockets.send_data(client_socket, data_string)
    print "FRC: Response sent to camera module."
    client_socket.close()

# Helper function to send a response to the server socket.
def send_server(server_address, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    caspr_sockets.send_data(client_socket, data)
    client_socket.close()
    return 0


# This will call into neural net
def getID_NUM(image):
    _face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = _face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x,y), (x+w,y+h), (0,0,255), 2)

    return len(faces)

# Facial Recognition Processing Node:
#   This node processes the given face image and returns result.
def facial_rec_processor(i, data):
    print "FRP: Facial Recognition Processor received image."
    guid = data['guid']
    hwid = data['hwid']
    timestamp = data['timestamp']
    image1 = data['image']

    # CV2 reads the red and blue channels in reverse
    # Split and merge to reverse
    b, g, r = cv2.split(image1)
    image = cv2.merge([r,g,b])

    image_name = guid + '_processed.png'
    path = os.path.join(image_path, image_name)
    cv2.imwrite(path, image)

    # Get ID_NUM from image being tested.
    ID_NUM = getID_NUM(image)
    # Compare with images in database
    Person = caspr_db.getPersonByID_NUM(ID_NUM)

    result = False
    name = None
    if Person is not None:
        name = Person.LastName + ", " + Person.FirstName
        result = Person.Banned
        caspr_db.postLog(Person.PersonID)

    results = dict(sender_addr=data['sender_addr'],
        req_type='rsl',
        guid=guid,
        hwid=hwid,
        timestamp=timestamp,
        face_found=True,
        name=name,
        banned=result)
    result_buffer = pickle.dumps(results)
    send_server((server_name, server_port), result_buffer)
    return

# Function for handling enrollment into the system.
def facial_rec_enrollment(i, data):
    print "FRE: Facial Recognition Enrollment received image."
    firstName = data['first_name']
    lastName = data['last_name']
    banned = data['banned']
    image = data['image']

    ### Need to crop image

    ID_NUM = getID_NUM(image)

    print "FRE: Saving image..."
    image_name = lastName + firstName[0] + '.png'
    path = os.path.join(image_path, image_name)
    cv2.imwrite(path, image)

    caspr_db.postPerson(ID_NUM, path, banned, firstName, lastName)
    return


# Facial Recognition Control Node:
#   Receives image data from local socket.
#   Queues the data.
#   If the child process is free, send data from queue.
def facial_rec_control(args):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
        server_socket.bind((server_name, server_port))
        server_socket.listen(5)

        child_busy = False
        print "FRC: Facial Recognition Control Node ready to receive."
        print "Hit Ctrl-C to quit."

        while True:
            client_socket, address = server_socket.accept()
            data_buffer = caspr_sockets.recv_data(client_socket)
    
            if data_buffer:
                data = pickle.loads(data_buffer)

                if data['req_type'] == 'enr': # Enrollment
                    print "FRC: Enrollment."
                    child = Process(target=facial_rec_enrollment, args=(0, data))
                    child.start()

                if data['req_type'] == 'req': # Request for process.
                    q.put(data)
                    print "FRC: Request added to queue."

                if data['req_type'] == 'img': # Image to process.
                    child_busy = True
                    print "FRC: Sending image to processor..."
                    child = Process(target=facial_rec_processor, args=(0, data))
                    child.start()

                if data['req_type'] == 'rsl': # Result to send
                    child_busy = False
                    print "FRC: Result received from processor."
                    # --------- Send response to module -----------
                    print "FRC: Sending response to module..."
                    send_response(data)

                if (not child_busy) and (not q.empty()):
                    print "FRC: Sending next request."
                    new_data = q.get()
                    new_data['req_type'] = 'img'
                    new_data_buffer = pickle.dumps(new_data)
                    p = Process(target=send_server, args=((server_name, server_port), new_data_buffer))
                    p.start()

    except KeyboardInterrupt:
        print "Shutting down..."
        sys.exit(0)



# Argument Parser
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Facial recognition parent node')
	args = parser.parse_args()

	facial_rec_control(args)
