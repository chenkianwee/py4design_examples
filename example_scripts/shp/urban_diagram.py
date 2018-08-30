import time
import collada
from collada import polylist, triangleset
from py4design import py3dmodel, shp2citygml, massing2citygml, analysisrulepalette, templaterulepalette, citygml2eval
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
#constraints
bdry_shp_file = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\shp\\site_bdry\\site_bdry.shp"
no_of_unit = 7000
#site_area
edu_sa = 18000
park_sa = 15000
health_sa = 5000

#gfa
commercial_gfa = 7000

#parameters
bldg_footprint = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\brief\\dae\\typology1.dae"
unit_per_flr = 8
nparks = 1
nedu = 1
nhealth = 1
nplots = 6

#default settings
flr2flr_height = 3
offset_factor = 5
plot_xdim = 30
plot_ydim = 30

#results
generated_dae = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\result\\dae\\gen.dae"
citygml_filepath = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\result\\gml\\gen.gml"
solar_dae = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\result\\dae\\solar.dae"
#===========================================================================================
#GET THE SITE BOUNDARY
#===========================================================================================
time1 = time.clock()
display_2dlist = []
colour_list = []

sf = shapefile.Reader(bdry_shp_file)
shapeRecs=sf.shapeRecords()

grid_list = []
pop_d_list = []
print "GRID THE PLANNING AREAS ... ..."
for rec in shapeRecs:
    poly_attribs=rec.record
    pop = poly_attribs[2]
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        for occface in occface_list:
            occface = py3dmodel.construct.make_offset(occface, -10)
            larea = py3dmodel.calculate.face_area(occface)
            grids = py3dmodel.construct.grid_face(occface, plot_xdim, plot_ydim)
            ngrid = len(grids)
            grid_list.extend(grids)
        
#===========================================================================================
#READ THE BLDG FOOTPRINT COLLADA
#===========================================================================================
print "READ FOOTPRINT COLLADA ... ..."
bldg_footprint_occface_list = []
mesh = collada.Collada(bldg_footprint)
unit = mesh.assetInfo.unitmeter or 1
geoms = mesh.scene.objects('geometry')
geoms = list(geoms)
for geom in geoms:   
    prim2dlist = list(geom.primitives())
    for primlist in prim2dlist:     
        if primlist:
            for prim in primlist:
                if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                    pyptlist = prim.vertices.tolist()
                    occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                    is_face_null = py3dmodel.fetch.is_face_null(occpolygon)
                    if not is_face_null:
                        bldg_footprint_occface_list.append(occpolygon)

# generate buildings 
bldg_proto_footprint = bldg_footprint_occface_list[0]
bldg_proto_midpt = py3dmodel.calculate.face_midpt(bldg_proto_footprint)
bldg_proto_footprint = py3dmodel.modify.scale(bldg_proto_footprint, unit, bldg_proto_midpt)
footprint_area = py3dmodel.calculate.face_area(bldg_proto_footprint)
bldg_footprint_list = []
b_midpt_list = []

#===========================================================================================
#READ THE BLDG FOOTPRINT COLLADA
#===========================================================================================
print "MIDPT ... ..."
ideal_plot_area = plot_xdim*plot_ydim
area_threshold = ideal_plot_area*0.3
for grid in grid_list:
    garea = py3dmodel.calculate.face_area(grid)
    if garea > area_threshold:
        pyptlist = py3dmodel.fetch.points_frm_occface(grid)
        chull = py3dmodel.construct.convex_hull2d(pyptlist)
        offset_val = min([plot_xdim,plot_ydim])/offset_factor
        oface = py3dmodel.construct.make_offset(chull, offset_val*-1)
        cpyptlist = py3dmodel.fetch.points_frm_occface(oface)
        midpt = py3dmodel.calculate.points_mean(cpyptlist)
        bldg_footprint = py3dmodel.modify.move(bldg_proto_midpt, midpt, bldg_proto_footprint)
        b_midpt_list.append(midpt)
        bldg_footprint = py3dmodel.fetch.topo2topotype(bldg_footprint)
        bldg_footprint_list.append(bldg_footprint)

n_bldg_footprint = len(bldg_footprint_list)
unit_each = no_of_unit/n_bldg_footprint
storey_each = unit_each/unit_per_flr
print storey_each

bldg_list = []

bcnt = 0
for bldg in bldg_footprint_list:
    bldg_midpt = b_midpt_list[bcnt]
    bldg_footprint_ext = py3dmodel.construct.extrude(bldg, (0,0,1), flr2flr_height*storey_each)
    bldg_list.append(bldg_footprint_ext)
#    for i in range(storey_each):
#        loc_pt = py3dmodel.modify.move_pt(bldg_midpt, (0,0,1), 3*i)
#        m_bldg_storey = py3dmodel.modify.move(bldg_midpt, loc_pt, bldg_footprint_ext)
    bcnt +=1
    
'''
py3dmodel.export_collada.write_2_collada(generated_dae, occface_list = bldg_list)
#first set up the massing2citygml object
print "#==================================="
print "READING COLLADA...", generated_dae
print "#==================================="
massing_2_citygml = massing2citygml.Massing2Citygml()
massing_2_citygml.read_collada(generated_dae)

#first set up the analysis rule necessary for the template rules
is_shell_closed = analysisrulepalette.IsShellClosed()

#then set up the template rules and append it into the massing2citygml obj
id_bldgs = templaterulepalette.IdentifyBuildingMassings()
id_bldgs.add_analysis_rule(is_shell_closed, True)
massing_2_citygml.add_template_rule(id_bldgs)
print "EXECUTE ANALYSIS"
massing_2_citygml.execute_analysis_rule()
print "#==================================="
print "WRITING CITYGML ... ...", citygml_filepath
print "#==================================="
massing_2_citygml.execute_template_rule(citygml_filepath)

weatherfilepath = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\brief\\epw\\SGP_Singapore.486980_IWEC.epw"
    
evaluations = citygml2eval.Evals(citygml_filepath)
xdim = 9
ydim = 9

lower_irrad_threshold = 245#kw/m2
upper_irrad_threshold = 355#kw/m2
illum_threshold = 10000#lux ~~254kw/m2
roof_irrad_threshold = 1280 #kwh/m2
facade_irrad_threshold = 512 #kwh/m2

print "#==================================="
print "EVALUATING MODEL ... ...", citygml_filepath
print "#==================================="

res_dict  = evaluations.nshffai(upper_irrad_threshold,weatherfilepath,xdim,ydim)
print "NON SOLAR HEATED FACADE TO FLOOR AREA INDEX:", res_dict["afi"]
print "NON SOLAR HEATED FACADE AREA INDEX:", res_dict["ai"]

d_str = "NSHFFAI: " + str(res_dict["afi"]) + "\n" + "NSHFAI: " + str(res_dict["ai"])
py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                               "kWh/m2", solar_dae, description_str = d_str, 
                                               minval = 0, maxval = 758.17)
    
'''
py3dmodel.utility.visualise([bldg_list, grid_list])
