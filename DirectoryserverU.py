"""
Created on Fri Dec 01 15:07:37 2017
@author: UJJWAL
"""
import sys
import config
import random
from TcpServer import TcpServer

class DirectoryServer(TcpServer):
    message = {config.REQUESTFILEDETAIL}
    server = [config.REPLICATIONSERVER + (x * (config.REPSERVERCOPIES + 1)) for x in range(config.REPLICATIONSERVER)]
    folder = {}

    # overriding request processing function
    def process_req(own, conf, req, var):
        # requesting file details from directory
        if req == config.REQUESTFILEDETAIL:
            try:
                # adding the folder to directory listing if writing
                if var[2] == 'WRITE':
                    # check if folder exists in directory listing
                    if var[1] not in own.folders:
                        # if not writing then assigning folder to random server
                        random_server_port = random.choice(own.server)
                        own.folders[var[1]] = {'id' : own.hash_str(own.ip + str(random_server_port) + var[1]), 'ip' : own.ip, 'port' : str(random_server_port), 'files' : [var[0]]}
                
                # returning the directory id and location
                response = own.folder[var[1]]

                # checking if the file is in directory
                if var[0] in response['files']:
                    own.sendmsg(conf, config.RETURNFILEDETAIL.format(response['id'], response['ip'], response['port']))
                else:
                    own.error(conf, "File not found.")
            
            except KeyError:
                # returning the file not found if file_id key not in files dict
                own.error(conf, "File not found.")

def main():
    print "Directory Server started on " + str(config.DIRECTORYSERVER)
    server = DirectoryServer(config.DIRECTORYSERVER)
if __name__ == "__main__": main()
