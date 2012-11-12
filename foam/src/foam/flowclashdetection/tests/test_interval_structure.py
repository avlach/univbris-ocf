from foam.flowclashdetection.interval_structure import IValNode, IValTree

if __name__ == "__main__":
	
	ivtree = IValTree()
	print "Test 1"
	ivtree.root = ivtree.addIVal(ivtree.root, 10, 20, "slice1")
	ivtree.printTree(ivtree.root) 
	print "Test 2"
	ivtree.root = ivtree.addIVal(ivtree.root, 30, 50, "slice2")
	ivtree.printTree(ivtree.root)
	print "Test 3"
	ivtree.root = ivtree.addIVal(ivtree.root, 20, 60, "slice3")
	ivtree.printTree(ivtree.root)
	print "Test 4"
	ivtree.printOverlapList(ivtree.findOverlapIVal(ivtree.root, 30, 40, []), 30, 40)
	print "Test 5"
	ivtree.remIVal(ivtree.root, 10, 20, "slice1")
	ivtree.printTree(ivtree.root)