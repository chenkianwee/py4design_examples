import os 
import time
from py4design import py2radiance, py3dmodel, urbangeom

#===========================================================================================
#INPUTS
#===========================================================================================
bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bldg.brep"
#create all the relevant folders 
current_path = os.path.dirname(__file__)
base_filepath = os.path.join(current_path, 'base.rad')

data_folder = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\rad"
daysim_data_folder = os.path.join(data_folder, 'py2radiance_data')
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def avg_daysim_res(res):
    """
    for daysim hourly simulation
    """     
    cumulative_list = []
    #sunuphrs = rad.sunuphrs
    #illum_ress = []
    for sensorpt in res:
        cumulative_sensorpt = sum(sensorpt)
        #avg_illuminance = cumulative_sensorpt
        cumulative_list.append(cumulative_sensorpt)
        #illum_ress.append(avg_illuminance)
        
    return cumulative_list

def write_res2csv(result, sensor_pts, csv_res_filepath):
    nsensors = len(sensor_pts)
    strx = "x,y,z"
    for i in range(8760):
        if i == 8760-1:
            strx = strx + "," + str(i+1) + "\n"
        else:
            strx = strx + "," + str(i+1)
        
    for cnt in range(nsensors):
        hourly = result[cnt] #8760
        sensor_pt = sensor_pts[cnt]
        x = sensor_pt[0]
        y = sensor_pt[1]
        z = sensor_pt[2]
        strx = strx + str(x) + "," + str(y) + "," + str(z)
        hcnt = 0
        for hour in hourly:
            if hcnt == 8760-1:
                strx = strx + "," + str(hour) + "\n"
            else:
                strx = strx + "," + str(hour)
            hcnt+=1
    
    f = open(csv_res_filepath, "w")
    f.write(strx)
    f.close()
    
#===========================================================================================
#MAIN
#===========================================================================================
time1 = time.clock()
display2dlist = []
#initialise py2radiance 
rad = py2radiance.Rad(base_filepath, daysim_data_folder)

bldg_cmpd = py3dmodel.utility.read_brep(bldg_filepath)
bldg_solids = py3dmodel.fetch.topo_explorer(bldg_cmpd, "solid")

roof_list = []
facade_list = []
footprint_list = []

for bldg_solid in bldg_solids:
    facades, roofs, footprints = urbangeom.identify_building_surfaces(bldg_solid)
    facade_list.extend(facades)
    roof_list.extend(roofs)
    footprint_list.extend(footprints)

srf_list = facade_list + roof_list + footprint_list
srf_cnt = 0
for surface in srf_list:
    srfname = "srf" + str(srf_cnt)
    surface = py3dmodel.modify.fix_face(surface)        
    srf_polygon = py3dmodel.fetch.points_frm_occface(surface)
    srfmat = "RAL9010_pur_white_paint"
    py2radiance.RadSurface(srfname,srf_polygon,srfmat,rad)
    srf_cnt += 1

rad.create_rad_input_file()

#roof_list = roof_list[0:10]
sensor_pts = []
sensor_dirs = []
for roof in roof_list:
    normal = py3dmodel.calculate.face_normal(roof)
    nx = round(normal[0],1)
    ny = round(normal[1],1)
    nz = round(normal[2],1)
    normal = [nx, ny, nz]
    #generate the sensor points
    mv_roof = py3dmodel.modify.move([0,0,0], [0,0,0.05], roof)
    mv_roof = py3dmodel.fetch.topo_explorer(mv_roof, "face")[0]
    
    grid_occfaces = py3dmodel.construct.grid_face(mv_roof,10,10)
    display2dlist.extend(grid_occfaces)
    #calculate the midpt of each surface
    for grid_occface in grid_occfaces:
        midpt = py3dmodel.calculate.face_midpt(grid_occface)
        sensor_pts.append(midpt)
        sensor_dirs.append(normal)

sensor_pts = sensor_pts[0:100]
sensor_dirs = sensor_pts[0:100]
#once the geometries are created initialise daysim
daysim_dir = os.path.join(data_folder, 'daysim_data')
rad.initialise_daysim(daysim_dir)

#a 60min weatherfile is generated
weatherfilepath = "F:\\kianwee_work\\digital_repository\\epw\\USA_NJ_Trenton-Mercer.County.AP.724095_TMY3.epw"
rad.execute_epw2wea(weatherfilepath)
rad.execute_radfiles2daysim()

#create sensor points
rad.set_sensor_points(sensor_pts,sensor_dirs)
rad.create_sensor_input_file()
rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
rad.execute_gen_dc("w/m2") #w/m2 or lux
rad.execute_ds_illum()
res = rad.eval_ill_per_sensor()
#write_res2csv(res, sensor_pts, csv_res_filepath)
time2 = time.clock()
total_time = time2-time1
print "*******Time Take:", total_time/60, "mins***************"
print "DONE"
#py3dmodel.utility.visualise_falsecolour_topo(display2dlist, lx_ress, other_occtopo_2dlist = [facade_list], other_colour_list = ['WHITE'] )