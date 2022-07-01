import os
import time

import gdal
from py4design import py3dmodel
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
dtm_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\dem\\\princeton_10by10km_dem\\princeton_10by10km_dem_10meters.tif"
#dtm_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\dem\\\princeton_10by10km_dem\\test2.tif"

#specify the directory to store the results which includes
result_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains"

#specify if you want to view the result interactively
viewer = False

#split the terrain into multiple shells
split = True
#extent of each shell
x_extent = 500#m
y_extent = 500#m
#===========================================================================================
#THE RESULT FILES
#===========================================================================================
result_filepath_pt = os.path.join(result_dir, "terrain_10by10km_pt.brep")
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def raster_reader(input_terrain_raster):
    '''
    __author__ = "Paul Neitzel, Kian Wee Chen"
    __copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
    __credits__ = ["Paul Neitzel", "Jimeno A. Fonseca"]
    __license__ = "MIT"
    __version__ = "0.1"
    __maintainer__ = "Daren Thomas"
    __email__ = "cea@arch.ethz.ch"
    __status__ = "Production"
    '''
    # read raster records
    raster_dataset = gdal.Open(input_terrain_raster)
    band = raster_dataset.GetRasterBand(1)
    rangex = raster_dataset.RasterXSize
    rangey = raster_dataset.RasterYSize
    
    a = band.ReadAsArray(0, 0, raster_dataset.RasterXSize, raster_dataset.RasterYSize)
    (y_index, x_index) = np.nonzero(a)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster_dataset.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2)  # to centre the point
    if x_size <0:
        x_size = x_size*-1
    if y_size <0:
        y_size = y_size*-1
    return [(x, y, z) for x, y, z in zip(x_coords, y_coords, a[y_index, x_index])], rangex, rangey, x_size, y_size 

def convert_pyptlist2float(pyptlist):
    npyptlist = []
    cnt_list = []
    cnt = 0
    for pypt in pyptlist:
        n_pypt = (float(pypt[0]), float(pypt[1]), float(pypt[2]))
        npyptlist.append(n_pypt)
        cnt_list.append(cnt)
        cnt+=1
    return npyptlist

def convert_pyptlist2ptdict2d(pyptlist, rangex):
    pyptdict2d = {}
    cnt = 0
    for pypt in pyptlist:
        i = cnt%rangex
        j = cnt/rangex
        index = (i,j)
        z = pypt[2]
        if z < -413:
            pypt = [pypt[0], pypt[1], 0]
        pyptdict2d[index] = pypt
        cnt+=1
        
    return pyptdict2d

def extract_grid_frm_ptdict2d(pyptdict2d, npts_j, npts_i, jstart, istart):
    pyptlist = []
    for j in range(npts_j):
        j = j+jstart
        for i in range(npts_i):
            i = i+istart
            #print i,j
            pypt = pyptdict2d[(i,j)]
            pyptlist.append(pypt)
    return pyptlist

def construct_terrain(pyptlist):
    tin_occface_list = py3dmodel.construct.delaunay3d(pyptlist)
    #terrain_shell = py3dmodel.construct.make_compound(tin_occface_list)
    terrain_shell = py3dmodel.construct.sew_faces(tin_occface_list)[0]
    return terrain_shell
    
#===========================================================================================
#CONSTRUCT THE TERRAIN 
#===========================================================================================
time1 = time.clock()
display_2dlist = []
#read the tif terrain file and create a tin from it 
pyptlist, rangex, rangey, x_size, y_size  = raster_reader(dtm_file)
print rangex, rangey, x_size, y_size
pyptlist = convert_pyptlist2float(pyptlist)

print "WRITING THE POINT FILE ... ..."
vlist = py3dmodel.construct.make_occvertex_list(pyptlist)

pt_cmpd = py3dmodel.construct.make_compound(vlist)
py3dmodel.utility.write_brep(pt_cmpd, result_filepath_pt)


