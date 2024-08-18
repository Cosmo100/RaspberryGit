
import socket
import time


ip   = "hauptrechner"
port = 54345
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
N=0

while True:
    N +=1
    Test = str(N)
    #sock.sendto(Test.encode('utf-8'),(ip,port))
    
    sock.sendto(Test.encode('utf-8'), (ip, port)) 
    time.sleep(5)
