from pox.openflow.nicira import nx_match
from pox.openflow.nicira import nx_flow_mod
from pox.openflow.nicira import nx_action_controller
from pox.openflow.nicira import nx_action_push_mpls
from pox.openflow.nicira import nx_action_pop_mpls
from pox.openflow.nicira import nx_action_resubmit
from pox.openflow.nicira import nx_action_set_tunnel
from pox.openflow.nicira import nx_action_set_tunnel64
from pox.openflow.nicira import nx_action_fin_timeout
from pox.openflow.nicira import nx_action_exit
from pox.openflow.nicira import nx_action_dec_ttl

from pox.openflow.libopenflow_01 import ofp_action_output
from pox.openflow.libopenflow_01 import ofp_action_enqueue
from pox.openflow.libopenflow_01 import ofp_action_strip_vlan
from pox.openflow.libopenflow_01 import ofp_action_vlan_vid
from pox.openflow.libopenflow_01 import ofp_action_vlan_pcp
from pox.openflow.libopenflow_01 import ofp_action_dl_addr
from pox.openflow.libopenflow_01 import ofp_action_nw_addr
from pox.openflow.libopenflow_01 import ofp_action_nw_tos
from pox.openflow.libopenflow_01 import ofp_action_tp_port
from pox.openflow.libopenflow_01 import ofp_features_request

from pox.core import core

from pox.lib.addresses import EthAddr, IPAddr, IPAddr6

