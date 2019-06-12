
# coding: utf-8

# In[1]:


import socket


# In[2]:


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# In[ ]:


sock.bind(('192.168.43.143',8080))
data,addr = sock.recvfrom(200)
print('data:',data.decode())
print('client IP:',addr[0])
print('client Port:',addr[1])

