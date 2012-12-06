#Vasileios: implementation of the flowspace collision detection engine

import foam.geni.approval
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.flowclashdetection.interval_structure import IValNode, IValTree


#I will work on it later (minor priority) --> just arrange the string representations
#of the trees and whether extra attributes are needed per tree

class MACIValTree(IValTree):
	def __init__ (self, attr):
		super(MACIValTree, self).__init__()
		self.attr = attr
		self.restr = ""
	def __str__ (self):
		print "This is the current MAC interval tree:"
		_recstrformation(self, self.root)
		print self.retstr
		
	def _recstrformation (self, root):
		if self.root is None:
			pass
		else:
			return "Interval [" + str(root.low_end) + "-" + str(root.high_end) + "] : value = " + str(root.value) + \
			", maximum high end of children = " + str(root.max_high) + ", positioned at level " + str((self.depth - self.findDepth(root) + 1)),
			if root.parent is not None:
				if root.low_end < root.parent.low_end:
					print ", is left child of interval node " + "[" + str(root.parent.low_end) \
					+ "-" + str(root.parent.high_end) + "]" + ' of value ' + str(root.parent.value)
				else:
					print ", is right child of interval node " + "[" + str(root.parent.low_end) \
					+ "-" + str(root.parent.high_end) + "]" + ' of value ' + str(root.parent.value)
			else:
				print ", is root node"
			self.printTree(root.left)
			self.printTree(root.right)
			
		return retstr
	

class VLANIValTree(IValTree):

class IPSubnetIValTree(IValTree):
	
class TPPortIValTree(IValTree):
	
#see ofeliaaproval.py for the mechanism used (at geni bucket)
	
	

