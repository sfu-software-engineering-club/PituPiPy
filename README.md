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
python tracker/tracker.py --port=[TRACKER_PORT]
`

client startup command:  
`
python client/client.py --client_port=[CLIENT_PORT] --client_file_port=[CLIENT_FILE_PORT] --tracker_ip=[TRACKER_IP] --tracker_port=[TRACKER_PORT]
`