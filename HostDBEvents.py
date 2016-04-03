from abc import ABCMeta, abstractmethod

class HostDBEvents:
	
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def hostAdded(self, hostentry):
		pass
	
	@abstractmethod
	def hostUpdated(self, oldentry, updatedentry):
		pass
	
	@abstractmethod
	def hostremoved(self, hostentry):
		pass
