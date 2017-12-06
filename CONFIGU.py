# SERVERS
FILE_SERVER = 5000
DIR_SERVER = 5001
LOCK_SERVER = 5002
REP_SERVER = 5003
CAC_SERVER = 5004

# VARIABLES
LOCK_ATTEMPTS = 1
REP_SERVERS = 2
REP_SERVER_COPIES = 5

# Client and directory server connection
REQUEST_FILE_DETAILS = 'REQUEST_FILE_DETAILS: {}\nDIRECTORY: {}\nACTION: {}\n\n'
RETURN_FILE_DETAILS = 'RETURN_FILE_DETAILS: {}\nIP: {}\nPORT: {}\n\n'

# client/replication server and lock server communication
REQUEST_LOCK = 'REQUEST_LOCK: {}\nCLIENT: {}\n\n'
REQUEST_USE = 'REQUEST_USE: {}\nCLIENT: {}\n\n'
REQUEST_UNLOCK = 'REQUEST_UNLOCK: {}\nCLIENT: {}\n\n'

# Client and Replication Server Communication
WRITE_FILE = 'WRITE_FILE: {}\nCLIENT: {}\nDATA: {}\n\n'
READ_FILE = 'READ_FILE: {}\nCLIENT: {}\n\n'
DELETE_FILE = 'DELETE_FILE: {}\nCLIENT: {}\n\n'
RETURN_FILE_DATA = 'RETURN_FILE_DATA: {}\n\n'

# Status 
SUCCESS = 'SUCCESS: {}\n\n'
FAILURE = 'FAILURE: {}\n\n'
ERROR_MSG = 'ERROR: {}\n\n'
