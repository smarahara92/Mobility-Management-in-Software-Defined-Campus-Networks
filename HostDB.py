import time

from pox.lib.recoco import Timer

import HostDBEvents

class HostDB:
	"""
	It keep track of hosts in the network
	"""
	
	###########################################################################################################
	# Each entry in the hostentries list is list of values in following order                                 #
	# ------------------------------------------------------------------------------------------------------- #
	# | IPv6 ADDRESS | MAC ADDRESS | DATAPATH ID | PHYSICAL PORT NUMBER | TIMEOUT | LAST REFRESHED | ACTION | #
	# ------------------------------------------------------------------------------------------------------- #
	###########################################################################################################
	
	def __init__(self, eventHandler):
		self.hostentries = []
		self.eventHandler = eventHandler
		Timer(5, self.clean, recurring = True)
	
	def getHostEntries(self, searchby, value):
		return [hostentry for hostentry in self.hostentries if (hostentry[searchby] == value)]
	
	def getHostEntryField(self, searchby, value, returnby):
		for hostentry in self.hostentries:
			if(hostentry[searchby] == value):
				return hostentry[returnby]
		return None
	
	def addHost(self, ipv6, mac, dpid, pno, timeout, action, duplicateDetectionEnbled = True):
		if(duplicateDetectionEnabled):
			for hostentry in self.hostentries:
				if(hostentry[0] == ipv6):
					return
		hostentry = [ipv6, mac, dpid, pno, timeout, time.time(), action]
		self.hostenties.append(hostentry)
		self.eventHandler.hostAdded(hostentry)
	
	def updateHosts(self, searchby, value, updateby, updatedvalues):
		for hostentry in self.hostentries:
			if(hostentry[searchby] == value):
				oldentry = hostentry[0:]
				for by, updatedvalue in zip(updateby, updatedvalues):
					hostentry[by] = updatedvalue
				self.eventHandler.hostUpdated(oldentry, hostentry)
	
	def removeHosts(self, searchby, value):
		hosts = []
		for hostentry in self.hostentries:
			if(hostentry[searchby] != value):
				host.append(hostentry)
			else:
				self.eventHandler.hostRemoved(hostentry)
		self.hostentries = hosts
	
	def refreshHosts(self, searchby, value):
		curtime = time.time();
		for hostentry in self.hostentries:
			if(hostentry[searchby] == value):
				hostentry[-2] = curtime
	
	def clean(self):
		curtime = time.time()
		hosts = [hostentry for hostentry in self.hostentries if ((curtime - hostentry[-2]) < hostentry[-3])]
		self.hostentries = hosts
