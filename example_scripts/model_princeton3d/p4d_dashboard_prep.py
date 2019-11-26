import os
import sys
import json
from dateutil.parser import parse
from dateutil import tz

import numpy as np
from py4design import py3dmodel, urbangeom
import PyQt5
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree

import p4d_function as p4d_func

class Dashboard(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.layers = dict(name = 'Layers', type='group', expanded = True, title = "Step 1: Choose Which Layers to View", 
                           children =   [dict(name='Static Layer', type = 'group', title = "Static Layers",
                                              children = [dict(name = 'Terrain', type = 'bool', value=True),
                                                          dict(name = 'Buildings', type = 'bool', value=True),
                                                          dict(name = 'Trees', type = 'bool', value=True),
                                                          dict(name = 'Roads', type = 'bool', value=True)
                                                         ]
                                              ),    
                                        dict(name='Dynamic Layer', type = 'group', title = "Dynamic Layers",
                                              children = [dict(name = 'Hourly Grd Solar Irradiation', type = 'bool', value=True),
                                                          dict(name = 'Hourly Cart Travel Behaviour', type = 'bool', value=True)
                                                         ]
                                              ),
                                        dict(name='Change Layers Visibility', type = 'action', title = "Change!!!")
                                        ]
                            )
    
        self.load_result = dict(name='Load Result', type='group', expanded = True, title = "Step 2: Specify a Date & Time and Mnaually Explore the Dynamic Data",
                                    children=[dict(name='Date of Interest', type = 'group', title = "Specify Date of Interest", 
                                                   children = [dict(name='Year:', type= 'list', values= [2019], value=2019),
                                                               dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                               dict(name='Day:', type= 'int', limits = (1,31), value = 1),
                                                               dict(name='Hour:', type= 'int', limits = (0,23), value = 12)
                                                               ]
                                                   ),
                                            
                                              dict(name='Data Loaded', type = 'str', title = "Data Loaded", readonly = True),
                                              dict(name='Load Data', type = 'action', title = "Load!!!"),
                                              dict(name = 'Forward', type = 'action', title = 'Step Forward!!!'),
                                              dict(name = 'Backward', type = 'action', title = 'Step Backward!!!')
                                              ]
                                    )
    
        self.date_range = dict(name='Date Range', type='group', expanded = True, title = "Step 3: Specify a Date Range and Automatically Explore the Dynamic Data",
                              children=[dict(name='Start Date', type = 'group', expanded = False, title = "Specify Start Date", 
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 15),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 8)
                                                         ]
                                                                       
                                             ),
                                        dict(name='End Date', type = 'group', expanded = False, title = "Specify End Date",
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 15),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 18)
                                                         ]
                                                         
                                             ),
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Load Data Range', type = 'action', title = "Load!!!"),
                                        dict(name = 'Play Data', type = 'action', title = 'Play!!!'),
                                        ]
                                )
        
        
        
        self.params = Parameter.create(name='ParmX', type='group', children=[self.layers,
                                                                             self.load_result,
                                                                             self.date_range
                                                                             ])
        
        self.tree.setParameters(self.params, showTop=False)
        
        #generate falsecolour bar
        self.min_val = 133.0
        self.max_val = 914.0
        
        self.falsecolour = p4d_func.gen_falsecolour_bar(self.min_val, self.max_val)
        
        self.env_parm = dict(name='Environment', type='group', expanded = True, title = "The Environment (C)",
                                children=[
                                          dict(name='Air Temp', type = 'str', title = "Air Temp", readonly = True),
                                          dict(name='Dewpoint', type = 'str', title = "Dewpoint", readonly = True),
                                          dict(name='Globe Temp', type = 'str', title = "Globe Temp", readonly = True)
                                          ]
                                )
        self.params2 = Parameter.create(name = "Parmx2", type = "group", children = [self.falsecolour
                                                                                     ])
        self.tree2.setParameters(self.params2, showTop=False)
        
        self.params.param('Date Range').param("Load Data Range").sigActivated.connect(self.load_data_range)
        self.params.param('Load Result').param("Load Data").sigActivated.connect(self.load_data)
        self.params.param('Date Range').param("Play Data").sigActivated.connect(self.play_data)
        self.params.param('Load Result').param("Forward").sigActivated.connect(self.forward)
        self.params.param('Load Result').param("Backward").sigActivated.connect(self.backward)
        self.params.param('Layers').param("Change Layers Visibility").sigActivated.connect(self.change_visibility)
        
        self.data = None
    
    def setupGUI(self):
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        
        self.tree = ParameterTree(showHeader=False)
        self.splitter.addWidget(self.tree)

        
        self.splitter2 = QtGui.QSplitter()
        self.splitter2.setOrientation(QtCore.Qt.Horizontal)
        
        self.tree2 = ParameterTree(showHeader=False)
        self.splitter2.addWidget(self.splitter)
        self.splitter2.addWidget(self.tree2)
        self.splitter2.setStretchFactor(0, 3)
        
        self.layout.addWidget(self.splitter2)
        
        self.view3d = gl.GLViewWidget()
        self.splitter.addWidget(self.view3d)
        
        #========================================================================
        #load the 3d terrain model
        #========================================================================
        terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\terrain.brep"
        terrain_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\terrains.json"
        
        terrain_cmpd = py3dmodel.utility.read_brep(terrain_filepath)
        midpt = py3dmodel.calculate.get_centre_bbox(terrain_cmpd)
        #terrain_shells = py3dmodel.fetch.topo_explorer(terrain_cmpd, "shell")
        #p4d_func.topos2meshes_json(terrain_shells, terrain_mesh_json, face_colours2d = None)
        
        terrains_mesh_list = p4d_func.read_meshes_json(terrain_mesh_json, shader = "shaded",  gloptions = "additive")
        
        for t in terrains_mesh_list:
            t.setColor([1.0,1.0,1.0,1.0])
            
        self.terrain_meshes = terrains_mesh_list
        #========================================================================
        #laod the 3d buildings
        #========================================================================
        facade_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\facade.json"
        roof_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\roof.json"
        roof_edge_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\roof_edge.json"
