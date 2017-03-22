import os 
import pyliburo

def avg_daysim_res(res_dict):
    """
    for daysim hourly simulation
    """
    npts = len(res_dict.values()[0])
    sensorptlist = []
    for _ in range(npts):
        sensorptlist.append([])
        
    for res in res_dict.values():
        for rnum in range(npts):
            sensorptlist[rnum].append(res[rnum])
            
    cumulative_list = []
    sunuphrs = rad.sunuphrs
    illum_ress = []
    for sensorpt in sensorptlist:
        cumulative_sensorpt = sum(sensorpt)
        avg_illuminance = cumulative_sensorpt/sunuphrs
        cumulative_list.append(cumulative_sensorpt)
        illum_ress.append(avg_illuminance)
        
    return illum_ress
        
#create all the relevant folders 
current_path = os.path.dirname(__file__)
base_filepath = os.path.join(current_path, 'base.rad')
data_folderpath = os.path.join(current_path, 'py2radiance_data')
display2dlist = []
#initialise py2radiance 
rad = pyliburo.py2radiance.Rad(base_filepath, data_folderpath)

#create a box 10x10x10m
box = pyliburo.py3dmodel.construct.make_box(10,10,10)
occfaces = pyliburo.py3dmodel.fetch.faces_frm_solid(box)
displaylist = []
displaylist.append(box)
#display2dlist.append(displaylist)

sensor_pts = []
sensor_dirs = []
face_cnt = 0
displaylist2 = []
for occface in occfaces:
    radsrfname = "srf" + str(face_cnt)
    rad_polygon = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(occface)
    srfmat = "RAL9010_pur_white_paint"
    pyliburo.py2radiance.RadSurface(radsrfname,rad_polygon,srfmat,rad)
    
    #get the surface that is pointing upwards, the roof
    normal = pyliburo.py3dmodel.calculate.face_normal(occface)
    if normal == (1,0,0):
        #generate the sensor points
        grid_occfaces = pyliburo.py3dmodel.construct.grid_face(occface,3,3)
        display2dlist.extend(grid_occfaces)
        #calculate the midpt of each surface
        for grid_occface in grid_occfaces:
            midpt = pyliburo.py3dmodel.calculate.face_midpt(grid_occface)
            midpt = pyliburo.py3dmodel.modify.move_pt(midpt,normal,0.8)
            sensor_pts.append(midpt)
            sensor_dirs.append(normal)
    face_cnt+=1

rad.create_rad_input_file()

#once the geometries are created initialise daysim
daysim_dir = os.path.join(current_path, 'daysim_data')
rad.initialise_daysim(daysim_dir)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
#a 60min weatherfile is generated
weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
rad.execute_epw2wea(weatherfilepath)
rad.execute_radfiles2daysim()

#create sensor points
rad.set_sensor_points(sensor_pts,sensor_dirs)
rad.create_sensor_input_file()
rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
rad.execute_gen_dc("w/m2") #lux
rad.execute_ds_illum()
res_dict = rad.eval_ill()
avg_irrad = avg_daysim_res(res_dict)
print avg_irrad
print "DONE"
pyliburo.py3dmodel.construct.visualise_falsecolour_topo(avg_irrad, display2dlist, other_topo2dlist = [occfaces], other_colourlist = ['WHITE'] )
#pyliburo.py3dmodel.construct.visualise_falsecolour_topo() (display2dlist, ["WHITE"])
