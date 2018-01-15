import argparse
import socket


def open_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    return sock

def main(args):
    ssl_connect = args.ssl_connect
    hostname = args.hostname
    neu_id = args.neu_id
    port_num = args.port_num

    open_socket(hostname, port_num)

    status_msg = connect_host(sock, neu_id)
    
    has_flag = False
    
    while not has_flag:
        solution = parse_status(status_msg)

        reciept = send_solution(sock, solution)

        has_flag, status_msg = check_receipt(receipt)

    print status_msg

    return


if self.__name__=='__main__':
    parser = argparse.parser()
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('hostname', type=str, action='store',
                            help='Name of the host to connect to.')
    parser.add_argument('neu_id', type=int, action='store',
                            help='the students neu id number to get the secret flag for')
    parser.add_argument('port', '-p', type=int, action='store', default=27998
                            help='the port number to connect to at the host')
    parser.add_argument('ssl_connect', '-s', action='store_true',
                            help='If true use a secure ssl connection')

    args = parser.parseargs()

    main(args)


