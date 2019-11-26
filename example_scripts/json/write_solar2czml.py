import os 
import time
import json
import datetime
from datetime import timedelta

import shapefile
from py4design import py3dmodel, shp2citygml, shapeattributes

#===========================================================================================
#INPUTS
#===========================================================================================
shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_roofs\\main_campus_roofs_wgs84.shp"
json_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\json"

czml_dir = "F:\\kianwee_work\\spyder_workspace\\geojsonexamples\\czml"
filename = "roofsolar"
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list
        
def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)
        
def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list

def gen_dates(start_date, end_date, tdelta):
    date_list = []
    cur_date = start_date
    while cur_date <= end_date:
        cur_date = cur_date + tdelta
        date_str = cur_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        date_list.append(date_str)
    return date_list

def pyptlist2cartesians(pyptlist):
    cartesians = []
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]
        z = pypt[2]
        cartesians.append(x)
        cartesians.append(y)
        cartesians.append(z)
        
    return cartesians
    
def write2czml(roof_list, mthly_list, start_date, end_date, tdelta, minmax):
    sdate_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    edate_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    czml = [{"id" : "document",
             "name" : "Roof Solar Analysis",
             "version" : "1.0",
             "clock": { "interval": sdate_str + "/" + edate_str,
                       "currentTime": sdate_str,
                       "multiplier": 60
                       }
             }]
    
    minx = minmax[0]
    maxx = minmax[1]
    rcnt = 0
    for roof in roof_list:
        roof_uid = roof.get_value("uid")
        roof_face = roof.shape
        wires = py3dmodel.fetch.topo_explorer(roof_face, "wire")
        nwires = len(wires)
        entity = {"id": roof_uid, 
                  "polygon": {"positions": [], 
                              "material": {"solidColor": {"color": []}}}}
        
        polygon = entity["polygon"]
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(roof_face)
            polygon["holes"] = [{"cartographicDegrees":[]}]
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                        
                    cartesians = pyptlist2cartesians(pyptlist)
                    polygon["positions"].append({"cartographicDegrees": cartesians})
                    
                else: #means its a hole not a face
                    if is_anticlockwise2:
                        pyptlist.reverse()
                        
                    cartesians = pyptlist2cartesians(pyptlist)
                    polygon["holes"][0]["cartographicDegrees"].append(cartesians)
            
        else:
            #get the positions of each polygon
            pyptlist = py3dmodel.fetch.points_frm_occface(roof_face)
            is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if not is_anticlockwise2:
                pyptlist.reverse()
            
            cartesians = pyptlist2cartesians(pyptlist)
            polygon["positions"].append({"cartographicDegrees": cartesians})
        
  
        suid_list = []
        #wrte the material property
        for mth in mthly_list:
            suid = mth["uid"]
            suid_list.append(suid)
        
        index = suid_list.index(roof_uid)
        res_4_aroof = mthly_list[index]["solar"]
        res_4_aroof = res_4_aroof[0:24] 

        date_list = gen_dates(start_date, end_date, tdelta)
        
        pcnt = 0
        for res in res_4_aroof:
            if res > 0:
                interval_t1 = date_list[pcnt]
                interval_t2 = date_list[pcnt+1]
                r,g,b = py3dmodel.utility.pseudocolor(res, minx, maxx)
                rgba = [int(r*255),int(g*255),int(b*255),255]
                colour_interval = {"interval": interval_t1 + "/" + interval_t2,
                                   "rgba": rgba}
                
                polygon["material"]["solidColor"]["color"].append(colour_interval)
                #print interval_t1, interval_t2 
            pcnt+=1

        czml.append(entity)
        rcnt+=1
    return czml
#===========================================================================================
#MAIN
#===========================================================================================
#
#{
#    "id" : "dynamicPolygon",
#    "name": "Dynamic Polygon with Intervals",
#    "availability":"2012-08-04T16:00:00Z/2012-08-04T17:00:00Z",
#    "polygon": {
#        "positions": [{
#            "interval" : "2012-08-04T16:00:00Z/2012-08-04T16:20:00Z",
#            "cartographicDegrees" : [
#                -50, 20, 0,
#                -50, 40, 0,
#                -40, 40, 0,
#                -40, 20, 0
#            ]
#        }, {
#            "interval" : "2012-08-04T16:20:00Z/2012-08-04T16:40:00Z",
#            "cartographicDegrees": [
#                -35, 50, 0,
#                -35, 10, 0,
#                -45, 30, 0
#            ]
#        }, {
#            "interval" : "2012-08-04T16:40:00Z/2012-08-04T17:00:00Z",
#            "cartographicDegrees" : [
#                -35, 50, 0,
#                -40, 50, 0,
#                -40, 20, 0,
#                -35, 20, 0
#            ]
#        }],
#        "holes": [{
#            "interval" : "2012-08-04T16:00:00Z/2012-08-04T16:20:00Z",
#            "cartographicDegrees" : [
#                [
#                    -47, 35, 0,
#                    -46, 25, 0,
#                    -42, 30, 0
#                ]
#            ]
#        }],
#        "material": {
#            "solidColor": {
#                "color": [{
#                    "interval" : "2012-08-04T16:00:00Z/2012-08-04T16:30:00Z",
#                    "rgba" : [1, 0, 1, 1]
#                }, {
#                    "interval" : "2012-08-04T16:30:00Z/2012-08-04T17:00:00Z",
#                    "rgba" : [0, 1, 1, 1]
#                }]
#            }
#        }
#    }
#}
                
time1 = time.clock()
display2dlist = []

print "*******Reading Solar Results***************"
mthly_res_list = []
mn_list = []
file_list = os.listdir(json_dir)
for f in file_list:
    solar_filepath = os.path.join(json_dir, f)
    json_file = open(solar_filepath, "r")
    mth_solar = json.load(json_file)
    mthly_res_list.append(mth_solar)
    mth_res = []
    for solar in mth_solar:
        plist = solar["solar"]
        plist = [x for x in plist if x != 0]
        mth_res.extend(plist)
        
    json_file.close()
    mn_list.append([min(mth_res), max(mth_res)])

print "*******Reading Roofs***************"
shpatt_list = read_sf_poly(shp_filepath)
shpatt_list = shpatt_list[0:50]

mth_date_list = []
for i in range(13):
    if i ==12:
        mth_date_list.append(datetime.datetime(2020,1,1))
    else:
        mth_date_list.append(datetime.datetime(2019,i+1,1))

fcnt = 0
for mr in mthly_res_list:
    #it should be the number of roof surfaces
#    print len(mr), len(shpatt_list), "it should be the same number"
    mth_date = mth_date_list[fcnt]
    nxt_mth_date = mth_date_list[fcnt+1]
    tdelta = timedelta(hours=1)
    minmax = mn_list[fcnt]
    czml = write2czml(shpatt_list, mr, mth_date, nxt_mth_date, tdelta, minmax)
    
    json_str = json.dumps(czml)
    json_filepath = os.path.join(czml_dir, filename + str(fcnt) + ".czml")
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()
    
    fcnt +=1

time2 = time.clock()
total = (time2-time1)/60.0
print "*******Total Time Taken:", total, "***************"