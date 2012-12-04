#Vasileios: implementation of the flowspace collision detection engine

#from foam.flowvisor import FSAllocation
#from foam.lib import FlowSpec
import foam.geni.approval
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.flowclashdetection.interval_structure import IValNode, IValTree

class MACIValTree(IValTree):

#class ETherTypeIValTree(IValTree):

class VLANIValTree(IValTree):

class IPSubnetIValTree(IValTree):
	
#class NWProtoIValTree(IValTree):
	
class TPPortIValTree(IValTree):
	
#see ofeliaaproval.py for the mechanism used (at geni bucket)
	
	

