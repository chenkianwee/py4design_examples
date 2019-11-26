import collections
import numpy as np
xmin, ymin, zmin, xmax, ymax, zmax = 0, 0, 0, 9, 10, 10
x = [[1,2,3], [4,5,6], [7,8,9], [10,11,12]]
zipped = zip(*x)
xs = np.array(zipped[0])
x_valid = np.logical_and((xmin <= xs),
                         (xmax >= xs))
#y = np.take(x, np.array([0, 2]), axis=0)
#print y.tolist()
#
#z = np.array([])
#if z.size == 0:
#    print "it is not empty"

x = range(10)
y = range(5,15)

a_multiset = collections.Counter(x)
b_multiset = collections.Counter(y)

overlap = list((b_multiset & a_multiset).elements())
a_remainder = list((a_multiset - b_multiset).elements())
b_remainder = list((b_multiset - a_multiset).elements())

print x
print y
print overlap
print a_remainder
print b_remainder

weekly_hr_list = [168, 336, 504, 672, 840, 1008, 1176, 1344, 1512, 1680, 1848, 2016, 2184, 2352, 2520, 2688, 
                  2856, 3024, 3192, 3360, 3528, 3696, 3864, 4032, 4200, 4368, 4536, 4704, 4872, 5040, 5208, 
                  5376, 5544, 5712, 5880, 6048, 6216, 6384, 6552, 6720, 6888, 7056, 7224, 7392, 7560, 7728, 
                  7896, 8064, 8232, 8400, 8568, 8759]

print weekly_hr_list[0:52]
print len(weekly_hr_list)


print "logical testtttt"
print x

lo = np.logical_not(np.array(x)<5)
print lo

x = []
x[-1]