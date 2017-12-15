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
    def __init__(own, port):
        print "Replication Slave " + str(port) + " Created!"
        Thread.__init__(own)
        own.port = port
        own.daemon = True
        own.start()
    def run(own):
        ReplicationServer(own.port)

class ReplicationServer(TcpServer):
    message = {config.READFILE, config.WRITEFILE, config.DELETEFILE, config.SUCCESS, config.FAILURE}
    slave = []
    file = {}

    # overriding init function to import slaves list
    def __init__(own, port, slave=[]):
        own.slave = slave
        own.is_slave = True if slave == [] else False
        if not os.path.exists(str(port)):
            os.makedirs(str(port))
        TcpServer.__init__(own, port)

    # overriding request processing function
    def process_req(own, conf, request, var):
        # requesting file data from replication server
        if request == config.READFILE or request == config.WRITEFILE or request == config.DELETEFILE:
            file_id = var[0]
            client = var[1]

            # updating file data if file update is asked for
            if request == config.WRITEFILE:
                data = var[2]

                # checking with lock server if it permits 
                if not own.is_slave:
                    (resp, resp_vars) = own.propagate_msg(config.REQUESTUSE, (file_id, client), config.LOCKSERVER)

                # writing file to all servers if it is allowed
                if own.is_slave or resp == config.SUCCESS:
                    own.files[file_id] = True

                    # writing file to disk
                    f = open(os.path.join(str(own.port), file_id), 'w')
                    f.write(data)
                    f.close()

                    # propagating request to all slaves if master
                    for slave in own.slaves:
                        print "PROPAGATING WRITE REQUEST TO " + str(slave)
                        own.propagate_msg(request, var, slave, False)
                    # responding to the  client with success message
                    if not own.is_slave:
                        own.send_msg(conf, config.SUCCESS.format("File written successfully."))
                else:
                    own.send_msg(conf, resp.format(*resp_var))

            else:
                # to check if the file exists for read and delete
                if file_id in own.files:

                    # to check if the lock server permits
                    if not own.is_slave:
                        (resp, resp_var) = own.propagate_msg(config.REQUESTUSE, (file_id, client), config.LOCKSERVER)

                    if own.is_slave or resp == config.SUCCESS:
                        # sending back file data if requested 
                        if request == config.READFILE:
                            f = open(os.path.join(str(own.port), file_id), 'r')
                            own.send_msg(conf, config.RETURNFILEDATA.format(f.read()))
                            f.close()

                        # deleting the file from index if requested 
                        elif request == config.DELETEFILE:
                            del own.files[file_id]

                            # propagating the request to all slaves
                            for slave in own.slaves:
                                print "PROPAGATING DELETE REQUEST TO  " + str(slave)
                                own.propagate_msg(request, var, slave, False)
                            # responding with success message
                            if not own.is_slave:
                                own.send_msg(conf, config.SUCCESS.format("File deleted successfully."))
                    else:
                        own.send_msg(conf, resp.format(*resp_var))

                # else returning "file not found"
                else:
                    own.error(conf, "File not found.")

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
