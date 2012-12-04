#approval script refactored for OFELIA needs by Vasileios Kotronis
#in the following I use the prefix "of" to distuingish between the 
#foam's internal approval script and the current one (tailored for OFELIA)

import logging
import uuid

from foamext.IPy import IP
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.core.log import KeyAdapter
from foam.openflow.types import Port
from foam.geni.approval import UnknownApprovalMode, ApprovalFailure, \
															 UncoveredFlowspecs, ConflictingPorts, \
															 UnboundedDatapath, VLANPresence,			 \
															 NoDatapaths, PortAlyzer, PortGroup, 	 \
															 IllegalPortGroupValue, IllegalUserURNValue, \
															 updatePortGroups, updateUserURNs, setMode
from foam.flowclashdetection.mechanism import MACIValTree, ETherTypeIValTree, \
																							VLANIValTree, IPSubnetIValTree, \
																							NWProtoIValTree, TPPortIValTree
from foam.ethzlegacyoptinstuff.flowspaceutils import int_to_dotted_ip, dotted_ip_to_int, \
																										 mac_to_int, int_to_mac

NEVER = 0
ALWAYS = 1
RULES = 2

def of_rebuildDB ():
	of_AppData.rebuild()
	
def of_analyzeForApproval (sliver):
	flog = logging.getLogger("foam")
  
	if of_AppData.approveUser(sliver.getUserURN()):
		return True

	try:
		of_AppData.validateSliver(sliver)
		return True
	except (ApprovalFailure, UncoveredFlowspecs), e:
		flog.info("Sliver (%s) pended: %s" % (sliver.getURN(), str(e)))
		sliver.setPendReason(str(e))
		sliver.store()
		return False
	except Exception, e:
		flog.exception("[Approval] Sliver (%s) pended because of untrapped exception" % (sliver.getURN()))
	
	
class MACConflict(ApprovalFailure):
	def __init__ (self, mac):
		super(MACConflict, self).__init__()
		self.mac = mac
	def __str__ (self):
		return "MAC Address (%s) is already reserved by another sliver." % (self.mac)

class EtherTypeConflict(ApprovalFailure):
	def __init__ (self, dltype):
		super(EtherTypeConflict, self).__init__()
		self.dltype = dltype
	def __str__ (self):
		return "Ethertype (%s) is already reserved by another sliver." % (self.dltype)

class VLANConflict(ApprovalFailure):
	def __init__ (self, vlanid):
		super(VLANConflict, self).__init__()
		self.vlanid = vlanid
	def __str__ (self):
		return "VLAN (%s) is already reserved by another sliver." % (self.vlanid)
		
class IPSubnetConflict(ApprovalFailure):
	def __init__ (self, subnet):
		super(IPSubnetConflict, self).__init__()
		self.subnet = subnet
	def __str__ (self):
		return "IP Subnet (%s) is already reserved by another sliver." % (str(self.subnet))
		
class TPPortConflict(ApprovalFailure):
	def __init__ (self, tpport):
		super(TPPortConflict, self).__init__()
		self.tpport = tpport
	def __str__ (self):
		return "Transport protocol port (%s) is already reserved by another sliver." % (self.tpport)
		
		
