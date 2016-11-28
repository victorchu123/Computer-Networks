#!/usr/bin/python3
#
# COMP 360, Section 1, Fall 2016
# Victor Chu
#
# Simple traceroute implementation using raw sockets to send 
# ICMP Echo Request Packets (created using IP and ICMP Headers)
# and receive ICMP Echo Reply Packets that contain the information 
# needed to print out the traceroute information. 
#
# *** Only that supports IPv4 addresses
#
# Usage:
#    - icmp_traceroute.py
#        -   1. cd to directory with file
#            2. add '#!python3_path' to the beginning of the file;
#                type in 'which python' in terminal to find this.
#                (only necessary if the path is different from the one in the file)
#            3. run 'chmod a+x icmp_traceroute.py'
#            4. type in './icmp_traceroute.py optional_args'
#
#                where 
#                -----
#                optional_args (optional arguments):
#                    - source ip (dotted-quad string)
#                    - destination ip (dotted-quad string)
#                    - ip header identficiation (int)
#                    - ip header time-to-live (int)
#                    - icmp header identification (int)
#                    - icmp sequence number (int)
#                - *** if optional args are used, all must be provided ***
#
        
import socket
import struct
import sys
import array
import time

class IcmpTraceroute():

    def __init__(self, src_ip, dst_ip, ip_id, ip_ttl, icmp_id, icmp_seqno):

        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ip_id = ip_id
        self.max_ttl = ip_ttl
        self.ip_ttl = 1
        self.icmp_id = icmp_id
        self.icmp_seqno = icmp_seqno
        print('ICMP traceroute created.')

    def run_traceroute(self):

        # Iterate as many times as TTL values
        for ttl in range (1, self.max_ttl + 1):

            # Create ICMP pkt, process response and compute statistics
            [RTT, ip_src_addr] = self.traceroute()

            # Print statistics for this run
            print ("[TTL: {}]".format(ttl), "[Destination IP: {}]".format(ip_src_addr), "[RTT: {}]".format(RTT))
            # Update variables for next run
            self.ip_id = self.ip_id + 1
            self.icmp_id = self.ip_id + 1
            self.ip_ttl = ttl

    def traceroute(self):

        # Create packet
        ip_header = self.create_ip_header()
        icmp_header = self.create_icmp_header()
        bin_echo_req = ip_header + icmp_header

        # Create send and receive sockets
        send_sock = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        recv_sock = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # Set IP_HDRINCL flag so kernel does not rewrite header fields
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # Set receive socket timeout to 2 seconds
        recv_sock.settimeout(2.0)

        # Send packet to destination
        try:
            print("Sending ICMP Echo Request...")
            # record time request was sent
            time_sent = time.time()
            send_sock.sendto(bin_echo_req, (self.dst_ip, 0))
            send_sock.close()
        except OSError as e:
            print('Unable to send packet, exiting.')
            send_sock.close()
            exit(0)

        # Receive echo reply (hopefully)
        try:
            [bin_echo_reply, addr] = recv_sock.recvfrom(1024)
            # record time response was received
            time_recvd = time.time()
            recv_sock.close()
        except OSError as e:
            print('No response, exiting.')
            recv_sock.close()
            exit(0)

        # Extract info from ip_header
        [ip_header_length, ip_identification, ip_protocol,
                ip_src_addr]  = self.decode_ip_header(bin_echo_reply)

        # Extract info from icmp_header
        [icmp_type, icmp_code] = self.decode_icmp_header(
                bin_echo_reply, ip_header_length)

        # calculates rtt in units of ms
        RTT = "{} ms".format(round(((time_recvd - time_sent) * 1000), 3))

        return [RTT, ip_src_addr]

    def convert_ip_addr_to_binary(self, ip_addr):
        # tries to convert given IPv4 address from a dotted-quad string format to 32-bit packed binary format
        # if fails, prints an error message and exits.
        try:
            binary_ip = socket.inet_aton(ip_addr)
        except OSError as e:
            print ("IPv4 address string passed to this function is invalid: ", e)
            exit(0)
        return binary_ip

    def create_ip_header(self):

        # Returned IP header is packed binary data in network order
        
        # IP header info from https://tools.ietf.org/html/rfc791
        ip_version_and_IHL = 69                                     # 8 bits
        ip_TOS = 0                                                  # 8 bits
        ip_tot_length = 28                                          # 16 bits
        ip_id = self.ip_id                                          # 16 bits
        ip_flags_and_foffset = 0                                    # 16 bits
        ip_ttl = self.ip_ttl                                        # 8 bits
        ip_protocol = 1                                             # 8 bits
        ip_checksum = 0                                             # 16 bits
        ip_src_addr = self.convert_ip_addr_to_binary(self.src_ip)   # 32 bits
        ip_dst_addr = self.convert_ip_addr_to_binary(self.dst_ip)   # 32 bits

        # IP header is packed binary data in network order
        ip_header = struct.pack('!BBHHHBBH4s4s', # ! means network order
        ip_version_and_IHL,     # B = unsigned char = 8 bits
        ip_TOS,         # B = unsigned char = 8 bits
        ip_tot_length,      # H = unsigned short = 16 bits
        ip_id,          # H = unsigned short = 16 bits
        ip_flags_and_foffset,       # H = unsigned short = 16 bits
        ip_ttl,         # B = unsigned char = 8 bits 
        ip_protocol,    # B = unsigned char = 8 bits
        ip_checksum,    # H = unsigned short = 16 bits 
        ip_src_addr,    # s = char[]
        ip_dst_addr)    # s = char[]

        return ip_header

    def create_icmp_header(self):

        ECHO_REQUEST_TYPE = 8
        ECHO_CODE = 0

        # ICMP header info from https://tools.ietf.org/html/rfc792
        icmp_type = ECHO_REQUEST_TYPE      # 8 bits
        icmp_code = ECHO_CODE              # 8 bits
        icmp_checksum = 0                  # 16 bits
        icmp_identification = self.icmp_id # 16 bits
        icmp_seq_number = self.icmp_seqno  # 16 bits

        # ICMP header is packed binary data in network order
        icmp_header = struct.pack('!BBHHH', # ! means network order
        icmp_type,           # B = unsigned char = 8 bits
        icmp_code,           # B = unsigned char = 8 bits
        icmp_checksum,       # H = unsigned short = 16 bits
        icmp_identification, # H = unsigned short = 16 bits
        icmp_seq_number)     # H = unsigned short = 16 bits

        return icmp_header

    def decode_ip_header(self, bin_echo_reply):

        # Decode ip_header
        try:
            # decodes whole response, which has the format of (ip_header + icmp_header) * 2
            response_decoded = struct.unpack('!BBHHHBBH4s4sBBHHHBBHHHBBH4s4sBBHHH', bin_echo_reply)
            # Extract fields of interest
            ip_version_and_IHL = response_decoded[0] # combined ip header's version and header length
            ip_header_length = ip_version_and_IHL - 64 # we do this since we know the ip_version is always 4 (0100),
                                                       # so we can subtract that from the concatenation
            ip_identification = response_decoded[3] # ip header's id
            ip_protocol = response_decoded[6] # ip header's protocol
            # Converts the provided 32-bit packed IPv4 address into a standard dotted-quad string format
            # if fails, prints an error and exits.
            ip_src_addr = socket.inet_ntoa(response_decoded[8])
        except OSError as e:
            print ("Cannot decode message: ", e)
            exit(0)
        except struct.error as e:
            print ("Couldn't unpack message: ", e)
            exit(0)

        return [ip_header_length, ip_identification,
                ip_protocol, ip_src_addr]

    def decode_icmp_header(self, bin_echo_reply, ip_header_length):

        # Note: Echo Reply contains entire IP packet that triggered
        # it. Enables Echo Reply to be matched with originating
        # Echo Request. You are not required to decode this
        # payload, simply the ICMP header of the Echo Reply

        # Decode icmp_header
        try:
            total_len = bin_echo_reply[3] # total length of the header with data (ip + icmp + data)
            ip_len = ip_header_length * 4 # length of ip header
            icmp_len = (total_len//2) - ip_len # length of icmp header
            # tries to decode/unpack the portion of the response which has the icmp header
            response_decoded = struct.unpack('!BBHHH', bin_echo_reply[ip_len : ip_len + icmp_len])
            # Extract fields of interest
            icmp_type = response_decoded[0] # Should equal 11, for Time-to-live exceeded
            icmp_code = response_decoded[1] # Should equal 0
        except struct.error as e:
            print ("Cannot decode message: ", e)
            exit(0)
            
        return [icmp_type, icmp_code]

def main():

    src_ip = '129.133.194.105' # Your IP addr (e.g., IP address of VM)
    dst_ip = '172.16.100.1' # IP addr behind Wesleyan firewall
    ip_id = 111             # IP header in wireshark should have
    ip_ttl = 2              # 1 or 2 if you're on Wesleyan network
    icmp_id = 222           # ICMP header in wireshark should have
    icmp_seqno = 1          # Starts at 1, by convention

    if len(sys.argv) > 1:
        src_ip = sys.argv[1]
        dst_ip = sys.argv[2]
        ip_id = int(sys.argv[3])
        ip_ttl = int(sys.argv[4])
        icmp_id = int(sys.argv[5])
        icmp_seqno = int(sys.argv[6])

    traceroute = IcmpTraceroute(
            src_ip, dst_ip, ip_id, ip_ttl, icmp_id, icmp_seqno)
    traceroute.run_traceroute()

if __name__ == '__main__':
    main()
