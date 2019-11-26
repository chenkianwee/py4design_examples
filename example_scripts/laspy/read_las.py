from laspy.file import File
import numpy as np

las_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las\\USGS_Lidar_Point_Cloud_NJ_SdL5_2014_18TWK325655_LAS_2015\\18TWK325655.las"
inFile = File(las_filepath, mode='r')
pts = inFile.points
coords = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
headerformat = inFile.header.header_format
print len(pts)
#class_arr = inFile.raw_classification
#print class_arr
#for c in class_arr:
#    if c == 3:
#        print "tree"

#filter all single return points of classes 3, 4, or 5 (vegetation)
veg = np.where(inFile.raw_classification == 11)
#single_veg = np.where()
coords = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
valid_pts = np.take(coords, veg, axis = 0)[0]
print len(valid_pts)
print len(veg)
print veg
#for i in veg:
#    if i == True:
#        print "tree"

## pull out full point records of filtered points, and create an XYZ array for KDTree
#single_veg_points = inFile.points[single_veg]     
#single_veg_points_xyz = np.array((single_veg_points['point']['X'], 
#                                  single_veg_points['point']['Y'],
#                                  single_veg_points['point']['Z'])).transpose()

#print len(single_veg_points_xyz)
##for spec in headerformat:
##    print(spec.name)
#    
##print inFile.header.scale
##print inFile.header.max
##print inFile.header.min
#    
#
#pointformat = inFile.point_format
##for spec in inFile.point_format:
##    print(spec.name)
#    
## Get arrays which indicate invalid X, Y, or Z values.
##print inFile.Z
##print inFile.z
#
#X_invalid = np.logical_or((inFile.header.min[0] > inFile.x),
#                          (inFile.header.max[0] < inFile.x))
#Y_invalid = np.logical_or((inFile.header.min[1] > inFile.y),
#                          (inFile.header.max[1] < inFile.y))
#Z_invalid = np.logical_or((inFile.header.min[2] > inFile.z),
#                          (inFile.header.max[2] < inFile.z))
#bad_indices = np.where(np.logical_or(X_invalid, Y_invalid, Z_invalid))

#print len(bad_indices)
#for i in bad_indices:
#    print i
inFile.close()