import time
import shapefile

from py4design import py3dmodel, urbangeom
#===========================================================================================
#INPUTS
#===========================================================================================
bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bldg.brep"
shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_roofs\\main_campus_roofs.shp"

#===========================================================================================
#FUNCTIONS
#===========================================================================================
def write_poly_shpfile(occface_list, shp_filepath, attname_list, att_list):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('uid','N',10)
    for attname in attname_list:
        print attname
        w.field(attname,'N', decimal=2)
         
    cnt=0
    for occface in occface_list:
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        atts = att_list[cnt]
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.record(cnt, atts[0], atts[1], atts[2])
            w.poly(poly_shp_list)
                    
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(occface)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if is_anticlockwise:
                pyptlist.reverse()
            pyptlist2d = []
            for pypt in pyptlist:
                x = pypt[0]
                y = pypt[1]
                pypt2d = [x,y]
                pyptlist2d.append(pypt2d)
                
            w.record(cnt, atts[0], atts[1], atts[2])
            w.poly([pyptlist2d])
            
        cnt+=1
    w.close()
    
#===========================================================================================
#MAIN
#===========================================================================================
time1 = time.clock()
display2dlist = []
print "*******Reading Buildings***************"
bldg_cmpd = py3dmodel.utility.read_brep(bldg_filepath)
bldg_solids = py3dmodel.fetch.topo_explorer(bldg_cmpd, "solid")

roof_list = []
attname_list = ["zmin", "zmax", "height"]
att_list = []
print "*******Separating Building Surfaces***************"
for bldg_solid in bldg_solids:
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_solid)
    facades, roofs, footprints = urbangeom.identify_building_surfaces(bldg_solid)
    height = zmax-zmin
    atts = [zmin, zmax, height]
    att_list.append(atts)
    roof_list.extend(roofs)

print "*******Writing to ShpFile***************"
write_poly_shpfile(roof_list, shp_filepath, attname_list, att_list)