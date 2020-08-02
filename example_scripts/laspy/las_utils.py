# ==================================================================================================
#
#    Copyright (c) 2020, CHEN Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of gen3dcitywiz
#
#    gen3dcitywiz is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    gen3dcitywiz is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gen3dcitywiz.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import os
import numpy as np
from laspy.file import File

#===========================================================================================
#FUNCTIONS
#===========================================================================================
def get_lasfiles(path):
    filenames = os.listdir(path)
    las = []
    non_las = []
    for fname in filenames:
        fsplit = fname.split('.')
        fpath = os.path.join(path, fname)
        if fsplit[-1] == 'las':
            las.append(fpath)
        else:
            is_dir = os.path.isdir(fpath)
            if is_dir:
                non_las.append(fpath)
    return las, non_las

def get_lasfiles2(path):
    las, non_las = get_lasfiles(path)

    for nl in non_las:
        las2, non_las2 = get_lasfiles(nl)
        las.extend(las2)
    
    return las
    
def get_las_file_bdry(las_filepath):
    lasfile = File(las_filepath, mode='r')
    mx = lasfile.header.max
    mn = lasfile.header.min
    lasfile.close()
    mn.extend(mx)
    return mn

def read_laspaths(laspath_list):
    lasfile_list = []
    for laspath in laspath_list:
        lasfile = File(laspath, mode='r')
        lasfile_list.append(lasfile)
        
    return lasfile_list

def close_lasfiles(lasfile_list):
    for lasfile in lasfile_list:
        lasfile.close()

def get_coord(lasfile):
    coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
    return coords

def pts_in_bbox2d_las(lasfile, bbox):
    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[3]
    ymax = bbox[4]
    xvalid = np.logical_and(lasfile.x >= xmin, lasfile.x <= xmax)
    yvalid = np.logical_and(lasfile.y >= ymin , lasfile.y <= ymax )
    valid_indices = np.where(np.logical_and(xvalid, yvalid))
    coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
    valid_pts = np.take(coords, valid_indices, axis = 0)[0]
    return valid_pts