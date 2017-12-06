# starting all servers
python2 Dir_server.py 5001 &
python2 Lock_server.py 5002 &
python2 Replication_server.py 5003 &
python2 Tcp_server.py 5000  &
python2 cache_server.py 5004  &
