import sys
import config
from threading import Lock
from TcpServer import TcpServer
from eve.auth import BasicAuth

class LockServerU(TcpServer):
    message = {config.REQUESTLOCK, config.REQUESTUNLOCK, config.REQUESTUSE}
    locksmutex = Lock()
    locking = {}

    # overriding the request processing function
    def processrequesting(own, conf, request, var):
        file_id = var[0]
        client = var[1]

        # lock request
        if request == config.REQUESTLOCK:
            try:
                # acquiring locks mutex
                own.locks_mutex.acquire()
                # returning failure if file is locked and lock owner is different client
                if file_id in own.locks and own.locks[file_id] != client:
                    own.send_msg(conf, config.FAILURE.format("File has been locked by another client"))
                # otherwise okay to lock file for client and returning success
                else:
                    own.locks[file_id] = client
                    own.send_msg(conf, config.SUCCESS.format("Locked"))
            finally:
                own.locks_mutex.release()

        # unlock request
        elif request == config.REQUESTUNLOCK:
            try:
                # acquiring locks mutex
                own.locks_mutex.acquire()
                # unlocking and return success if file is locked and owned by client
                if file_id in own.locks and own.locks[file_id] == client:
                    del own.locks[file_id]
                    own.send_msg(conf, config.SUCCESS.format("Unlocked"))
                # otherwise returning failure if file is not in array
                elif file_id not in self.locks:
                    own.send_msg(conf, config.FAILURE.format("File not locked"))
                # otherwise returning file locked by another client
                else:
                    own.send_msg(conf, config.FAILURE.format("File locked by another client"))

            finally:
                own.locks_mutex.release()

        # usage request
        elif request == config.REQUESTUSE:
            try:
                # acquiring locks mutex
                own.locks_mutex.acquire()
                # returning disallowed only if file is locked and owned by different client
                if file_id in own.locks and own.locks[file_id] != client:
                    own.send_msg(conf, config.FAILURE.format("Disallowed"))
                # otherwise return allowed to access file
                else:
                    own.send_msg(conf, config.SUCCESS.format("Allowed"))
            finally:
                own.locks_mutex.release()
     

def main():
    print "Lock Server was started on " + str(config.LOCKSERVER)
    server = LockServer(config.LOCKSERVER)
if __name__ == "__main__": main()
