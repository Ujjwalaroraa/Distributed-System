"""
Created on Saturday Dec 02 11:04:19 2017
@author: UJJWAL
"""
import os
import sys
import config
from threading import Thread
from TcpServer import TcpServer

class ReplicationSlave(Thread):
    def __init__(self, port):
        print "Replication Slave " + str(port) + " Created!"
        Thread.__init__(self)
        self.port = port
        self.daemon = True
        self.start()
    def run(self):
        ReplicationServer(self.port)

class ReplicationServer(TcpServer):
    messages = {config.READ_FILE, config.WRITE_FILE, config.DELETE_FILE, config.SUCCESS, config.FAILURE}
    slaves = []
    files = {}

    # overriding init function to import slaves list
    def __init__(self, port, slaves=[]):
        self.slaves = slaves
        self.is_slave = True if slaves == [] else False
        if not os.path.exists(str(port)):
            os.makedirs(str(port))
        TcpServer.__init__(self, port)

    # overriding request processing function
    def process_req(self, conn, request, vars):
        # requesting file data from replication server
        if request == config.READ_FILE or request == config.WRITE_FILE or request == config.DELETE_FILE:
            file_id = vars[0]
            client = vars[1]

            # updating file data if file update is asked for
            if request == config.WRITE_FILE:
                data = vars[2]

                # checking with lock server if it permits 
                if not self.is_slave:
                    (resp, resp_vars) = self.propagate_msg(config.REQUEST_USE, (file_id, client), config.LOCK_SERVER)

                # writing file to all servers if it is allowed
                if self.is_slave or resp == config.SUCCESS:
                    self.files[file_id] = True

                    # writing file to disk
                    f = open(os.path.join(str(self.port), file_id), 'w')
                    f.write(data)
                    f.close()

                    # propagating request to all slaves if master
                    for slave in self.slaves:
                        print "PROPAGATING WRITE REQUEST TO " + str(slave)
                        self.propagate_msg(request, vars, slave, False)
                    # responding to the  client with success message
                    if not self.is_slave:
                        self.send_msg(conn, config.SUCCESS.format("File written successfully."))
                else:
                    self.send_msg(conn, resp.format(*resp_vars))

            else:
                # to check if the file exists for read and delete
                if file_id in self.files:

                    # to check if the lock server permits
                    if not self.is_slave:
                        (resp, resp_vars) = self.propagate_msg(config.REQUEST_USE, (file_id, client), config.LOCK_SERVER)

                    if self.is_slave or resp == config.SUCCESS:
                        # sending back file data if requested 
                        if request == config.READ_FILE:
                            f = open(os.path.join(str(self.port), file_id), 'r')
                            self.send_msg(conn, config.RETURN_FILE_DATA.format(f.read()))
                            f.close()

                        # deleting the file from index if requested 
                        elif request == config.DELETE_FILE:
                            del self.files[file_id]

                            # propagating the request to all slaves
                            for slave in self.slaves:
                                print "PROPAGATING DELETE REQUEST TO  " + str(slave)
                                self.propagate_msg(request, vars, slave, False)
                            # responding with success message
                            if not self.is_slave:
                                self.send_msg(conn, config.SUCCESS.format("File deleted successfully."))
                    else:
                        self.send_msg(conn, resp.format(*resp_vars))

                # else returning "file not found"
                else:
                    self.error(conn, "File not found.")

def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Port number required")
    print "Replication Master started on " + sys.argv[1]
    
    slaves = []

    # initialising other multiple slave servers
    for i in range(config.REP_SERVER_COPIES):
        port = int(sys.argv[1]) + (i + 1)
        slaves.append(port)
        ReplicationSlave(port)

    # initialising other master replication server
    master = ReplicationServer(int(sys.argv[1]), slaves)


if __name__ == "__main__": main()
