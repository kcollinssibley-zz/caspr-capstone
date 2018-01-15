# This will be used to "send" dummy images to the control node for testing
# using http
# send face and body image to control node

import argparse
import cv2
import httplib
import numpy as np
import os
import time
import uuid

def main(args):
    hw_id = 194
    server_name = args.server_name
    port_num = args.port_num
    
    # Establish connection
    connection = httplib.HTTPConnection(server_name, port_num)
    print "Connection to server established."

    # Read in image
    filename = args.s_filename # this is dummy code
    ext = os.path.splitext(filename)[1]
    GUID = str(uuid.uuid4())

    headers = {'Content-type': 'image/png', 'GUID': GUID, 'hw_id': hw_id, 'time_stamp': time.time()}
    try:
        image = cv2.imread(filename)
        if image is not None:
            retval, _buffer = cv2.imencode(ext, image)
            print "Image read."

            # Send image
            try:
                connection.request('POST', '/upload', _buffer, headers)
                print "Image sent."

                # Get response
                response = connection.getresponse()
                print(response.read(), response.status, response.reason)
            except Exception as e:
                print str(e)
        else:
            print('[Error]: image not valid')
    except Exception as e:
        print str(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send dummy image to control node')
    parser.add_argument('server_name', type=str, help='Name of server to connect to.')
    parser.add_argument('port_num', type=int, help='Port number of server.')
    parser.add_argument('s_filename', type=str, help='filename of image to be sent')
    args = parser.parse_args()

    main(args)
