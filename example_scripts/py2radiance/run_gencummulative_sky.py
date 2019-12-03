import os 
from py4design import py2radiance, py3dmodel

def avg_daysim_res(res):
    """
    for daysim hourly simulation
    """     
    cumulative_list = []
    sunuphrs = rad.sunuphrs
    print(sunuphrs)
    illum_ress = []
    for sensorpt in res:
        cumulative_sensorpt = sum(sensorpt)
        avg_illuminance = cumulative_sensorpt
        cumulative_list.append(cumulative_sensorpt)
        illum_ress.append(avg_illuminance)
        
    return illum_ress
        
#create all the relevant folders 
current_path = os.path.dirname(__file__)
base_filepath = os.path.join(current_path, 'base.rad')
data_folderpath = os.path.join(current_path, 'py2radiance_data_cummulativesky')
display2dlist = []
#initialise py2radiance 
rad = py2radiance.Rad(base_filepath, data_folderpath)

#create a box 10x10x10m
box = py3dmodel.construct.make_box(10,10,10)
occfaces = py3dmodel.fetch.faces_frm_solid(box)
cmpd = py3dmodel.construct.make_compound(occfaces)
edges = py3dmodel.fetch.topo_explorer(cmpd, "edge")
displaylist = []
displaylist.append(box)
#display2dlist.append(displaylist)

sensor_pts = []
sensor_dirs = []
face_cnt = 0
displaylist2 = []
for occface in occfaces:
    radsrfname = "srf" + str(face_cnt)
    rad_polygon = py3dmodel.fetch.points_frm_occface(occface)
    srfmat = "RAL9010_pur_white_paint"
    py2radiance.RadSurface(radsrfname,rad_polygon,srfmat,rad)
    
    #get the surface that is pointing upwards, the roof
    normal = py3dmodel.calculate.face_normal(occface)
    if normal == (0,0,1):
        #generate the sensor points
        grid_occfaces = py3dmodel.construct.grid_face(occface,3,3)
        display2dlist.extend(grid_occfaces)
        #calculate the midpt of each surface
        for grid_occface in grid_occfaces:
            midpt = py3dmodel.calculate.face_midpt(grid_occface)
            midpt = py3dmodel.modify.move_pt(midpt,normal,0.8)
            sensor_pts.append(midpt)
            sensor_dirs.append(normal)
    face_cnt+=1


#once the geometries are created initialise daysim
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
#a 60min weatherfile is generated
weatherfilepath = os.path.join(parent_path, "py2radiance", "SGP_Singapore.486980_IWEC.epw")
rad.create_rad_input_file()

#create sensor points
rad.set_sensor_points(sensor_pts,sensor_dirs)
rad.execute_cumulative_oconv("7 19", "1 1 12 31", weatherfilepath, output = "irradiance")
rad.execute_cumulative_rtrace("2")
res = rad.eval_cumulative_rad(output = "irradiance")
print(res)

print("DONE")
py3dmodel.utility.visualise_falsecolour_topo(display2dlist, res, other_occtopo_2dlist = [edges], 
                                             other_colour_list = ['WHITE'] )