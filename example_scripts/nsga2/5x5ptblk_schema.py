import os
import pyliburo
from collada import *
#==================================================
#INPUTS
#==================================================
resume = False
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
dae_file = os.path.join(parent_path, "example_files","5x5ptblks", "dae", "5x5ptblks.dae")
base_citygml_file =  os.path.join(parent_path, "example_files","5x5ptblks", "gml", "5x5ptblks.gml")

ngeneration = 3
init_population = 2
mutation_rate = 0.01
crossover_rate  = 0.8 
live_file =  os.path.join(parent_path, "example_files","5x5ptblks", "nsga2_xml", "live.xml")
dead_file =  os.path.join(parent_path, "example_files","5x5ptblks", "nsga2_xml", "dead.xml")
#==================================================
#FUNCTIONS
#==================================================   
def read_collada(dae_filepath):
    buildinglist = []
    luselist = []
    mesh = Collada(dae_file)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    gcnt = 0
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:  
            buildinglist.append([])
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
                        pyliburo.py3dmodel.fetch.is_face_null(occpolygon)
                        if not pyliburo.py3dmodel.fetch.is_face_null(occpolygon):
                            buildinglist[-1].append(occpolygon)
                            gcnt +=1
                  
    #create solid out of the buildings 
    shapelist = []
    for bfaces in buildinglist:
        if bfaces:     
            if len(bfaces) == 1:
                luselist.append(bfaces[0])
            else:
                bsolid = pyliburo.py3dmodel.construct.make_shell_frm_faces(bfaces)[0]
                shapelist.append(bsolid)
            

    shapelist.extend(luselist)
    compound = pyliburo.py3dmodel.construct.make_compound(shapelist)  
    ref_pt = pyliburo.py3dmodel.calculate.face_midpt(luselist[0])
    scaled_shape = pyliburo.py3dmodel.modify.uniform_scale(compound, unit, unit, unit,ref_pt)
    return pyliburo.py3dmodel.fetch.shape2shapetype(scaled_shape)
    
def get_footprint_roof(building_solid):
    occfacelist = pyliburo.py3dmodel.fetch.geom_explorer(building_solid, "face")
    footprint = []
    roof = []
    for occface in occfacelist:
        nrml = pyliburo.py3dmodel.calculate.face_normal(occface)
        if nrml == (0,0,1): 
            roof.append(occface)
        if nrml == (0,0,-1):
            footprint.append(occface)
            
    return footprint[0], roof[0]
                
def daeluse2gmlluse(daeluse, citygml_writer):
    luse_lod = "lod1"
    luse_name = "plot1"
    luse_function = "1010"
    luse_generic_attrib_dict = {}
    gml_srf = pyliburo.gml3dmodel.write_a_gml_srf_member(daeluse)
    luse_geometry_list = [gml_srf]
    citygml_writer.add_landuse(luse_lod, luse_name, luse_geometry_list, function = luse_function, 
                               generic_attrib_dict = luse_generic_attrib_dict)

def daebldglist2gmlbuildings(daebldg_shelllist, citygml_writer):
    bldg_cnt = 0
    for building in daebldg_shelllist:
        bldg_lod = "lod1"
        bldg_name = "building" + str(bldg_cnt)
        bldg_str_abv_grd = "30"
        bfacelist = pyliburo.py3dmodel.fetch.geom_explorer(building, "face")
        footprint, roof = get_footprint_roof(building)
        bldg_geometry_list = pyliburo.gml3dmodel.write_gml_srf_member(bfacelist)
        heightpt1 = pyliburo.py3dmodel.calculate.face_midpt(footprint)
        heightpt2 = pyliburo.py3dmodel.calculate.face_midpt(roof)
        height = pyliburo.py3dmodel.calculate.distance_between_2_pts(heightpt1, heightpt2)
        bldg_height = height
        citygml_writer.add_building(bldg_lod, bldg_name, bldg_geometry_list, 
                                    height = str(bldg_height),
                                    stry_abv_grd = str(bldg_str_abv_grd))
                       
        bldg_cnt +=1
    
