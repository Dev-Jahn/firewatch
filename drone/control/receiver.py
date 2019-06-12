import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('192.168.43.143',6666))
#sock.bind(('192.168.43.143',8080))

while 1:
	data,addr = sock.recvfrom(200)
	print('data:',data.decode())
	print('client IP:',addr[0])
	print('client Port:',addr[1])

