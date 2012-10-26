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
		self.value = value
		self.left = None
		self.right = None
		self.max_high = 0
		

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
			else:
				root.right = self.addIVal(root.right, start, stop, value)
		return root
	
	#work needs to be done in removal...
	def remIVal(self, parent, root, value):
		if root == None:
			pass
		else:
			if root.value == value:
				if root is parent.left:

					parent.left = root.left
					
				else:
					parent.right = root.right
				
			self.remIVal(root, root.left, value)
			self.remIVal(root, root.right, value)
		
		
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
			print "[" + root.low_end + "-" + root.high_end + "] : " + value 
			self.printTree(root.left)
			self.printTree(root.right)

	
	
	
