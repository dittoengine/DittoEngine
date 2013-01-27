import time

def timeFunction(func, args=None):
   if args is None:
      args = []
   print "-- Starting testing --"
   t1 = time.clock()
   func(*args)
   t2 = time.clock()
   print "-- Finished testing --"
   print "Function took %f secs to execute" % (t2-t1)
