from py4design import py3dmodel, shp2citygml
import shapefile
#the centroid file must be a shpfile with a single centroid
shpfile_centroid = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_point1\\princeton_point10by10km.shp"
shpfile_res = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_bdry2\\princeton_bdry5by5km.shp"

rectangle = True #if false circle is drawn
xdim = 5000 #metres
ydim = 5000 #metres
radius = 50 #metres
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
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
        
        w.poly([pyptlist2d])
        w.record(cnt)
        cnt+=1
    w.close()
#===========================================================================================
#FUNCTIONS
#===========================================================================================
sf = shapefile.Reader(shpfile_centroid)
rec=sf.shapeRecords()[0]
pypt2d = shp2citygml.get_geometry(rec)[0]
pypt3d = (pypt2d[0], pypt2d[1], 0)
#draw cirle or rec with the centroid
if rectangle == True:
    bdry = py3dmodel.construct.make_rectangle(xdim, ydim)
    bdry = py3dmodel.modify.move([0,0,0], pypt3d, bdry)
    bdry = py3dmodel.fetch.topo2topotype(bdry)
else:
    bdry = py3dmodel.construct.make_polygon_circle(pypt3d, [0,0,1], radius)
    
write_poly_shpfile([bdry], shpfile_res)