#        bldg_edge_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\bldg_edge.json"
#        bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bldg.brep"
#        bldg_cmpd = py3dmodel.utility.read_brep(bldg_filepath)
#        bldg_solids = py3dmodel.fetch.topo_explorer(bldg_cmpd, "shell")
#        
#        facade_list = []
#        roof_list = []
#        floor_list = []
#        new_solids = []
#        for solid in bldg_solids:
#            fixed_shell = py3dmodel.modify.fix_shell_orientation(solid)
#            new_solid = py3dmodel.construct.make_solid(fixed_shell)
#            new_solid2 = py3dmodel.modify.fix_close_solid(new_solid)
#            facades, roofs, floors = urbangeom.identify_building_surfaces(new_solid2)
#            facade_list.extend(facades)
#            roof_list.extend(roofs)
#            floor_list.extend(floors)
#            new_solids.append(new_solid2)
#            
#        bldg_cmpd  = py3dmodel.construct.make_compound(new_solids)
#        bface_list = py3dmodel.fetch.topo_explorer(bldg_cmpd, "face")
#        
#        floor_tri = p4d_func.triangulate_faces(floor_list)
#        facade_tri = p4d_func.triangulate_faces(facade_list)
#        roof_tri = p4d_func.triangulate_faces(roof_list)
#        
#        p4d_func.tri_faces2mesh_json(floor_tri, flr_mesh_json)
#        p4d_func.tri_faces2mesh_json(facade_tri, facade_mesh_json)
#        p4d_func.tri_faces2mesh_json(roof_tri, roof_mesh_json)
        
        roof_mesh_list = p4d_func.read_meshes_json(roof_mesh_json, shader = "balloon", gloptions = "additive", draw_edges = False)
        roof_mesh_list[0].setColor([0.5,0.5,0.5,1])
        facade_mesh_list = p4d_func.read_meshes_json(facade_mesh_json, shader = "balloon", gloptions = "additive", draw_edges = False)
#        floor_mesh_list = p4d_func.read_meshes_json(flr_mesh_json, shader = "shaded", gloptions = "translucent", draw_edges = False)
#        tri_face_list = []
#        for bface in bface_list:
#            tri_faces = py3dmodel.construct.simple_mesh(bface)
#            tri_face_list.extend(tri_faces)
        
#        p4d_func.topos2meshes_json([bldg_cmpd], bldg_mesh_json, face_colours = None)
#        p4d_func.draw_boundary_edge_json(roof_list, roof_edge_json)
        line_list = p4d_func.read_edges_json(roof_edge_json, line_colour = (0,0,0,1), width = 1, antialias=True, mode="lines")
        
        self.roof_meshes = roof_mesh_list
        self.facade_meshes = facade_mesh_list
        self.bldg_lines = line_list
        #========================================================================
        #load the trees 
        #========================================================================
#        tree_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\tree.brep"
        tree_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\trees.json"
#        tree_cmpd = py3dmodel.utility.read_brep(tree_filepath)
#        tree_faces = py3dmodel.fetch.topo_explorer(tree_cmpd, "face")
        
