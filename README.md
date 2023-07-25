## Local Testing

`pip install pipenv`  
or for Mac  
`brew install pipenv` 

to start working in a virtual environment,  
`pipenv shell`  

Formatting  
`black [FILE_PATH]`

tracker startup command:  
`
python tracker/tracker.py --port [Optional:Network_Capacity]
`
e.g.
`
python tracker/tracker.py 20
`

client startup command:  
`
python client/client.py --client_ip=[CLIENT_IP] --client_port=[CLIENT_PORT] --client_file_port=[CLIENT_FILE_PORT] --tracker_ip=[TRACKER_IP] --tracker_port=[TRACKER_PORT]
`
Optional Arguments  
--client_ip  
--client_port  