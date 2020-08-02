import os
import zipfile

dirx = 'E:\\kianwee_work_data\\lidar_campus_as_lab\\lidar'

fnames = os.listdir(dirx)

for fname in fnames:
    f_list = fname.split('.')
    path = os.path.join(dirx, fname)
    if f_list[-1] == 'laz':
        os.remove(path)
        print('laz file removed:',path)
    
    elif f_list[-1] == 'zip':
        ndirx = os.path.join(dirx, f_list[0])
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(ndirx)        
        os.remove(path)
        print('zip file unzipped',path)