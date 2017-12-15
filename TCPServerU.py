
"""
Created on Tues Nov  21 10:59:04 2017
@author: UJJWAL
"""
import sys
import socket
import re
import os
import math
import config
import hashlib
from time import sleep
from Queue import Queue
import thread
from threading import Thread, Lock

# defining worker class that implements thread
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(own, request, server):
        Thread.__init__(own)
        # store clients queue pointer
        own.request = request
        # pointer to master server object
        own.server = server
        # set as daemon so it dies when main thread exits
        own.daemon = True
        # start the thread on init
        own.start()

    # function run indefinitely once thread will started
    def run(own):
        while True:
            # pop an element from the queue
            (conf, addr) = own.request.get()
            # check if valid connection or not else kill loop
            if conf:
                for msg in own.server.extract_msg(conf, addr):
                    (request, var) = own.server.get_req(conf, msg)
                    own.server.process_req(conf, request, var)
            else:
                break;
            # set task as done in queue
            own.request.task_done()

# define main tcp server class
class TcpServer(object):

    # queue threshold to increase or decrease num workers
    QUEUE_THRESHOLD = 50.0

    # max and min number of threads
    MAX_THREADS = 100.0
    MIN_THREADS = 10.0

    def __init__(own, port):
        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # queue object to store requests
        own.requests = Queue()

        # thread counter
        own.num_threads = own.MIN_THREADS

        # bind to port and listen for connections
        s.bind(("0.0.0.0", port)) 
        (own.ip, own.port) = s.getsockname()
        s.listen(5)

        # create initial workers
        for _ in range(int(own.MIN_THREADS)): 
            Worker(own.requests, own)

        # continuous loop to keep accepting requests
        while 1:
            # accept a connection request
            conf, addr = s.accept()
            own.accept(conf, addr)

    # accept connection request from socket
    def accept(own, conf, addr):
        # cache queue size and get threshold
        qsize = own.request.qsize()
        queue_margin = int(math.ceil(self.num_threads * (self.QUEUE_THRESHOLD / 100.0)))

        # check if queue size is between num_threads and (num_threads - margin)
        if qsize >= (own.num_threads - queue_margin) and own.num_threads != own.MAX_THREADS:
            # add queue_margin amount of new workers
            for _ in range(queue_margin): 
                if own.num_threads == own.MAX_THREADS:
                    break
                Worker(own.requests)
                own.num_threads += 1
        # else check if queue size is between 0 and margin
        elif qsize <= queue_margin and own.num_threads != own.MIN_THREADS:
            # remove queue_margin amount of workers
            for _ in range(queue_margin): 
                if own.num_threads == own.MIN_THREADS:
                    break
                clients.put((None, None))
                own.num_threads -= 1

        # receive data and put request in queue
        own.requests.put((conf, addr))
    
    # create hash of string
    def hash_str(own, string):
        sha = hashlib.sha1(string)
        return sha.hexdigest()

    # function to get message text from a connection
    def extract_msg(own, conf, addr):
        while conf:
            msg = ""
            # Loop through message to receive data
            while "\n\n" not in msg and conf:
                data = conf.recv(4096)
                msg += data
                if len(data) < 4096:
                    break
            # yields current msg from conn if found
            if msg:
                yield msg
                # break if not client connecting file server
                if own.port != config.FILESERVER:
                    break

    # send message back to connection
    def send_msg(own, conf, data):
        # supress replication server messages
        if not hasattr(own, 'is_slave') or own.is_slave == False:
            print "Sent: \"" + data.rstrip('\n') + "\""
        conn.sendall(data)

    # read the request message from the input
    def get_req(own, conf, msg):
        # supress replication server messages
        if not hasattr(own, 'is_slave') or own.is_slave == False:
            print "Received: \"" + msg.rstrip('\n') + "\""
        matched_request = ""
        matched_vars = []
        for r in own.messages:
            m = re.match(r.replace("{}", "(.*)"), msg)
            if m:
                matched_request = r
                matched_vars = m.groups()
        if not matched_request:
            own.error(conf, "Unknown Message")
        else:
            return (matched_request, matched_vars)

    # send message to server
    def propagate_msg(own, request, var, server, response_required=True):
        # connect to socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", server)) 

        # send data
        own.send_msg(s, request.format(*var))

        # accept response from socket
        if response_required:
            for msg in own.extract_msg(s, s.getpeername()):
                s.close()
                return own.get_req(s, msg)

    # return an error message to the user
    def error(own, conf, msg):
        own.send_msg(conf, config.ERROR_MSG.format(msg))