class Switch:
	"""
	The class provide api for get ports information and manipulate flow tables
	Each object of this type is communicate with only one openflow switch
	"""
	
	match_attributes = {
			'in_port' : (None, None, False, int),
			'eth_dst' : (None, None, True, EthAddr),
			'eth_src' : (None, None, True, EthAddr),
			'eth_type' : (None, None, False, int),
			'ip_proto' : (['eth_type'], [[0x0800, 0x86dd]], False, int),
			'ip_src' : (['eth_type'], [[0x0800]], True, IPAddr),
			'ip_dst' : (['eth_type'], [[0x0800]], True, IPAddr),
			'tcp_src' : (['ip_proto'], [[6]], False, int),
			'tcp_dst' : (['ip_proto'], [[6]], False, int),
			'udp_src' : (['ip_proto'], [[17]], False, int),
			'udp_dst' : (['ip_proto'], [[17]], False, int),
			'sctp_src' : (['ip_proto'], [[132]], False, int),
			'sctp_dst' : (['ip_proto'], [[132]], False, int),
			'icmp_type' : (['ip_proto'], [[1]], False, int),
			'icmp_code' : (['ip_proto'], [[1]], False, int),
			'arp_op' : (['eth_type'], [[0x0806]], False, int),
			'arp_spa' : (['eth_type'], [[0x0806]], True, IPAddr),
			'arp_tpa' : (['eth_type'], [[0x0806]], True, IPAddr),
			'arp_sha' : (['eth_type'], [[0x0806]], True, EthAddr),
			'arp_tha' : (['eth_type'], [[0x0806]], True, EthAddr),
			'ipv6_src' : (['eth_type'], [[0x86dd]], True, IPAddr6),
			'ipv6_dst' : (['eth_type'], [[0x86dd]], True, IPAddr6),
			'ipv6_flabel' : (['eth_type'], [[0x86dd]], True, int),
			'icmpv6_type' : (['ip_proto'], [[58]], True, int),
			'icmpv6_code' : (['ip_proto'], [[58]], True, int),
			'nd_target' : (['icmpv6_type'], [[135, 136]], False, IPAddr6),
			'nd_sll' : (['icmpv6_type'], [[135]], False, EthAddr),
			'nd_tll' : (['icmpv6_type'], [[136]], False, EthAddr),
			'mpls_label' : (['eth_type'], [[0x8847, 0x8848]], False, int),
			'mpls_tc' : (['eth_type'], [[0x8847, 0x8848]], False, int),
			'mpls_bos' : (['eth_type'], [[0x8847, 0x8848]], False, int),
			'tun_id' : (None, None, True, int),
			'ipv6_exthdr' : (['eth_type'], [[0x86dd]], True, int),
		      }
	
	flowmod_attributes = {
				'cookie' : int,
				'cookie_mask' : int,
				'table_id' : int,
				'command' : int,
				'idle_timeout' : int,
				'hard_timeout' : int,
				'priority' : int,
				'buffer_id' : int,
				'out_port' : int,
				'out_group' : int,
				'flags' : int
			     }
	
	action_attributes = {
				'output' : (ofp_action_output, True, {'port' : int, 'max_len' : int}),
				'enqueue' : (ofp_action_enqueue, True, {'port' : int, 'queue_id' : int}),
				'strip_vlan' : (ofp_action_strip_vlan, False, {}),
				'vlan_vid' : (ofp_action_vlan_vid, True, {'vlan_vid' : int}),
				'vlan_pcp' : (ofp_action_vlan_pcp, True, {'vlan_pcp' : int}),
				'set_dl_src' : (ofp_action_dl_addr.set_src, True, {'dl_addr' : EthAddr}),
				'set_dl_dst' : (ofp_action_dl_addr.set_dst, True, {'dl_addr' : EthAddr}),
				'set_nw_src' : (ofp_action_nw_addr.set_src, True, {'nw_addr' : IPAddr}),
				'set_nw_dst' : (ofp_action_nw_addr.set_dst, True, {'nw_addr' : IPAddr}),
				'set_tos' : (ofp_action_nw_tos, True, {'nw_tos' : int}),
				'set_tp_src' : (ofp_action_tp_port.set_src, True, {'tp_port' : int}),
				'set_tp_dst' : (ofp_action_tp_port.set_dst, True, {'tp_port' : int}),
				'send_to_controller' : (nx_action_controller, True, {'max_len' : int, 'controller_id':int, 'reason':int}),
				'push_mpls' : (nx_action_push_mpls, False, {}),
				'pop_mpls' : (nx_action_pop_mpls, False, {'ethertype', int}),
				'resubmit' : (nx_action_resubmit.resubmit, True, {'in_port' : int}),
				'resubmit_to_table' : (nx_action_resubmit.resubmit_table, True, {'table' : int, 'in_port' : int}),
				'set_tunnel' : (nx_action_set_tunnel, True, {'tun_id' : int}),
				'set_tunnel64' : (nx_action_set_tunnel64, True, {'tun_id' : int}),
				'fin_timeout' : (nx_action_fin_timeout, True, {'fin_idle_timeout' : int, 'fin_hard_timeout' : int}),
				'exit' : (nx_action_exit, False, {}),
				'dec_ttl' : (nx_action_dec_ttl, False, {})
			    }
	
	def __init__(self, connection, confile):
		self.connection = connection
		self._initialize(confile)
		connection.addListeners(self)
	
	def _handle_PortStatus(self, event):
		"""
		The method sends features_request message every time it receives
		PortStatus message so that the object always contains upto date
		information of ports
		"""
		connection.send(ofp_features_request())
	
	def getMacAddressbyNum(self, portnum):
		for port in self.connection.features.ports:
			if(port.port_no == portnum):
				return port.hw_addr
		return None
	
	def getMacAddressbyName(self, portname):
		for port in self.connection.features.ports:
			if(port.name == portname):
				return port.hw_addr
		return None
	
	def _initialize(self, switchconfile):
		confile = open(switchconfile, 'r')
		for flowrule in confile:
			try:
				flowruledict = {}
				flowfields = flowrule.split(' ')
				for field in flowfields:
					item = field.split("=")
					item[0] = item[0].strip()
					item[1] = item[1].strip()
					if(self.match_attributes.has_key(item[0])):
						flowruledict[item[0]] = self.match_attributes[item[0]][-1](item[1])
					elif(self.flowmod_attributes.has_key(item[0])):
						flowruledict[item[0]] = self.flowmod_attributes[item[0]](item[1])
					elif(self.action_attributes.has_key(item[0])):
						actionfields = item[1].split(",")
						types = self.action_attributes[item[0]][-1]
						flowruledict[item[0]] = {}
						for actionfield in actionfields:
							actionitem = actionfield.split(":")
							flowruledict[item[0]][actionitem[0]] = types[actionitem[0]](actionitem[1])
			except Exception:
				raise Exception("Error at : " + flowrule)
			self.modify_flow_table(**flowruledict)
	
	def _verify_attributes(self, verifiableobj, attriblist, posattribvalues):
		"""
		verifiableobj = The object, which we want to verify its attributes
		attriblist = list of names of attributes
		posattribvalues =  list of list of possible attribute values of a attribute in attriblist 
				   which has same index as current index of the list.
				   If it has no possible values it must be empty list
		"""
		for attribname, posattribvalues in zip(attriblist, posattribvalues):
			try:
				attribute = verifiableobj.__getattr__(attribname)
				attributeok = True
				for posvalue in posattribvalues:
					if(posvalue == attribute):
						return True
					else:
						attributeok = False
				return attributeok
			except AttributeError:
				return False
		return True
	
	
	def modify_flow_table(self, **kwargs):
		"""
		The method will modify flow tables of the openflow switch as per arguments.
		It takes variable number of named arguments, these names must match with
		the names defined in static dictionaries of this class.
		"""

		match = nx_match()
		flowmod = nx_flow_mod()
		prelen = len(kwargs) + 1
		while(len(kwargs) < prelen):
			prelen = len(kwargs)
			prekey = None
			for key in kwargs.keys():
				value = kwargs[key]
				if(prekey != None):
					kwargs.pop(prekey)
					prekey = None
				try:
					if(self.match_attributes.has_key(key)):
						record = self.match_attributes[key]
						if((record[0] == None) or self._verify_attributes(match, record[0], record[1])):
							if(record[2] and (type(value) is str) and (value.find("/") != -1)):
								fields = value.split("/")
								match.__setattr__(key, record[-1](fields[0]))
								match.__setattr__(key + "_mask", record[-1](fields[1]))
							else:
								match.__setattr__(key, value)
							prekey = key
					elif(self.flowmod_attributes.has_key(key)):
						flowmod.__setattr__(key, value)
						prekey = key
					elif(self.action_attributes.has_key(key)):
						record = self.action_attributes[key]
						if(record[1]):
							flowmod.actions.append(record[0](**value))
						else:
							flowmod.actions.append(record[0]())
						prekey = key
				except Exception as e:
					return
			if(len(kwargs) == prelen):
				break
		flowmod.match = match
		print flowmod

#switch = Switch("conf.txt")
#switch.modify_flow_table(in_port=30, eth_type=34525, ip_proto=58, icmpv6_type=135, idle_timeout=50, nd_sll="12:23:34:45:56:67", output={'port': 20}, set_dl_src = {'dl_addr' : "23:34:45:56:67:78"})
