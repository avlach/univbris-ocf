#construct an interval tree structure
#author: Vasileios Kotronis
#based on:
#-- http://en.wikipedia.org/wiki/Interval_tree --> main source #1
#-- http://code.activestate.com/recipes/286239-binary-ordered-tree/ -->main source #2
#additional sources:
#-- http://hackmap.blogspot.ch/2008/11/python-interval-tree.html
#-- C++-->python porting from http://code.google.com/p/intervaltree/
#-- http://forrst.com/posts/Interval_Tree_implementation_in_python-e0K
#-- https://github.com/misshie/interval-tree/blob/master/lib/interval_tree.rb
#-- http://code.activestate.com/recipes/457411-an-interval-mapping-data-structure/ 


class IValNode(object):
	
	def __init__(self, low_end, high_end, value):
		self.low_end = low_end
		self.high_end = high_end
		self.max_high = 0
		self.value = value
		self.left = None
		self.right = None
		self.parent = None
		
	
class IValTree(object):
	
	def __init__(self):
		self.root = None
		
	def addIVal(self, root, start, stop, value):
		if root == None:
			root = IvalNode(start, stop, value)
		else:
			root.max_high = max(root.max_high, stop)
			if start <= root.low_end:
				root.left = self.addIVal(root.left, start, stop, value)
				root.left.parent = root
			else:
				root.right = self.addIVal(root.right, start, stop, value)
				root.right.parent = root
		return root
	
	def remIVal(self, root, start, stop, value):
		iValList = self.findOverlapIVal(root, start, stop,  [])
		for i in range(len(iValList)):
			if iValList[i].value == value:
				break
		node_to_remove = iValList[i]
		if node_to_remove is None:
			print "The current interval is non-existent!"
		else if node_to_remove.parent is None: #This is the current root
			if node_to_remove.left is None:
				if node_to_remove.right is None:
					root = None
				else:
					node_to_remove.right.parent = None
					root = node_to_remove.right
			else:
				if node_to_remove.right is None:
					node_to_remove.left.parent = None
					root = node_to_remove.left
				else:
					
		else:
			if node_to_remove.low_end <= node_to_remove.parent.low_end: #node is at the left
				node_to_remove.parent.left = node_to_remove.left
				rec_node = node_to_remove.parent
				while rec_node != None:
					rec_node = rec_node.parent
					rec_node.max_high = max(rec_node.left.max_high, rec_node.right.max_high)
					if rec_node.left is None or rec_node.right is None
			else: #node is at the right
				node_to_remove.parent.right = node_to_remove.right
				
		node_to_remove = None		
		
		return root
			
		else:
			
	def findOverlapIVal(self, root, start, stop, clashList):
		cList = clashList
		if root != None:
			if root.low_end > stop:
				self.findOverlapIVal(root.left, start, stop, cList)
			elif root.high_end < start:
				if root.max_high > start:
					findOverlapIVal(root.left, start, stop, cList)
					findOverlapIVal(root.right, start, stop, cList)
			else:
				cList = cList + [root]
		return cList
	
	def depth(self, root):
		if root == None:
			return 0
		else:
			ldpeth = self.depth(root.left)
			rdepth = self.depth(root.right)
			return max(ldepth, rdpeth) + 1
	
	def size(self, root):
		if root == None:
			return 0
		else:
			return self.size(root.left) + 1 + self.size(root.right)
			
	def printTree(self, root):
		if root == None:
			pass
		else:
			print "ival [" + root.low_end + "-" + root.high_end + "] : " + value + ", "
			self.printTree(root.left)
			self.printTree(root.right)

	
	
	