#        tree_cmpd = py3dmodel.construct.make_compound(tree_faces)
#        p4d_func.tri_faces2mesh_json(tree_faces, tree_mesh_json)
        tree_meshes = p4d_func.read_meshes_json(tree_mesh_json, shader = "shaded", gloptions = "additive")
        tree_meshes[0].setColor([0,0.5,0,1])
        
        self.tree_meshes = tree_meshes
        #========================================================================
        #load roads 
        #========================================================================
#        road_brep_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\road.brep"
        road_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\roads.json"
#        road_cmpd = py3dmodel.utility.read_brep(road_brep_filepath)
#        p4d_func.topos2meshes_json([road_cmpd], road_mesh_json)
#        p4d_func.tri_faces2mesh_json(road_faces , road_mesh_json)
        road_meshes = p4d_func.read_meshes_json(road_mesh_json)
        for mesh in road_meshes:
            mesh.setColor([0.5,0.5,0.5,1])
        
        self.road_meshes = road_meshes
        #========================================================================
        #load falsecolour results 
        #========================================================================
        #get all the geometries 
        json_mesh_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\solar_grd.json"
#        json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\overall\\grd_solar_mth0.json"
#        f = open(json_filepath, "r")
#        json_data = json.load(f)
#        rec = py3dmodel.construct.make_rectangle(5,5)
#        minval = 133.0
#        maxval = 914.0
#        
#        tri_face_list = []
#        face_colours = []
#        for d in json_data:
#            pypt = d["point"]
#            solar_vals = d["solar"]
#            solar_val = solar_vals[12]
#            mrec = py3dmodel.modify.move([0,0,0], pypt, rec)
#            tri_faces = py3dmodel.construct.simple_mesh(mrec)
#            
#            tri_face_list.extend(tri_faces)
#            colour = py3dmodel.utility.pseudocolor(solar_val, minval, maxval)
#            for _ in range(len(tri_faces)):
#                face_colours.append([colour[0], colour[1], colour[2], 1])
#                
#        p4d_func.tri_faces2mesh_json(tri_face_list, json_mesh_filepath, face_colours = face_colours)            
        
        falsecolour_mesh_list = p4d_func.read_meshes_json(json_mesh_filepath, shader = "balloon", gloptions = "translucent")
        self.colour_meshes = falsecolour_mesh_list
        #========================================================================
        #load extrusion results 
        #========================================================================
        path_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\path.json"
        extrude_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\extrude.json"
        extline_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\extrude_lines.json"
        