print "CONSTRUCTING THE TERRAIN ... ..."
if split == True:
    pyptdict2d = convert_pyptlist2ptdict2d(pyptlist,rangex)
    
    npts_extentx =  int(x_extent/x_size)
    npts_extenty =  int(y_extent/y_size)
    
    xstep = rangex/npts_extentx
    ystep = rangey/npts_extenty
            
    print xstep, ystep
    print npts_extentx, npts_extenty
    cnt_list = []
    grid_ptlist = []
    terrain_list = []
    cnt = 0
    jcnt=0
    for j in range(ystep):
        icnt = 0
        for i in range(xstep):
            istart = i*npts_extentx
            jstart = j*npts_extenty
            #print jcnt
            #print "HEADER", istart, jstart, "CNT", icnt, jcnt, "STEP", xstep-1, ystep-1
            if icnt == xstep-1 and jcnt == ystep-1:
                #print "AM AT 1"
                npts_extentx1 = rangex - istart -1
                npts_extenty1 = rangey - jstart - 1
                grid_pts = extract_grid_frm_ptdict2d(pyptdict2d, npts_extenty1+1, npts_extentx1+1, jstart, istart)
                
            elif icnt == xstep-1:
                #print "AM AT 2"
                npts_extentx1 = rangex - istart -1
                grid_pts = extract_grid_frm_ptdict2d(pyptdict2d, npts_extenty+1, npts_extentx1+1, jstart, istart)
                
            elif jcnt == ystep-1:
                #print "AM AT 3"
                npts_extenty1 = rangey - jstart - 1
                grid_pts = extract_grid_frm_ptdict2d(pyptdict2d, npts_extenty1+1, npts_extentx+1, jstart, istart)
            
            else: 
                #print "AM AT 4"
                grid_pts = extract_grid_frm_ptdict2d(pyptdict2d, npts_extenty+1, npts_extentx+1, jstart, istart)
                
            #terrain = construct_terrain(grid_pts)
            t_vlist = py3dmodel.construct.make_occvertex_list(grid_pts)
            pt_cmpd = py3dmodel.construct.make_compound(t_vlist)
            print "WRITING THE TERRAIN FILE... ...", str(cnt)
            result_filepath = os.path.join(result_dir, "terrain_10by10km_" + str(cnt) +".brep")
            result_filepath2 = os.path.join(result_dir, "terrain_10by10km_pt_" + str(cnt) +".brep")
            #py3dmodel.utility.write_brep(terrain, result_filepath)
            py3dmodel.utility.write_brep(pt_cmpd, result_filepath2)
            #terrain_list.append(terrain)
            grid_ptlist.append(grid_pts)
            cnt_list.append(cnt)
            cnt+=1
            icnt+=1
        jcnt+=1
    
    #terrain_cmpd = py3dmodel.construct.make_compound(terrain_list)
    #result_filepath = os.path.join(result_dir, "terrain_10by10km.brep")
    #py3dmodel.utility.write_brep(terrain_cmpd, result_filepath)
    
    time2 = time.clock()
    total_time = time2-time1

    print "*******Total Time Take:", total_time/60, "mins***************"
    
    if viewer == True:
        py3dmodel.utility.visualise([terrain_list, [pt_cmpd]], ["GREEN", "BLUE"])
        py3dmodel.utility.visualise_falsecolour_topo(terrain_list, cnt_list)
    
else:
    terrain = construct_terrain(pyptlist)
    print "WRITING THE TERRAIN FILE... ..."
    result_filepath = os.path.join(result_dir, "terrain_10by10km.brep")
    py3dmodel.utility.write_brep(terrain, result_filepath)
    
    time2 = time.clock()
    total_time = time2-time1

    print "*******Total Time Take:", total_time/60, "mins***************"
    
    if viewer == True:
        py3dmodel.utility.visualise([[terrain], [pt_cmpd]], ["GREEN", "BLUE"])
