#!/usr/bin/env python3
#
# COMP 360, Section 1, Fall 2016
# Victor Chu
#
# This is a client that makes a TCP connection to a web proxy,
# sends a get HTTP request to the server, and prints out the 
# HTTP response from the Web Proxy.
#

import socket
import sys

class EchoClient():

    def __init__(self, server_host, server_port, url):
        self.start(server_host, server_port, url)

    def start(self, server_host, server_port, url):
        host, path = self.parse_url(url)  # parses whole url received into host and path

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

        # HTTP GET Request to send to Web Proxy over the socket
        str_msg = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(path, host)

        try:
            bin_msg = str_msg.encode('utf-8')
        except UnicodeEncodeError as e:
            print ('Part of the message was unable to be encoded:', e)

        try:
            sock.sendall(bin_msg) # sends HTTP GET Request
        except Exception as e:
            print ("GET Request failed to send:", e)
            
        # receives and prints out the HTTP Response from Web Proxy 
        print ("Printing response from Web Proxy...\r\n")
        print (self.recv_resp(sock).decode('utf-8'))

        # Close server socket
        print ('')
        print("Closing TCP connection with Client...")
        sock.close()

    # Purpose & Behavior: Receives Proxy HTTP Response
    # Input: Socket that you want to receive a response from.
    # Output: An utf-8 encoded HTTP response.
    def recv_resp(self, sock):
        msg = ''
        try: 
            msg_encoded = msg.encode('utf-8') # encodes ascii empty string to binary empty string
        except UnicodeEncodeError as e:
            print ('Part of message was unable to be encoded:', e)

        while True:
            received_resp = sock.recv(4096)
            # breaks out if we recv no data
            if not received_resp:
                break
            msg_encoded += received_resp
        return msg_encoded

    # Purpose & Behavior: Parses url into a proper host and path; accounts for 'http://''
    # and 'www.' urls.
    # Input: URL that you want to parse.
    # Output: Corresponding host and path.
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

        # handles the case if path is empty
        if (path == ''):
            path = "/"

        return (host,path)

def main():
    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50008

    # Parse command line parameters if any
    if len(sys.argv) == 2:
        url = sys.argv[1]
    elif len(sys.argv) > 2:
        url = sys.argv[1]
        server_host = int(sys.argv[2])
        server_port = sys.argv[3]

    # Create EchoClient object
    client = EchoClient(server_host, server_port, url)

if __name__ == '__main__':
    main()
