#Proxy Web Server
##List of files:
	- client.py
		- Purpose: Client handles Client HTTP Requests and Proxy HTTP Responses (more detail in file header)
	- web_proxy.py 
		- Purpose: Web Proxy handles the Proxy HTTP Response, Proxy HTTP Request, and Server HTTP Response (more detail in file header)
	- cache.py
		- Purpose: Stores HTTP Responses in a dictionary

##Usage:
	FOR RUNNING WITH CLIENT
	-----------------------
	1) run web_proxy.py
		a. cd to directory with file 
		b. type in './web_proxy.py optional_args'

			where
			-----
			optional_args (optional arguments):
				server_host (host that we want to connect to): default = localhost
				server_port (port that we want to connect to): default = 50008
	2) run client.py
		a. cd to directory with file
		b. type in './client.py positional_args optional_args'

			where 
			-----
			positional_args (required arguments):
				URL (http:// or www.)
			optional_args (optional arguments):
				server_host (host that we want to connect to)
				server_port (port that we want to connect to)
		
	FOR RUNNING WITH WEB BROWSER
	----------------------------
	1) run web_proxy.py
		-same steps as running with client, but type in "localhost 50007" for optional_args
	2) go to your favorite web browser's proxy settings and select the Web Proxy (HTTP) Protocol and set up the Web Proxy Server as localhost:50007
	3) test the web proxy out with all HTTP websites

