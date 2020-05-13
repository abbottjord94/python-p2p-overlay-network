import socket
import sys
import json
import threading

class ClientConnectionManager():

	_sockets = []
	_addresses = []

	def __init__(self, other_nodes):
		self._sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in other_nodes]
		for i in range(0,len(other_nodes)):
			self._sockets[i].connect(other_nodes[i])

		threading.Thread(target=self.parse_client_messages).start()

	def connect_to_node(self, other_node):
		try:
			self._addresses.append(other_node)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(other_node)
			self._sockets.append(sock)
		except:
			print("could not connect to node:", other_node, sys.exc_info()[0])

	def parse_client_messages(self):
		while 1:
			for sock in self._sockets:
				msg = sock.recv(1024)
				if not msg: break
				else:
					#parse messages here
					print(sock,msg.decode())
					msg_obj = json.loads(msg.decode())
					if(msg_obj.get("header") == "LISTEN_PORT"):
						print("Listen Port message received: ", msg_obj)

class ListenServerManager():

	_listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	_listenSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	_clientConnectionManager = ClientConnectionManager(())
	_addresses = []

	def __init__(self, tcp_ip, tcp_port,initial_connection):
		self.tcp_port = tcp_port
		self._listenSocket.bind((tcp_ip, tcp_port))
		if not initial_connection == None:
			self._clientConnectionManager.connect_to_node(initial_connection)

		threading.Thread(target=self.listen_for_messages()).start()

	def listen_for_messages(self):
		self._listenSocket.listen(1)
		while 1:
			c,a = self._listenSocket.accept()
			self.broadcast_listen_port(c)
			self.broadcast_connections(c)
			threading.Thread(target=self.handle_connection,args=(c,a)).start()

	def broadcast_connections(self,connection):
		try:
			msg_obj = {"header":"CLIENT_CONNECTIONS", "connections":self._addresses}
			print("Broadcasting the following connections to: ", connection, msg_obj)
			connection.send(json.dumps(msg_obj).encode())
		except:
			print("Failed to broadcast connections to: ", connection)

	def broadcast_listen_port(self,connection):
		try:
			msg_obj = {"header":"LISTEN_PORT", "listen_port":self.tcp_port}
			print("Broadcasting listen port to: ", connection, msg_obj)
			connection.send(json.dumps(msg_obj).encode())
		except:
			print("Failed to broadcast listen port to ", connection)

	def handle_connection(self,conn,addr):
		self._addresses.append(addr)
		print("handle_connection started for: ", addr)
		while 1:
			msg = conn.recv(1024)
			if not msg: break
			else:
				#Handle listened messages
				print(addr,msg.decode())
				#We'll start with connecting to other nodes
				try:
					msg_obj = json.loads(msg.decode())
					if(msg_obj.get("header")) == "CLIENT_CONNECTIONS":
						other_nodes = msg_obj.get("connections")
						print(other_nodes)
					if(msg_obj.get("header")) == "LISTEN_PORT":
						print("Listen Port Message Received")
						a = self._addresses.find(addr)
						a[1] = msg_obj.get("listen_port")
						print(a)
				except:
					pass
print(sys.argv)
for arg in sys.argv:
	if arg == '--connect':
		print(arg, sys.argv[sys.argv.index(arg)+1], sys.argv[sys.argv.index(arg)+2])
		_listenServerManager = ListenServerManager('192.168.0.14',5005,(sys.argv[sys.argv.index(arg)+1], int(sys.argv[sys.argv.index(arg)+2])))

print("No arguments found")
_listenServerManager = ListenServerManager('192.168.0.14',5005,None)
