
# coding: utf-8

# In[3]:


import socket


# In[4]:


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# In[6]:


sock.bind(('192.168.42.162',8080))
#sock.bind(('192.168.43.143',8080))
data,addr = sock.recvfrom(200)
print('data:',data.decode())
print('client IP:',addr[0])
print('client Port:',addr[1])

