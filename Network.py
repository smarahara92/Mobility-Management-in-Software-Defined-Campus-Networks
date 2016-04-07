class Network:
	"""
	The logical representation of Network
	"""
	
	def __init__(self):
		self.dpidlist = []	# {dpid1, dpid2, ...} for finding index of each node in topology and pathgraph
		self.switchlist = {}	# {dpid1: switchobj1, dpid2: switchobj2, ...} It stores obj of each switch
		self.topology = {}	# {dpid1: [port1, port2, ...], dpid2: [port1, port2, ...], ...}
		self.pathgraph = {}	# {dpid1: [port1, port2, ...], dpid2: [port1, port2, ...], ...}
	
	
	def _handle_ConnectionUp(self, event):
		self.dpidlist.append(event.dpid)
		self.switchlist[event.dpid] = None # create Switch obj here
		totalnoswitches = len(self.dpidlist)
		for key in self.topology.keys():
			adjlist = self.topology[key]
			adjlistlen = len(adjlist)
			while(adjlistlen < totalnoswitches):
				adjlist.append(None)
				adjlistlen += 1
	
	def _handle_ConnectionDown(self, event):
		index = -1
		try:
			index = self.dpidlist.index(event.dpid)
			self.dpidlist.remove(event.dpid)
			self.switchlist.pop(event.dpid)
		except ValueError:
			return
		self.topology.pop(event.dpid)
		for key in self.topology.keys():
			self.topology[key].pop(index)
		floyd_warshall_algorithm()
	
	def _handle_LinkEvent(self, event):
		try:
			dpid2index = self.dpidlist.index(event.link.dpid2)
			dpid1index = self.dpidlist.index(event.link.dpid1)
		except ValueError:
			return
		if(event.added):
			if(self.topology[event.link.dpid1][dpid2index] is not None):
				self.topology[event.link.dpid1][dpid2index] = event.link.port1
				self.topology[event.link.dpid2][dpid1index] = event.link.port2
				floyd_warshall_algorithm()
		else:
			self.topology[event.link.dpid1][dpid2index] = None
			self.topology[event.link.dpid2][dpid1index] = None
			floyd_warshall_algorithm()
	
	def floyd_warshall_algorithm():
		
