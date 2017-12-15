# starting all servers
python2 DirectoryserverU.py 5001 &
python2 LockServerU.py 5002 &
python2 ReplicationServerU.py 5003 &
python2 TCPServerU.py 5000  &
python2 cachingServerU.py 5004  &
