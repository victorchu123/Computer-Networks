#!/usr/bin/env python3
#
# COMP 360, Section 1, Fall 2016
# V. Manfredi
#
# Simple echo client that makes a connection to an echo server,
# sends a string to the server, then terminates
#
# Usage:
#   python3 echo_client.py <server_host> <server_port>
#

import socket
import sys

class EchoClient():

    def __init__(self, server_host, server_port, url):
        self.start(server_host, server_port, url)

    def start(self, server_host, server_port, url):

        host_and_path = self.parse_url(url)
        host = host_and_path[0]
        path = host_and_path[1]

        for i in range(1, len(host_and_path)):
            if (host_and_path[1] == ''):
                path = "/"
            else:
                path = host_and_path[1]

        # Try to connect to echo server
        try:
            sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_host, server_port))
        except OSError as e:
            print ('Unable to connect to socket: ', e)
            if sock:
                sock.close()
            sys.exit(1)

        # Send message string to server over socket
        str_msg = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(path, host)

        try:
            bin_msg = str_msg.encode('utf-8')
        except UnicodeEncodeError as e:
            print ('Part of the message was unable to be encoded:', e)

        sock.sendall(bin_msg)

        print ("Printing response from Web Proxy...\r\n")
        print (self.recv_resp(sock).decode('utf-8'))

        # Close server socket
        print ('')
        print("Closing TCP connection with Client...")
        sock.close()

    def recv_resp(self, sock):
        msg = ''
        msg_encoded = msg.encode('utf-8')
        while True:
            received_resp = sock.recv(4096)
            if not received_resp:
                break
            msg_encoded += received_resp
        return msg_encoded

    def parse_url(self, url):
        split_url = url.split('/')
        path = ''
        path_start = 0

        if split_url[0] == 'http:':
            host = split_url[2]
            path_start = 3
        else:
            host = split_url[0]
            path_start = 1

        for i in range(path_start, len(split_url)):
            path += "/"+ split_url[i]

        return [host,path]

def main():

    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50008

    # Parse command line parameters if any
    if len(sys.argv) == 2:
        url = sys.argv[1]
    elif len(sys.argv) > 2:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])
        url = sys.argv[3]

    # Create EchoClient object
    client = EchoClient(server_host, server_port, url)

if __name__ == '__main__':
    main()
