#Vasileios: implementation of the flowspace collision detection engine

#from foam.flowvisor import FSAllocation
#from foam.lib import FlowSpec
import foam.geni.approval
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.flowclashdetection.interval_structure import IValNode, IValTree

class MACIValTree(IValTree):

class ETherTypeIValTree(IValTree):

class VLANIValTree(IValTree):

class IPSubnetIValTree(IValTree):
	
class NWProtoIValTree(IValTree):
	
class TPPortIValTree(IValTree):
	
	
def getAllocatedFlowSpace():

	
	#from validate sliver of approval
	'''
	fspecs = sliver.getFlowspecs()
    uncovered_fs = []
    for fs in fspecs:
      covered = False
      for mac in fs.getMACs():
        covered = True
        if mac in self._macs:
          raise MACConflict(mac)
    
      for dltype in fs.getEtherTypes():
        covered = True
        if dltype == "0x806" or dltype == "0x800":
          continue
        if dltype in self._ethertypes:
          raise EtherTypeConflict(dltype)

      for subnet in fs.getIPSubnets():
        covered = True
        net = IP(subnet)
        if net in self._subnets:
          raise IPSubnetConflict(net)
        for onet in self._subnets:
          if net.overlaps(onet):
            raise IPSubnetConflict(net)

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
		'''
		
SliverData = ApprovalData(GeniDB.getSliverList(False, True, True))