#        edge_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\path.brep"
#        edge_cmpd = py3dmodel.utility.read_brep(edge_brepfilepath)
#        edges = py3dmodel.fetch.topo_explorer(edge_cmpd, "edge")
#        p4d_func.draw_edge_json(edges, path_json_filepath)
#        
#        ext_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\ext.brep"
#        extrude_cmpd = py3dmodel.utility.read_brep(ext_brepfilepath)
#        ext_faces = py3dmodel.fetch.topo_explorer(extrude_cmpd, "face")
#        ext_tri_faces = p4d_func.triangulate_faces(ext_faces)
#        p4d_func.tri_faces2mesh_json(ext_tri_faces, extrude_json_filepath)
#        p4d_func.draw_boundary_edge_json(ext_faces, extline_json_filepath)
        
        path_lines = p4d_func.read_edges_json(path_json_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
        extrude_meshes = p4d_func.read_meshes_json(extrude_json_filepath, shader = "shaded", gloptions = "additive")
        extrude_meshes[0].setColor([1,0,0,1])
        extrude_lines = p4d_func.read_edges_json(extline_json_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
        
        self.path_lines = path_lines
        self.extrude_meshes = extrude_meshes
        self.extrude_lines = extrude_lines
        #========================================================================
        #viz test box
        #========================================================================
#        box_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\box.json"
#    
#        box = py3dmodel.construct.make_box(1000,1000,100)
#        box = py3dmodel.modify.move([0,0,0], midpt, box)
#        p4d_func.topos2meshes_json([box], box_json)
#        boxes = p4d_func.read_meshes_json(box_json)
#        face_colours = [[1,0,0,1], [1,0,0,1], [1,1,0,1], [1,1,0,1],
#                        [0,1,0,1], [0,1,0,1], [0,0,1,1], [0,0,1,1],
#                        [0,1,0,1], [0,1,0,1], [1,0,0,1], [1,0,0,1]]
#        
#        p4d_func.edit_mesh_face_colours(boxes[0], face_colours)
#        p4d_func.viz_graphic_items(boxes, self.view3d)
        #========================================================================
        #determine the back and front of each geometry 
        #========================================================================
        p4d_func.viz_graphic_items(terrains_mesh_list, self.view3d)
        
        p4d_func.viz_graphic_items(road_meshes , self.view3d)
        
        p4d_func.viz_graphic_items(falsecolour_mesh_list, self.view3d)
        
        p4d_func.viz_graphic_items(tree_meshes, self.view3d)
        
        p4d_func.viz_graphic_items(facade_mesh_list, self.view3d)
        p4d_func.viz_graphic_items(line_list, self.view3d)
        p4d_func.viz_graphic_items(roof_mesh_list, self.view3d)
        
        p4d_func.viz_graphic_items(path_lines, self.view3d)
        p4d_func.viz_graphic_items(extrude_meshes, self.view3d)
        p4d_func.viz_graphic_items(extrude_lines, self.view3d)
        
        #========================================================================
        #configure the camera to orbit around the terrain
        #========================================================================
        self.view3d.opts['center'] = PyQt5.QtGui.QVector3D(midpt[0], midpt[1], midpt[2])
        self.view3d.opts['distance'] = 5000
#        self.view3d.setBackgroundColor([125,125,125,125])
        
    def change_visibility(self):
        #get all the settings for static layers
        terrain_bool = self.params.param('Layers').param('Static Layer').param("Terrain").value()
        building_bool = self.params.param('Layers').param('Static Layer').param("Buildings").value()
        tree_bool = self.params.param('Layers').param('Static Layer').param("Trees").value()
        road_bool = self.params.param('Layers').param('Static Layer').param("Roads").value()
        
        #get all the settings for dynamic layers
        hrly_solar_bool = self.params.param('Layers').param('Dynamic Layer').param("Hourly Grd Solar Irradiation").value()
        hrly_cart_bool = self.params.param('Layers').param('Dynamic Layer').param("Hourly Cart Travel Behaviour").value()
        
        #get all the meshes
        terrains = self.terrain_meshes
        
        trees = self.tree_meshes
        roads = self.road_meshes
        
        roofs = self.roof_meshes 
        facades = self.facade_meshes
        bldg_outlines = self.bldg_lines
        
        falsecolours = self.colour_meshes
        
        path_lines = self.path_lines
        extrude_meshes = self.extrude_meshes
        ext_lines = self.extrude_lines
        
        #set the visibility
        p4d_func.set_graphic_items_visibility(terrains, terrain_bool)
        
        p4d_func.set_graphic_items_visibility(roofs, building_bool)
        p4d_func.set_graphic_items_visibility(facades, building_bool)
        p4d_func.set_graphic_items_visibility(bldg_outlines, building_bool)
        
        p4d_func.set_graphic_items_visibility(trees, tree_bool)
        p4d_func.set_graphic_items_visibility(roads, road_bool)
        
        p4d_func.set_graphic_items_visibility(falsecolours, hrly_solar_bool)
        
        p4d_func.set_graphic_items_visibility(path_lines, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(extrude_meshes, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(ext_lines, hrly_cart_bool)
        
    def load_data(self):
        #get the specified date
        s_year = self.params.param('Load Result').param('Date of Interest').param("Year:").value()
        s_mth = self.params.param('Load Result').param('Date of Interest').param("Month:").value()
        s_day = self.params.param('Load Result').param('Date of Interest').param("Day:").value()
        s_hour = self.params.param('Load Result').param('Date of Interest').param("Hour:").value()
        s_min = 0
        s_sec = 0
        str_sp_date = str(s_year) + "-" + str(s_mth) + "-" + str(s_day) + "-" +\
                        str(s_hour) + ":" + str(s_min) + ":" + str(s_sec)
                                
        date = parse(str_sp_date)
        self.current_date = date
        str_date = date.strftime("%Y-%m-%d %H:%M:%S")
        self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        date_index = p4d_func.date2index(date)
        
        #retrieve the data from the date index
        
        
    def forward(self):
        pass
    
    def backward(self):
        pass
    
    def load_data_range(self):
        pass
    
    def play_data(self):
        import subprocess
        str_start_date = self.str_start_date
        str_end_date = self.str_end_date
        current_path = os.path.dirname(__file__)
        ani_file = os.path.join(current_path, "coldtube_animation.py")
        #cmd = "python " + ani_file + " " + str_start_date + " " + str_end_date
        subprocess.call(["python", ani_file, str_start_date, str_end_date])
            
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = Dashboard()
    win.setWindowTitle("Dashboard 3D")
    win.show()
    win.showMaximized()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()