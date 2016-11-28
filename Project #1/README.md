List of files:
	- client.py
		- Purpose: Client handles Client HTTP Requests and Proxy HTTP Responses (more detail in file header)
	- web_proxy.py 
		- Purpose: Web Proxy handles the Proxy HTTP Response, Proxy HTTP Request, and Server HTTP Response (more detail in file header)
	- cache.py
		- Purpose: Stores HTTP Responses in a dictionary

Usage:
	- client.py
		- 	1. cd to directory with file
			2. add '#!python3_path' to the beginning of the file;
				type in 'which python' in terminal to find this.
				(only necessary if the path is different from the one in the file)
			3. run 'chmod a+x client.py'
			4. type in './client.py positional_args optional_args'

				where 
				-----
				positional_args (required arguments):
					URL (http:// or www.)
				optional_args (optional arguments):
					server_host (host that we want to connect to)
					server_port (port that we want to connect to)
	- web_proxy.py
	
		FOR RUNNING WITH CLIENT
		-----------------------
		- 	1. cd to directory with file 
			2. add '#!python3_path' to the beginning of the file;
				type in 'which python' in terminal to find this.
				(only necessary if the path is different from the one in the file)
			3. run 'chmod a+x web_proxy.py'
			4. type in './web_proxy.py optional_args'

				where
				-----
				optional_args (optional arguments):
					server_host (host that we want to connect to): default = localhost
					server_port (port that we want to connect to): default = 50008
		
		FOR RUNNING WITH WEB BROWSER
		----------------------------
		-	same steps as above, type in "localhost 50007" for optional_args

