#!/usr/bin/env python3
#
# COMP 360, Section 1, Fall 2016
# V. Manfredi
#
# Simple multi-threaded echo server that echos back whatever is sent to it
#
# Usage:
#   python3 echo_server.py <server_host> <server_port>
#

import socket
import sys
import threading
import time
import cache
from time import gmtime, strftime
from datetime import datetime

class EchoServer():

    def __init__(self, server_host, server_port):

        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            server_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.server_host, self.server_port))
            server_sock.listen(self.server_backlog)
        except OSError as e:
            print ('Unable to open socket: ', e)
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Wait for client connection
        while True:
            # Client has connected
            [client_conn, client_addr] = server_sock.accept()
            print ('Client has connected with address: ', client_addr)

            # Create thread to serve client
            thread = threading.Thread(
                    target = self.serve_content,
                    args = (client_conn, client_addr))
            thread.start()

    def serve_content(self, client_conn, client_addr):

        print ('Serving content to client with address', client_addr)

        # Receive data from client
        bin_data = client_conn.recv(1024)

        # Echo back received data to client
        # client_conn.sendall(bin_data)

        # Print data from client
        # print ('Server received', bin_data)

        try:
            get_request = bin_data.decode('utf-8')
        except UnicodeDecodeError as e:
            print ('Part of message was unable to be decoded:', e)

        # print ("GET Request: ", get_request)
        host, path = self.parse_request(get_request)

        if ("http://" in path):
            split_url = path.split("/")
            host = split_url[2]
            path = ''

            for i in range(3, len(split_url)):
                path += '/' + split_url[i]

            get_request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n'.format(path, host)

            try:
                bin_data = get_request.encode('utf-8')
            except UnicodeEncodeError as e:
                print ('Part of message was unable to be encoded:', e)

        print ('HTTP_request:\n' + get_request)

        url = host+path

        # print ('Host:{}\n Path:{}'.format(host, path))

        sock = self.open_HTTP_conn(host)
        time = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

        response = self.get_response(sock, url, time, bin_data, host, path)

        try:
            client_conn.sendall(response) # sends encoded message to server
        except:
            print ("Failed send over whole message.")
            if (client_conn is not None):
                client_conn.close()
        
        if (sock is not None):
            sock.close()

        # Close connection to client
        if (client_conn is not None):
            client_conn.close()

    def get_response(self, sock, url, time, bin_data, host, path):
        # checks if url is in cache already
        if cache.get(url) is not None:
            # conditional get request
            time = cache.get(url)[0]
            try:
                get_request = bin_data.decode('utf-8')
            except UnicodeDecodeError as e:
                print ('Part of message was unable to be decoded:', e)

            get_request_modded = 'GET {} HTTP/1.1\r\nHost: {}\r\nIf-Modified-Since: {}\r\nConnection: Close\r\n\r\n'.format(path, host, time)
            # print ("Modded GET Request: " + str(get_request_modded))

            try:
                bin_request_modded = get_request_modded.encode('utf-8')
            except UnicodeEncodeError as e:
                print ('Part of message was unable to be encoded:', e)

            try:
                sock.sendall(bin_request_modded)
            except AttributeError as e:
                print ("No socket found: ", e)

            response = self.recv_resp(sock)
            new_time = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

            if ("304 Not Modified".encode('utf-8') in response):
                print ("Getting response from cache...")
                return cache.get(url)[1]
            else:
                print ("Returning updated response...")
                cache.set(url, [new_time, response])
                return response            
        else: 
            print ("URL not in cache...")
            try:
                sock.sendall(bin_data)
                response = self.recv_resp(sock)
                cache.set(url, [time, response])
                return response
            except AttributeError as e:
                print ("No socket found: ", e)

    def parse_request(self, get_request):
        host = ''
        path = ''

        try:
            url_split = get_request.split(" ")
            host_arr = get_request.split("Host: ")[1].split(" ")[0].split("\r")
            host = host_arr[0]
            path = url_split[1]

            print ('Host:{} Path:{}'.format(host, path))
        except IndexError as e:
            print ("GET_request cannot be parsed:", e)

        return (host, path)

    def open_HTTP_conn(self, host):
        # Try to connect to host
        try:
            sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host,80))
            return sock
        except OSError as e:
            print ('Unable to connect to socket: ', e)
      
    def recv_resp(self, sock):
        msg = ''
        msg_encoded = msg.encode('utf-8')
        while True:
            received_resp = sock.recv(4096)
            if not received_resp:
                break
            else:
                msg_encoded += received_resp
        return msg_encoded

def main():

    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50009

    # Parse command line parameters if any
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    # Create EchoServer object
    server = EchoServer(server_host, server_port)

if __name__ == '__main__':
    main()
