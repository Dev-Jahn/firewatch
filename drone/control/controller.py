
# coding: utf-8

# In[34]:


import socket


# In[35]:


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# In[36]:


#sock.sendto("surprise motherfucker".encode(), ('192.168.43.143',8080))
#sock.sendto("surprise motherfucker".encode(), ('192.168.0.148',8080))


# In[37]:


sock.sendto("surprise motherfucker".encode(), ('192.168.43.143',6666))
#sock.sendto("surprise motherfucker".encode(), ('192.168.0.148',8080))