def gmlbuilding2buildingsolid(building, read_citygml):
    pypolygonlist = read_citygml.get_pypolygon_list(building)
    bsolid = pyliburo.py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygonlist)
    return bsolid
        
def parameterise_citygml(ref_citygml_file, parameterlist, citygml_resultpath):
    #==================================================
    #PARAMETERISE THE CITYGML FILE
    #==================================================
    #this model has 75 parameters
    #height, position, orientation
    read_citygml = pyliburo.pycitygml.Reader()
    read_citygml.load_filepath(ref_citygml_file)
    buildings = read_citygml.get_buildings()
    landuses = read_citygml.get_landuses()
    lpolygon = read_citygml.get_polygons(landuses[0])[0]
    landuse_pts = read_citygml.polygon_2_pt_list(lpolygon)
    lface = pyliburo.py3dmodel.construct.make_polygon(landuse_pts)
    
    changed_bldglist = []
    bcnt = 0
    for building in buildings:
        bsolid = gmlbuilding2buildingsolid(building, read_citygml)
        #move, rotate and change the height of the building 
        bfaces = pyliburo.py3dmodel.fetch.geom_explorer(bsolid, "face")
        for bface in bfaces:
            fnormal = pyliburo.py3dmodel.calculate.face_normal(bface)
            if fnormal == (0,0,-1):
                #must be the footprint
                #get the midpt
                midpt = pyliburo.py3dmodel.calculate.face_midpt(bface)
                
        #change the building height
        height_parm = parameterlist[bcnt + ((bcnt*2)+0)]
        orig_height = 90.0
        height_ratio = float(height_parm)/orig_height
        scaled_shape = pyliburo.py3dmodel.modify.uniform_scale(bsolid,1,1,height_ratio,midpt)
        #change the positions: there are 4 options, 0 - positive y, 1 - neg y, 2 - positive x, 3 - neg x
        pos_parm = parameterlist[bcnt + ((bcnt*2)+1)]
        if pos_parm == 0:
            moved_shape = scaled_shape
            locpt = midpt
        else:
            if pos_parm == 1:
                dir2mv = (0,1,0)
            if pos_parm == 2:
                dir2mv = (0,-1,0)
            if pos_parm == 3:
                dir2mv = (1,0,0)
            if pos_parm == 4:
                dir2mv = (-1,0,0)
            locpt = pyliburo.py3dmodel.modify.move_pt(midpt,dir2mv, 10)
            moved_shape = pyliburo.py3dmodel.modify.move(midpt, locpt, scaled_shape)
        #change the orientation of the building 
        orient_parm = parameterlist[bcnt + ((bcnt*2)+2)]
        rotat_shape = pyliburo.py3dmodel.modify.rotate(moved_shape, locpt, (0,0,1), orient_parm)
        changed_bldglist.append(pyliburo.py3dmodel.fetch.shape2shapetype(rotat_shape))
        bcnt += 1
                
    #write the design variant as a citygml file 
    citygml_writer = pyliburo.pycitygml.Writer()
    daebldglist2gmlbuildings(changed_bldglist, citygml_writer)
    daeluse2gmlluse(lface, citygml_writer)
    citygml_writer.write(citygml_resultpath)
    return changed_bldglist
    
def eval_density(citygml_filepath):
    read_citygml = pyliburo.pycitygml.Reader()
    read_citygml.load_filepath(citygml_filepath)
    buildings = read_citygml.get_buildings()
    flr2flr_height = 3.0
    luse_area = 136900.0
    flr_area_list = []
    for building in buildings:
        bsolid = gmlbuilding2buildingsolid(building, read_citygml)
        footprint, roof = get_footprint_roof(bsolid)
        footprint_area = pyliburo.py3dmodel.calculate.face_area(footprint)
        bldg_height = read_citygml.get_building_height(building)
        levels = bldg_height/flr2flr_height
        ttl_flr_area = footprint_area*levels
        flr_area_list.append(ttl_flr_area)
        
    luse_flr_area = sum(flr_area_list)
    far = luse_flr_area/luse_area
    return far
    