class of_ApprovalData(object):
	def __init__ (self, slivers = None):
		self._log = KeyAdapter("OFELIA Approval", logging.getLogger("foam"))
		self._initCore()
		self._build(slivers)
	
	def _build (self, slivers):
		self._loadSlivers(slivers)
		self._loadPortGroups()
		self._loadUserURNs()
		self._buildIValTrees(slivers)
		
	def _buildIValTrees(self, slivers): #dl type and NW proto not needed to ne handled by a tree structure
		MACTree = MACIValTree()
		VLANTree = VLANIValTree()
		IPSubnetTree = IPSubnetIValTree()
		TPPortTree = TPPortIValTree()
		
		for sliv in slivers:
			fspecs = sliv.getFlowspecs()
			for fs in fspecs:
					
				#build MAC tree from pool of MACS
				newInterval = True
				previntmac = None
				for mac in sorted(fs.getMACs()):
					intmac = mac_to_int(mac)
					if newInterval == True:	#new interval encountered
						MACstart = intmac
						MACstop = intmac
					else:
						if previntmac != None: 
							if (intmac - previntmac) == 1:	#still within the interval
								MACstop = intmac
								newInterval = False
							else:	#register the interval
								MACTree.addIVal(MACTree, MACstart, MACstop, sliv.getURN())
								newInterval = True
					previntmac = intmac
				
				#build VLAN tree from pool of VLANs
				newInterval = True
				previntvlanid = None
				for vlanid in sorted(fs.getVLANs()):
					intvlanid = int(vlanid)
					if newInterval == True:	#new interval encountered
						VLANstart = intvlanid
						VLANstop = intvlanid
					else:
						if previntvlanid != None: 
							if (intvlanid - previntvlanid) == 1:	#still within the interval
								VLANstop = intvlanid
								newInterval = False
							else:	#register the interval
								VLANTree.addIVal(VLANTree, VLANstart, VLANstop, sliv.getURN())
								newInterval = True
					previntvlanid = intvlanid
					
				#build IP address tree from pool of IP subnets (first make them intervals)
				for IPSub in fs.getIPSubnets():
					IPSubLen = IP(IPSub).len()
					[IPaddstr, NMstr] = IPSub.split("/")
					IPstart = IP(IPaddstr).strDec()
					IPstop = IPstart + IPSubLen
					IPSubnetTree.addIVal(IPSubnetTree, IPstart, IPstop, sliv.getURN())
				
				#build TP port tree from pool of TP ports
				newInterval = True
				previnttpport = None
				for tpport in sorted(fs.getTPPorts()):
					inttpport = int(tpport)
					if newInterval == True:	#new interval encountered
						TPPortstart = inttpport
						TPPortstop = inttpport
					else:
						if previnttpport != None: 
							if (inttpport - prevtpport) == 1:	#still within the interval
								TPPortstop = tpport
								newInterval = False
							else:	#register the interval
								TPPortTree.addIVal(TPPortTree, TPPortstart, TPPortstop, sliv.getURN())
								newInterval = True
					previnttpport = inttpport
				 
			
	def _initCore (self):
		self._macs = set()
		self._ethertypes = set()
		self._vlans = set()
		self._subnets = set()
		self._nwprotos = set() #transport protocol over IP (UDP, TCP)
		self._tpports = set()
		self._portgroups = {}
		self._urns = set()
	
	def _loadSlivers (self, slivers):
		for sliver in slivers:
			self.addSliver(sliver)
	
	def _loadPortGroups (self):
		groups = ConfigDB.getConfigItemByKey("geni.openflow.portgroups").getValue()
		if groups is None:
			return
		self._portgroups = groups
	
	def _updatePGData (self):
		groups = ConfigDB.getConfigItemByKey("geni.openflow.portgroups").write(self._portgroups)
	
	def rebuild (self):
		self._log.info("Rebuilding approval database")
		self._initCore()
		self._build(GeniDB.getSliverList(False, True, True))
	
	def _loadUserURNs (self):
		urns = ConfigDB.getConfigItemByKey("geni.approval.user-urns").getValue()
		if urns is None:
			return
		for urn in urns:
			self._urns.add(urn)
	
	def createPortGroup (self, name, desc):
		pg = PortGroup()
		pg.name = name
		pg.desc = desc
		self._portgroups[str(pg.uuid)] = pg
		self._updatePGData()
		return pg
	
	def getPortGroup (self, pgid):
		return self._portgroups[pgid]
	
	def getPortGroups (self):
		return self._portgroups
	
	def addUserURN (self, urn, user = None):
		item = ConfigDB.getConfigItemByKey("geni.approval.user-urns")
		if user:
			user.assertPrivilege(item.getRWAttrs())
		self._urns.add(urn)
		item.write(self._urns)
	
	def removeUserURN (self, urn, user = None):
		item = ConfigDB.getConfigItemByKey("geni.approval.user-urns")
		if user:
			user.assertPrivilege(item.getRWAttrs())
		self._urns.discard(urn)
		item.write(self._urns)
	
	def approveUser (self, urn):
		if urn in self._urns:
			return True
		else:
			return False
	
	def validateSliver (self, sliver):
		if not ConfigDB.getConfigItemByKey("geni.openflow.analysis-engine").getValue():
			return

		fspecs = sliver.getFlowspecs()
	
	
			has_dps = False
				dps = fs.getDatapaths()
				if not dps:
					raise NoDatapaths(fs)

				pl = PortAlyzer(self._portgroups)
				pl.validate(dps)
				
				if fs.hasVLANs():
					raise VLANPresence(fs)

				if not covered:
					uncovered_fs.append(fs)

		if uncovered_fs:
			raise UncoveredFlowspecs(uncovered_fs)
			
	def addSliver (self, sliver):



		
		
from foam.core.configdb import ConfigDB

of_AppData = of_ApprovalData(GeniDB.getSliverList(False, True, True))
