#!/usr/bin/env python3
#
# COMP 360, Section 1, Fall 2016
# Victor Chu
#
# This is a Web Proxy that:
# 1. Receives a HTTP GET Request from the Client.
# 2. Extracts URL from HTTP GET Request, checks if the URL 
# is in the cache, and creates an appropriate HTTP request
# to send to the Web Server.
# 3. Sends the HTTP Request to the Web Server.
# 4. Receives HTTP Response from Web Server.
# 5. Checks the Response and if it is marked with 200 OK, then
# it forwards the response to the Client and stores it in the cache.
# Otherwise, if 304 Unmodified, then the proxy forwards the response 
# from the cache to the Client.
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

    # Purpose & Behavior: Receives the HTTP GET Request from Client and
    # and sends the appropriate HTTP Request to the Web Server. Afterwards,
    # it gets the HTTP response from the Web Server and sends that back to the Client.
    # Also closes all sockets and connections.
    # Input: Client connection and client address.
    # Output: None
    def serve_content(self, client_conn, client_addr):
        print ('Serving content to client with address', client_addr)

        # Receive data from client
        bin_data = client_conn.recv(1024)

        # Print data from client
        print ('Server received', bin_data)

        # Decodes the GET request from client
        try:
            get_request = bin_data.decode('utf-8')
        except UnicodeDecodeError as e:
            print ('Part of message was unable to be decoded:', e)

        host, path = self.parse_request(get_request)
        bin_data, path, host = self.parse_complete_URL(path, host)
        url = host+path
        sock = None
        sock = self.open_HTTP_conn(host)
        response = self.get_response(sock, url, bin_data, host, path)

        try:
            # sends encoded message to server
            print ("Sending over response back to Client...")
            client_conn.sendall(response)
        except:
            print ("Failed send over whole message.")
            # Closes connection to client if there is a connection
            if (client_conn is not None):
                client_conn.close()
        
        # Closes socket to Web Server if it exists
        if (sock is not None):
            print("Closing TCP connection with Web Server...")
            sock.close()

        # Close connection to client
        print("Closing TCP connection with Client...\r\n")
        client_conn.close()

    # Purpose & Behavior: Parses URL when the GET Request includes
    # a complete url. The path is where the full URL for our purposes is.
    # Input: Path and host from HTTP GET Request
    # Output: Modified GET Request, path, and host.
    def parse_complete_URL(self, path, host):
        if ("http://" in path):
            split_url = path.split("/")
            host = split_url[2]
            path = ''

            for i in range(3, len(split_url)):
                path += '/' + split_url[i]

            get_request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n'.format(path, host)

            try:
                bin_data = get_request.encode('utf-8') # encodes GET Request
            except UnicodeEncodeError as e:
                print ('Part of message was unable to be encoded:', e)
        else:
            get_request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n'.format(path, host)
            try:
                bin_data = get_request.encode('utf-8') # encodes GET Request
            except UnicodeEncodeError as e:
                print ('Part of message was unable to be encoded:', e)
        return (bin_data, path, host)

    # Purpose & Behavior: - Checks if URL is in the cache and returns the appropriate
    # response. If the URL is in the cache, then we create a conditional request and 
    # decide whether to return the response in the cache or return an updated response 
    # and update the cache. - Otherwise, if the URL is not in the cache, then we are getting 
    # the response through the normal way by sending a request to the Web Server and receiving it.
    #  
    # Input: socket to Web Server, URL, encoded HTTP response, and host/path
    # Output: Correct HTTP Response that will be sent to the Client.
    def get_response(self, sock, url, bin_data, host, path):
        # checks if url is in cache already
        print ("Checking if URL is in cache...")

        # case for when URL is in cache
        if cache.get(url) is not None:
            print ("URL is in cache...")
            time = cache.get(url)[0]
            try:
                get_request = bin_data.decode('utf-8')
            except UnicodeDecodeError as e:
                print ('Part of message was unable to be decoded:', e)

            # creates conditional get request
            get_request_modded = 'GET {} HTTP/1.1\r\nHost: {}\r\nIf-Modified-Since: {}\r\nConnection: Close\r\n\r\n'.format(path, host, time)

            try:
                bin_request_modded = get_request_modded.encode('utf-8')
            except UnicodeEncodeError as e:
                print ('Part of message was unable to be encoded:', e)

            try:
                print("Sending request to Web Server: {}...".format(url))
                sock.sendall(bin_request_modded)
            except AttributeError as e:
                print ("No socket found: ", e)

            # gets current time that we are accessing the web server
            new_time = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
            response = self.recv_resp(sock)

            if ("304 Not Modified".encode('utf-8') in response):
                # returns response from cache since website has not been modified
                print ("Webpage has not been modified; returning response from cache...")
                return cache.get(url)[1]
            else:
                # returns an updated response that was received by sending the conditional get request
                print ("Webpage has been updated; returning updated response and updating cache")
                cache.set(url, [new_time, response])
                return response            
        else:
            # case for when URL is not in cache
            print ("URL is not in cache...")
            try:
                print("Sending request to Web Server: {}...".format(url))
                sock.sendall(bin_data) # sends unmodified get request to web server
                time = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
                response = self.recv_resp(sock) 
                print ("Storing response in cache...")
                cache.set(url, [time, response]) # updates cache with response
                return response
            except AttributeError as e:
                print ("No socket found: ", e)

    # Purpose & Behavior: Parses GET Request from Client into host and path.
    # Input: HTTP GET Request from Client.
    # Ouput: Tuple of host and path.
    def parse_request(self, get_request):
        host = ''
        path = ''

        try:
            url_split = get_request.split(" ")
            host_arr = get_request.split("Host: ")[1].split(" ")[0].split("\r")
            host = host_arr[0]
            path = url_split[1]
        except IndexError as e:
            print ("GET_request cannot be parsed:", e)

        return (host, path)

    # Purpose & Behavior: Opens TCP connection to given host.
    # Input: Host to connect to.
    # Ouput: Socket where TCP connection is started.
    def open_HTTP_conn(self, host):
        # Try to connect to host
        try:
            sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host,80)) # connect to host at port 80
            return sock
        except OSError as e:
            print ('Unable to connect to socket: ', e)
            if (sock is not None):
                sock.close()

    # Purpose & Behavior: Receives HTTP Response from Web Server.
    # Input: Socket that connects to the Web Server.
    # Ouput: Encoded binary HTTP Response.
    def recv_resp(self, sock):
        msg = ''
        msg_encoded = msg.encode('utf-8') # encodes GET Request as a binary string
        while True:
            received_resp = sock.recv(4096)
            # breaks out if we recv no data
            if not received_resp:
                break
            msg_encoded += received_resp
        return msg_encoded

def main():
    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50008

    # Parse command line parameters if any
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    # Create EchoServer object
    server = EchoServer(server_host, server_port)

if __name__ == '__main__':
    main()