def eval_daylight(citygml_filepath):
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    xdim = 9
    ydim = 9
    weatherfilepath = os.path.join(parent_path, "example_files","weatherfile", "SGP_Singapore.486980_IWEC.epw")
    '''
    illum threshold (lux)
    '''
    illum_threshold = 10000
    avg_dfavi, dfavi_percent, dfai, topo_list, illum_ress = evaluations.dfavi(illum_threshold,weatherfilepath,xdim,ydim)    
    
    return dfai
    
def generate_gene_dict_list():
    '''
    4 types of genes 
    float_range
    float_choice
    int_range
    int_choice
    '''
    dict_list = []
    for pcnt in range(75):
        gene_dict = {}
        pcnt3 = pcnt%3
        if pcnt3 == 0:
            #height parm
            gene_dict["type"] = "int_range"
            gene_dict["range"] = (30,91,3)
            dict_list.append(gene_dict)
        if pcnt3 == 1:
            #pos parm
            gene_dict["type"] = "int_choice"
            gene_dict["range"] = (0,1,2,3,4)
            dict_list.append(gene_dict)
        if pcnt3 == 2:
            #orientation parm
            gene_dict["type"] = "int_range"
            gene_dict["range"] = (0,360,10)
            dict_list.append(gene_dict)
            
    return dict_list
    
def generate_score_dict_list():
    far_score = {"name":"far", "minmax": "max"}
    pvfai_score = {"name":"pvfai", "minmax": "max"}
    dict_list = [far_score, pvfai_score]
    return dict_list

#==================================================
#CONVERT THE COLLADA FILE TO CITYGML
#==================================================
#read the collada file and organise the geometry into buildings and plots
buildinglist = []
luselist = []
collada_compound = read_collada(dae_file)

print "WRITING CITYGML FILE ... ..."
citygml_writer = pyliburo.pycitygml.Writer()     
cface_list = pyliburo.py3dmodel.fetch.geom_explorer(collada_compound, "face") #the last face is the plot
#convert the collada plot to citygml plot
daeluse2gmlluse(cface_list[550], citygml_writer)
#convert the collada buildings to citygml buidlings
cshell_list = pyliburo.py3dmodel.fetch.geom_explorer(collada_compound, "shell") 

daebldglist2gmlbuildings(cshell_list, citygml_writer)
citygml_writer.write(base_citygml_file)

#==================================================
#OPTIMISE
#==================================================
gene_dict_list = generate_gene_dict_list()
score_dict_list = generate_score_dict_list()

if resume == False:
    population = pyliburo.runopt.initialise_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
if resume == True:
    population = pyliburo.runopt.resume_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
    
for gencnt in range(ngeneration):
    indlist = population.individuals
    for ind in indlist:
        #==================================================
        #GENERATE DESIGN VARIANT
        #=================================================
        ind_id = ind.id
        dv_citygml ="F:\\kianwee_work\\smart\\case_studies\\5x5ptblks\\design_variants\\" + str(ind_id) + ".gml"
        parmlist = ind.genotype.values
        design_variant = parameterise_citygml(base_citygml_file, parmlist, dv_citygml)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        far = eval_density(dv_citygml)
        dfai = eval_daylight(dv_citygml)
        print 'FAR', far, "DFAI", dfai
        ind.set_score(0,far)
        ind.set_score(1,dfai)
        
    #==================================================
    #NSGA FEEDBACK 
    #=================================================
    pyliburo.runopt.feedback_nsga2(population)
    
print "DONE"
