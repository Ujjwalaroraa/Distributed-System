import sys
import config
from threading import Lock
from TcpServer import TcpServer
from eve.auth import BasicAuth

class LockServer(TcpServer):
    messages = {config.REQUEST_LOCK, config.REQUEST_UNLOCK, config.REQUEST_USE}
    locks_mutex = Lock()
    locks = {}

    # overriding the request processing function
    def process_req(self, conn, request, vars):
        file_id = vars[0]
        client = vars[1]

        # lock request
        if request == config.REQUEST_LOCK:
            try:
                # acquiring locks mutex
                self.locks_mutex.acquire()
                # returning failure if file is locked and lock owner is different client
                if file_id in self.locks and self.locks[file_id] != client:
                    self.send_msg(conn, config.FAILURE.format("File locked by another client"))
                # otherwise okay to lock file for client and returning success
                else:
                    self.locks[file_id] = client
                    self.send_msg(conn, config.SUCCESS.format("Locked"))
            finally:
                self.locks_mutex.release()

        # unlock request
        elif request == config.REQUEST_UNLOCK:
            try:
                # acquiring locks mutex
                self.locks_mutex.acquire()
                # unlocking and return success if file is locked and owned by client
                if file_id in self.locks and self.locks[file_id] == client:
                    del self.locks[file_id]
                    self.send_msg(conn, config.SUCCESS.format("Unlocked"))
                # otherwise returning failure if file is not in array
                elif file_id not in self.locks:
                    self.send_msg(conn, config.FAILURE.format("File not locked"))
                # otherwise returning file locked by another client
                else:
                    self.send_msg(conn, config.FAILURE.format("File locked by another client"))

            finally:
                self.locks_mutex.release()

        # usage request
        elif request == config.REQUEST_USE:
            try:
                # acquiring locks mutex
                self.locks_mutex.acquire()
                # returning disallowed only if file is locked and owned by different client
                if file_id in self.locks and self.locks[file_id] != client:
                    self.send_msg(conn, config.FAILURE.format("Disallowed"))
                # otherwise return allowed to access file
                else:
                    self.send_msg(conn, config.SUCCESS.format("Allowed"))
            finally:
                self.locks_mutex.release()
     

def main():
    print "Lock Server was started on " + str(config.LOCK_SERVER)
    server = LockServer(config.LOCK_SERVER)
if __name__ == "__main__": main()
