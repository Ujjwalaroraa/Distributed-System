"""
Created on Wed Dec 06 02:00:04 2017
@author: UJJWAL
"""
import socket
import sys
import config
import re
from time import sleep
from random import randrange

messages = [config.RETURNFILEDATA, config.RETURNFILEDETAIL, config.SUCCESS, config.FAILURE]

def send_req(ip, port, data):
    # connecting the server
    s = socket.socket(socket.AF_INET, socket.SOCKSTREAM)
    s.connect((ip, port)) 
    s.settimeout(2)
    s.sendall(data)
    print "Sent: \"" + data.rstrip('\n') + "\""
    return get_req(s.recv(2048))

def get_req(msg):
    global messages
    print "Received: \"" + msg.rstrip('\n') + "\""
    matched_request = ""
    matched_vars = []
    for r in messages:
        m = re.match(r.replace("{}", "(.*)"), msg)
        if m:
            matched_request = r
            matched_vars = m.groups()
    return (matched_request, matched_vars)

# printing the connection instructions
print "Client Proxy Interface"
print "======================"
name = raw_input("Enter client name: ")

# getting the file details from DS
(req, vars) = send_req("localhost", config.DIR_SERVER, config.REQUESTFILEDETAIL.format("test.txt", "Desktop", "WRITE"))
file_id = vars[0]
file_ip = vars[1]
file_port = int(vars[2])
raw_input("Press Enter to continue...\n")

# writing the file to server
file = open('test.txt', 'r')
send_req(file_ip, file_port, config.WRITEFILE.format(file_id, name, file.read()))
raw_input("Press Enter to continue...\n")

# getting lock on file
send_req("localhost", config.LOCKSERVER, config.REQUESTLOCK.format(file_id, name))
raw_input("Press Enter to continue...\n")

# reading the file from server
send_req(file_ip, file_port, config.READFILE.format(file_id, name))
raw_input("Press Enter to continue...\n")

# unlocking the file
send_req("localhost", config.LOCKSERVER, config.REQUESTUNLOCK.format(file_id, name))
raw_input("Press Enter to continue...\n")
