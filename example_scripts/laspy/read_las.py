from laspy.file import File
import numpy as np

las_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las\\USGS_Lidar_Point_Cloud_NJ_SdL5_2014_18TWK325655_LAS_2015\\18TWK325655.las"
inFile = File(las_filepath, mode='r')
pts = inFile.points
print pts[100005:200000]
coords = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()
print coords[0]
headerformat = inFile.header.header_format
for spec in headerformat:
    print(spec.name)
    
print inFile.header.scale
print inFile.header.max
print inFile.header.min
    

pointformat = inFile.point_format
for spec in inFile.point_format:
    print(spec.name)
    
# Get arrays which indicate invalid X, Y, or Z values.
print inFile.Z
print inFile.z

X_invalid = np.logical_or((inFile.header.min[0] > inFile.x),
                          (inFile.header.max[0] < inFile.x))
Y_invalid = np.logical_or((inFile.header.min[1] > inFile.y),
                          (inFile.header.max[1] < inFile.y))
Z_invalid = np.logical_or((inFile.header.min[2] > inFile.z),
                          (inFile.header.max[2] < inFile.z))
bad_indices = np.where(np.logical_or(X_invalid, Y_invalid, Z_invalid))

print bad_indices
inFile.close()
print inFile