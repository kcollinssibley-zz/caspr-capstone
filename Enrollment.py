#!/usr/bin/env python
# Script used to enroll person into database

import argparse
import cv2
import httplib
import numpy as np
import pickle
import os
import socket
import time
import lib.caspr_ip as caspr_ip
import lib.caspr_sockets as caspr_sockets

def receive_response(server_name):
    module_address = caspr_ip.get_ip_address('lo')
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
            data = pickle.loads(data_buffer)

            if data['req_type'] == 'enr_rsl':
            	if data['person_created'] == True:
                    print "CM: %s %s enrolled" % (data['first_name'], data['last_name'])
                else:
                    print "CM: No person created."
    return 0


def main(args):
	server_name = args.server_name
	port_num = args.port_num

	connection = httplib.HTTPConnection(server_name, port_num)
	print "Connection to server established."

	first = args.first_name
	last = args.last_name
	banned = args.banned

	filename = args.image_path
	ext = os.path.splitext(filename)[1]

	headers = { 'Content-type': 'image/png',
	'first_name': first,
	'last_name': last,
	'banned': banned }

	try:
		image1 = cv2.imread(filename)
		r, g, b = cv2.split(image1)
		image = cv2.merge([b,g,r])

		if image is not None:
			_buffer = pickle.dumps(image)
			print "Image read."

			try:
				connection.request('POST', '/enroll', _buffer, headers)
				print "Image sent."

				response = connection.getresponse()
				print(response.read(), response.status, response.reason)
				receive_response(server_name)
			except Exception as e:
				print str(e)
		else:
			print "[Error]: image not valid"
	except Exception as e:
		print str(e)

	return 0


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Enroll person into database.')
	parser.add_argument('server_name', type=str, help='Name of server to connect to.')
	parser.add_argument('port_num', type=int, help='Port number of server.')
	parser.add_argument('first_name', type=str, help='First name of person.')
	parser.add_argument('last_name', type=str, help='Last name of person.')
	parser.add_argument('banned', type=int, help='Is this person banned (1)yes/(0)no.')
	parser.add_argument('image_path', type=str, help='Image path.')
	args = parser.parse_args()

	main(args)
