List of files:
	- icmp_traceroute.py
		- Purpose: ICMP Traceroute runs a simple traceroute by using raw sockets, ICMP Echo Request/Reply Packets (more detail in file header)

Usage:
	- icmp_traceroute.py
		- 	1. cd to directory with file
			2. add '#!python3_path' to the beginning of the file;
				type in 'which python3' in terminal to find this.
				(only necessary if the path is different from the one in the file)
			3. run 'chmod a+x icmp_traceroute.py'
			4. type in './icmp_traceroute.py optional_args'

				where 
				-----
				optional_args (optional arguments):
					- source ip (dotted-quad string)
	       			- destination ip (dotted-quad string)
    	   			- ip header identficiation (int)
       				- ip header time-to-live (int)
       				- icmp header identification (int)
       				- icmp sequence number (int)
   				- *** if optional args are used, all must be provided ***

Testing:
	
	Case 1
	------
		Inputs: 
			- ran 'sudo ./icmp_traceroute.py' in terminal

			default optional args:
				- src_ip: '129.133.199.34' (ip from host VM)
				- dst_ip: '172.16.100.1' (ip that I want to go to)
				- ip_id: 111 (id that ip header in wireshark should have)
				- ip_ttl: 1 (time to live, which also determines the number of hops that I want to have in traceroute)
				- icmp_id: 222 (id that icmp header in wireshark should have)
				- icmp_seqno: 1 (should start at 1 by convention)

		Outputs: 
			- 	ICMP traceroute created. 
			 	Sending ICMP Echo Request...
				[TTL: 1] [Destination IP: 129.133.192.1] [RTT: 17.043 ms]

		- This case passes because terminal displays the correct TTL (starts at 1 and only computes one hop as the default settings specified), the correct destination IP address (comes from an intermediate ip between my ip and 172.16.100.1, which I confirmed from running the normal traceroute), and a RTT that is similar to the one from running the normal traceroute.
		Moreover, I verified that the ip_id and icmp_id and other fields show up correctly in Wireshark (this case is in the screenshots).

	Case 2
	------
		Inputs: 
			- ran 'sudo ./icmp_traceroute.py 129.133.199.34 172.16.100.1 333 2 444 1' in terminal

			provided optional args:
				- src_ip: '129.133.199.34' (ip from host VM)
				- dst_ip: '172.16.100.1' (ip that I want to go to)
				- ip_id: 333 (id that ip header in wireshark should have)
				- ip_ttl: 2 (time to live, which also determines the number of hops that I want to have in traceroute)
				- icmp_id: 444 (id that icmp header in wireshark should have)
				- icmp_seqno: 1 (should start at 1 by convention)

		Outputs:
			-   ICMP traceroute created.
				Sending ICMP Echo Request...
				[TTL: 1] [Destination IP: 129.133.192.1] [RTT: 13.228 ms]
				Sending ICMP Echo Request...
				[TTL: 2] [Destination IP: 129.133.192.1] [RTT: 13.583 ms]

		- This case passes because terminal displays the correct TTL (starts at 1) and increments by 1 until it reaches the max TTL (2, which means 2 hops in this case), the correct destination IP address (comes from an intermediate ip between my ip and 172.16.100.1, which I confirmed from running the normal traceroute), and a RTT that is similar to the one from running the normal traceroute.
		Moreover, I verified that the ip_id and icmp_id and other fields show up correctly in Wireshark (this case is in the screenshots).
 

