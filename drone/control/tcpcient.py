import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('192.168.43.143',6666))
s.listen(0)
client, addr = s.accept()
data = client.recv(65535)
print('data:',data.decode())
