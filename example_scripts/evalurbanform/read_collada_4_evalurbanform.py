from pyliburo import py3dmodel
import collada
from collada import polylist, triangleset, lineset

def read_collada(dae_filepath):
    closegeomlist = []
    opengeomlist_srf = []
    opengeomlist_shell = []
    edgelist = []

    mesh = collada.Collada(dae_filepath)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    gcnt = 0
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:  
            faces = []
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                        if not py3dmodel.fetch.is_face_null(occpolygon):
                            faces.append(occpolygon)
                            gcnt +=1
                    elif type(prim) == lineset.Line:
                        pyptlist = prim.vertices.tolist()
                        occedge = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                        edgelist.append(occedge)
                        gcnt +=1
                        
                if faces:
                    #remove all the duplicated faces
                    non_dup_f = py3dmodel.modify.rmv_duplicated_faces(faces)
                    #sew them together to form shells 
                    shell_list = py3dmodel.construct.sew_faces(non_dup_f)
                    nshells = len(shell_list)
                    if nshells == 1:
                        #a single mesh shld only have a single shell nothing more
                        shell = shell_list[0]
                        simplified_geom = simplify_shell(shell)
                        shapetype = py3dmodel.fetch.get_topotype(simplified_geom)
                        if  shapetype== py3dmodel.fetch.get_topotype("shell"):#shell
                            is_shell_close = py3dmodel.calculate.is_shell_closed(simplified_geom)
                            if is_shell_close:
                                solid = py3dmodel.construct.make_solid(simplified_geom)
                                fix_solid = py3dmodel.modify.fix_close_solid(solid)
                                closegeomlist.append(fix_solid)
                            else:
                                opengeomlist_shell.append(simplified_geom)
                        if shapetype == 4: #face
                            opengeomlist_srf.append(simplified_geom)
                            
    
    #find the midpt of all the geometry
    compound_list = closegeomlist + opengeomlist_shell + opengeomlist_srf + edgelist
    compound = py3dmodel.construct.make_compound(compound_list)  
    ref_pt = py3dmodel.calculate.get_centre_bbox(compound)
    ref_pt = (ref_pt[0],ref_pt[1],0)
    #make sure no duplicate edges
    edgelist2 = py3dmodel.modify.rmv_duplicated_edges(edgelist)
    #scale the compounds
    compound1 = py3dmodel.construct.make_compound(closegeomlist)  
    compound2 = py3dmodel.construct.make_compound(opengeomlist_shell)  
    compound3 = py3dmodel.construct.make_compound(opengeomlist_srf)  
    compound4 = py3dmodel.construct.make_compound(edgelist2) 
    
    scaled_shape1 = py3dmodel.modify.uniform_scale(compound1, unit, unit, unit,ref_pt)
    scaled_shape2 = py3dmodel.modify.uniform_scale(compound2, unit, unit, unit,ref_pt)
    scaled_shape3 = py3dmodel.modify.uniform_scale(compound3, unit, unit, unit,ref_pt)
    scaled_shape4 = py3dmodel.modify.uniform_scale(compound4, unit, unit, unit,ref_pt)
    
    scaled_compound1 = py3dmodel.fetch.topo2topotype(scaled_shape1)
    scaled_compound2 = py3dmodel.fetch.topo2topotype(scaled_shape2)
    scaled_compound3 = py3dmodel.fetch.topo2topotype(scaled_shape3)
    scaled_compound4 = py3dmodel.fetch.topo2topotype(scaled_shape4)
    
    recon_faces1, recon_edges1 = redraw_occfaces(scaled_compound1)
    recon_faces2, recon_edges2 = redraw_occfaces(scaled_compound2)
    recon_faces3, recon_edges3 = redraw_occfaces(scaled_compound3)
    recon_faces4, recon_edges4 = redraw_occfaces(scaled_compound4)
    
    close_shell_list = py3dmodel.construct.sew_faces(recon_faces1)
    solid_list = []
    for cs in close_shell_list:
        solid = py3dmodel.construct.make_solid(cs)
        fixed_solid = py3dmodel.modify.fix_close_solid(solid)
        solid_list.append(fixed_solid)
    
    if recon_faces2:
        oshell_list = py3dmodel.construct.sew_faces(recon_faces2)
    else:
        oshell_list = []

    return solid_list, oshell_list, recon_faces3, recon_edges4

def redraw_occfaces(occcompound):
    #redraw the surfaces so the domain are right
    #TODO: fix the scaling 
    faces = py3dmodel.fetch.topo_explorer(occcompound, "face")
    recon_faces = []
    for face in faces:
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        recon_face = py3dmodel.construct.make_polygon(pyptlist)
        recon_faces.append(recon_face)
        
    edges = py3dmodel.fetch.topo_explorer(occcompound, "edge")
    recon_edges = []
    for edge in edges:
        epyptlist = py3dmodel.fetch.points_frm_edge(edge)
        recon_edges.append(py3dmodel.construct.make_edge(epyptlist[0], epyptlist[1]))
        
    return recon_faces, recon_edges
    
def simplify_shell(occshell):
    fshell = py3dmodel.modify.fix_shell_orientation(occshell)
    #get all the faces from the shell and arrange them according to their normals
    sfaces = py3dmodel.fetch.topo_explorer(fshell,"face")
    nf_dict = py3dmodel.calculate.grp_faces_acc2normals(sfaces)
    merged_fullfacelist = []
    #merge all the faces thats share edges into 1 face
    for snfaces in nf_dict.values():
        merged_facelist = py3dmodel.construct.merge_faces(snfaces)
        merged_fullfacelist.extend(merged_facelist)
        
    if len(merged_fullfacelist) >1:
        simpleshell = py3dmodel.construct.sew_faces(merged_fullfacelist)
        fshell2 = py3dmodel.modify.fix_shell_orientation(simpleshell[0])
        return fshell2
    else:
        #if there is only one face it means its an open shell
        return merged_fullfacelist[0]
