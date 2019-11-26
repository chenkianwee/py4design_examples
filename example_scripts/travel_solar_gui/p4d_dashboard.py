import os
import sys
from dateutil.parser import parse
from datetime import timedelta

import PyQt5
from py4design import py3dmodel
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
                                                          dict(name = 'Roads', type = 'bool', value=True)]
                                              ),  
                                        dict(name='Falsecolour Layer', type = 'group', title = "Falsecolour Layers",
                                              children = [dict(name = 'Hourly Grd Solar Irradiation', type = 'bool', value=True)]
                                              ),
                                        dict(name='Extrusion Layer', type = 'group', title = "Extrusion Layers",
                                              children = [dict(name = 'Hourly Cart Travel Behaviour', type = 'bool', value=True)]                                                       
                                              ),
                                        dict(name='Change Layers Visibility', type = 'action', title = "Change!!!")]
                            )
    
        self.load_result = dict(name='Load Result', type='group', expanded = True, title = "Step 2: Specify a Date & Time and Manually Explore the Dynamic Data",
                                    children=[dict(name='Date of Interest', type = 'group', title = "Specify Date of Interest", 
                                                   children = [dict(name='Year:', type= 'list', values= [2019], value=2019),
                                                               dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                               dict(name='Day:', type= 'int', limits = (1,31), value = 1),
                                                               dict(name='Hour:', type= 'int', limits = (0,23), value = 0)]),                                            
                                              dict(name='Data Loaded', type = 'str', title = "Data Loaded", readonly = True),
                                              dict(name='Load Data', type = 'action', title = "Load!!!"),
                                              dict(name = 'Forward', type = 'action', title = 'Step Forward!!!'),
                                              dict(name = 'Backward', type = 'action', title = 'Step Backward!!!')]
                                )
    
        self.date_range = dict(name='Date Range', type='group', expanded = True, title = "Step 3: Specify a Date Range and Automatically Explore the Dynamic Data",
                              children=[dict(name='Start Date', type = 'group', expanded = False, title = "Specify Start Date", 
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 1),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 0)]),
                                        
                                        dict(name='End Date', type = 'group', expanded = False, title = "Specify End Date",
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 30),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 18)]),
                                        
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Load Data Range', type = 'action', title = "Load!!!"),
                                        dict(name = 'Play Data', type = 'action', title = 'Play!!!')]
                                )
                                        
        self.analyse_range = dict(name='Analysis', type='group', expanded = True, title = "Step 4: Find Potential Parking Spots",
                              children=[dict(name='Start Date', type = 'group', expanded = False, title = "Specify Start Date", 
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 2),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 10)]),
                                        
                                        dict(name='End Date', type = 'group', expanded = False, title = "Specify End Date",
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 2),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 18)]),
                                        
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Load Data Range', type = 'action', title = "Load"),
                                        dict(name='Parking Radius', type = 'float', title = "Parking Radius (m)", value = 100),
                                        dict(name='Parking Time Threshold', type = 'float', title = "Parking Time Threshold (hr)", value = 0.5),
                                        dict(name = 'Analyse Data', type = 'action', title = 'Analyse')]
                                )
                                 
        self.export_range = dict(name='Export', type='group', expanded = True, title = "Step 5: Export the Data",
                              children=[dict(name='Start Date', type = 'group', expanded = False, title = "Specify Start Date", 
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 2),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 10)]),
                                        
                                        dict(name='End Date', type = 'group', expanded = False, title = "Specify End Date",
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 9),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 2),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 18)]),
                                        
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Load Data Range', type = 'action', title = "Load"),
                                        
                                        dict(name='Result File Chosen', type = 'str', value = "", readonly = True),
                                        dict(name='Choose Result Filepath', type='action'),
                                        dict(name = 'Export Data', type = 'action', title = 'Export')]
                                )
        
        self.params = Parameter.create(name='ParmX', type='group', children=[self.layers,
                                                                             self.load_result,
                                                                             self.date_range,
                                                                             self.analyse_range,
                                                                             self.export_range]
                                        )
        
        self.tree.setParameters(self.params, showTop=False)
        
        #generate falsecolour bar
        self.min_val = 133.0
        self.max_val = 914.0
        
        self.falsecolour = p4d_func.gen_falsecolour_bar(self.min_val, self.max_val)
        self.min_max = dict(name='Min Max', type='group', expanded = True, title = "Specify the Min Max Value",
                            children=[dict(name='Min Value', type = 'float', title = "Min Value", value = self.min_val),
                                      dict(name='Max Value', type = 'float', title = "Max Value", value = self.max_val),
                                      dict(name = 'Change Min Max', type = 'action', title = 'Change Min Max')]
                            )
        
        self.params2 = Parameter.create(name = "Parmx2", type = "group", children = [self.falsecolour,
                                                                                     self.min_max])
        self.tree2.setParameters(self.params2, showTop=False)
        
        
        self.params.param('Layers').param("Change Layers Visibility").sigActivated.connect(self.change_visibility)
        
        self.params.param('Load Result').param("Load Data").sigActivated.connect(self.load_data)
        self.params.param('Load Result').param("Forward").sigActivated.connect(self.forward)
        self.params.param('Load Result').param("Backward").sigActivated.connect(self.backward)
        
        self.params.param('Date Range').param("Load Data Range").sigActivated.connect(self.load_data_range)
        self.params.param('Date Range').param("Play Data").sigActivated.connect(self.play_data)
        
        self.params.param('Analysis').param("Load Data Range").sigActivated.connect(self.load_analyse_data_range)
        self.params.param('Analysis').param("Analyse Data").sigActivated.connect(self.find_parking)
        
        self.params.param('Export').param("Choose Result Filepath").sigActivated.connect(self.choose_filepath)
        self.params.param('Export').param("Load Data Range").sigActivated.connect(self.load_export_data_range)
        self.params.param('Export').param("Export Data").sigActivated.connect(self.export_data)
        
        self.params2.param('Min Max').param("Change Min Max").sigActivated.connect(self.change_min_max)
        
        #check if there are parking data 
        self.check_parking_dir()
        if self.is_parking_layer:
            parking_layer = dict(name = 'Hourly Parking Spots', type = 'bool', value=True)
            self.params.param('Layers').param("Falsecolour Layer").addChild(parking_layer)
        
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
        
        self.tree2 = ParameterTree(showHeader=True)
        self.splitter2.addWidget(self.splitter)
        self.splitter2.addWidget(self.tree2)
        self.splitter2.setStretchFactor(0, 3)
        
        self.layout.addWidget(self.splitter2)
        
        self.view3d = gl.GLViewWidget()
        self.splitter.addWidget(self.view3d)
        
        self.solar_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\viz"
        self.travel_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\travel_extrude4carts"
        self.travel_shp_dir =  "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\travel_extrude4carts_shp"
        self.parking_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\parking4carts"
        
        self.parking_meshes = [None]
        #========================================================================
        #load the 3d terrain model
        #========================================================================
        terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\terrain.brep"
        terrain_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\terrains.json"
        
        terrain_cmpd = py3dmodel.utility.read_brep(terrain_filepath)
        midpt = py3dmodel.calculate.get_centre_bbox(terrain_cmpd)
        
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
        
        roof_mesh_list = p4d_func.read_meshes_json(roof_mesh_json, shader = "balloon", gloptions = "additive", draw_edges = False)
        roof_mesh_list[0].setColor([0.5,0.5,0.5,1])
        facade_mesh_list = p4d_func.read_meshes_json(facade_mesh_json, shader = "balloon", gloptions = "additive", draw_edges = False)
        line_list = p4d_func.read_edges_json(roof_edge_json, line_colour = (0,0,0,1), width = 1, antialias=True, mode="lines")
        
        self.roof_meshes = roof_mesh_list
        self.facade_meshes = facade_mesh_list
        self.bldg_lines = line_list
        #========================================================================
        #load the trees 
        #========================================================================
        tree_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\trees.json"
        tree_meshes = p4d_func.read_meshes_json(tree_mesh_json, shader = "shaded", gloptions = "additive")
        tree_meshes[0].setColor([0,0.5,0,1])
        
        self.tree_meshes = tree_meshes
        #========================================================================
        #load roads 
        #========================================================================
        road_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\roads.json"
        road_meshes = p4d_func.read_meshes_json(road_mesh_json)
        for mesh in road_meshes:
            mesh.setColor([0.5,0.5,0.5,1])
        
        self.road_meshes = road_meshes
        #========================================================================
        #load falsecolour results 
        #========================================================================
        #get all the geometries 
        json_mesh_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\solar_grd.json"      
        
        falsecolour_mesh_list = p4d_func.read_meshes_json(json_mesh_filepath, shader = "balloon", gloptions = "translucent")
        self.colour_meshes = falsecolour_mesh_list
        #========================================================================
        #load extrusion results 
        #========================================================================
        path_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\path.json"
        extrude_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\extrude.json"
        extline_json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\extrude_lines.json"
        
        path_lines = p4d_func.read_edges_json(path_json_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
        extrude_meshes = p4d_func.read_meshes_json(extrude_json_filepath, shader = "shaded", gloptions = "additive")
        extrude_meshes[0].setColor([1,0,0,1])
        extrude_lines = p4d_func.read_edges_json(extline_json_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
        
        self.path_lines = path_lines
        self.extrude_meshes = extrude_meshes
        self.extrude_lines = extrude_lines
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
        
    def check_parking_dir(self):
        parking_dir = self.parking_dir 
        viz_dir = os.path.join(parking_dir, "viz")
        file_list = os.listdir(viz_dir)
        if file_list:
            self.is_parking_layer = True
        else:
            self.is_parking_layer = False
        
    def change_visibility(self):
        #get all the settings for static layers
        terrain_bool = self.params.param('Layers').param('Static Layer').param("Terrain").value()
        building_bool = self.params.param('Layers').param('Static Layer').param("Buildings").value()
        tree_bool = self.params.param('Layers').param('Static Layer').param("Trees").value()
        road_bool = self.params.param('Layers').param('Static Layer').param("Roads").value()
        
        #get all the settings for dynamic layers
        hrly_solar_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Grd Solar Irradiation").value()
        hrly_cart_bool = self.params.param('Layers').param('Extrusion Layer').param("Hourly Cart Travel Behaviour").value()
        
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
        
        #add a new analysis layer to the layer tab
        children = self.params.param('Layers').param("Falsecolour Layer").children()
        name_list = []
        for child in children:
            child_name = child.name()
            name_list.append(child_name)
 
        if 'Hourly Parking Spots' in name_list:
            parking_meshes = self.parking_meshes
            hrly_parking_bool = self.params.param('Layers').param('Falsecolour Layer').param('Hourly Parking Spots').value()
            p4d_func.set_graphic_items_visibility(parking_meshes, hrly_parking_bool)
            
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
        hour_index = p4d_func.date2index(date)
        self.current_index = hour_index
        print hour_index
        #=============================================
        #retrieve the solar data from the date index
        #=============================================
        solar_dir = self.solar_dir
        solar_mesh = self.colour_meshes
        p4d_func.retrieve_solar_data(solar_mesh[0], hour_index, solar_dir, self.min_val, self.max_val)
        #=============================================
        #retrieve the travel data
        #=============================================
        path_lines = self.path_lines 
        extrude_meshes = self.extrude_meshes
        extrude_lines = self.extrude_lines 
        
        travel_dir = self.travel_dir
        mesh_vis, bdry_vis, path_vis = p4d_func.retrieve_travel_data(hour_index, travel_dir, extrude_meshes, extrude_lines, path_lines, self.view3d)
        
        if mesh_vis !=None:
            p4d_func.viz_graphic_items([mesh_vis], self.view3d)
            p4d_func.viz_graphic_items([bdry_vis], self.view3d)
            
        if path_vis !=None:
            p4d_func.viz_graphic_items([path_vis], self.view3d)
            
        self.path_lines = [path_vis]
        self.extrude_meshes = [mesh_vis]
        self.extrude_lines = [bdry_vis]
        
        hrly_cart_bool = self.params.param('Layers').param('Extrusion Layer').param("Hourly Cart Travel Behaviour").value()
        p4d_func.set_graphic_items_visibility(self.path_lines, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_meshes, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_lines , hrly_cart_bool)
        #=============================================
        #retrieve the parking data
        #=============================================
        parking_meshes = self.parking_meshes
        parking_dir = self.parking_dir
        parking_mesh = p4d_func.retrieve_parking_data(hour_index, parking_dir, parking_meshes, self.view3d, self.min_val, self.max_val)
        if parking_mesh != None:
            p4d_func.viz_graphic_items([parking_mesh], self.view3d)
        
        self.parking_meshes = [parking_mesh]
        
        hrly_park_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Parking Spots").value()
        p4d_func.set_graphic_items_visibility(self.parking_meshes, hrly_park_bool)
    
    def forward(self):
        current_index = self.current_index
        current_date = self.current_date
        forward = current_index + 1
        forward_date = current_date + timedelta(hours=1)
        #=============================================
        #retrieve the solar data from the date index
        #=============================================
        solar_dir = self.solar_dir
        solar_mesh = self.colour_meshes
        p4d_func.retrieve_solar_data(solar_mesh[0], forward, solar_dir, self.min_val, self.max_val)
        #=============================================
        #retrieve the travel data
        #=============================================
        path_lines = self.path_lines 
        extrude_meshes = self.extrude_meshes
        extrude_lines = self.extrude_lines 
        
        travel_dir = self.travel_dir
        mesh_vis, bdry_vis, path_vis = p4d_func.retrieve_travel_data(forward, travel_dir, extrude_meshes, extrude_lines, path_lines, self.view3d)
        
        if mesh_vis !=None:
            p4d_func.viz_graphic_items([mesh_vis], self.view3d)
            p4d_func.viz_graphic_items([bdry_vis], self.view3d)
            
        if path_vis !=None:
            p4d_func.viz_graphic_items([path_vis], self.view3d)
            
        self.path_lines = [path_vis]
        self.extrude_meshes = [mesh_vis]
        self.extrude_lines = [bdry_vis]
        
        hrly_cart_bool = self.params.param('Layers').param('Extrusion Layer').param("Hourly Cart Travel Behaviour").value()
        p4d_func.set_graphic_items_visibility(self.path_lines, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_meshes, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_lines , hrly_cart_bool)
        #=============================================
        #retrieve the parking data
        #=============================================
        parking_meshes = self.parking_meshes
        parking_dir = self.parking_dir
        parking_mesh = p4d_func.retrieve_parking_data(forward, parking_dir, parking_meshes, self.view3d, self.min_val, self.max_val)
        if parking_mesh != None:
            p4d_func.viz_graphic_items([parking_mesh], self.view3d)
        
        self.parking_meshes = [parking_mesh]
        
        hrly_park_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Parking Spots").value()
        p4d_func.set_graphic_items_visibility(self.parking_meshes, hrly_park_bool)
        #=============================================
        #update the dates
        #=============================================
        self.current_index = forward
        self.current_date = forward_date
        str_date = forward_date.strftime("%Y-%m-%d %H:%M:%S")
        self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        self.params.param('Load Result').param('Date of Interest').param("Year:").setValue(int(forward_date.strftime("%Y")))
        self.params.param('Load Result').param('Date of Interest').param("Month:").setValue(int(forward_date.strftime("%m")))
        self.params.param('Load Result').param('Date of Interest').param("Day:").setValue(int(forward_date.strftime("%d")))
        self.params.param('Load Result').param('Date of Interest').param("Hour:").setValue(int(forward_date.strftime("%H")))
        
    def backward(self):
        current_index = self.current_index
        current_date = self.current_date
        backward = current_index - 1
        backward_date = current_date - timedelta(hours=1)
        #=============================================
        #retrieve the solar data from the date index
        #=============================================
        solar_dir = self.solar_dir
        solar_mesh = self.colour_meshes
        p4d_func.retrieve_solar_data(solar_mesh[0], backward, solar_dir, self.min_val, self.max_val)
        #=============================================
        #retrieve the travel data
        #=============================================
        path_lines = self.path_lines 
        extrude_meshes = self.extrude_meshes
        extrude_lines = self.extrude_lines 
        
        travel_dir = self.travel_dir
        mesh_vis, bdry_vis, path_vis = p4d_func.retrieve_travel_data(backward, travel_dir, extrude_meshes, extrude_lines, path_lines, self.view3d)
        
        if mesh_vis !=None:
            p4d_func.viz_graphic_items([mesh_vis], self.view3d)
            p4d_func.viz_graphic_items([bdry_vis], self.view3d)
            
        if path_vis !=None:
            p4d_func.viz_graphic_items([path_vis], self.view3d)
            
        self.path_lines = [path_vis]
        self.extrude_meshes = [mesh_vis]
        self.extrude_lines = [bdry_vis]
        
        hrly_cart_bool = self.params.param('Layers').param('Extrusion Layer').param("Hourly Cart Travel Behaviour").value()
        p4d_func.set_graphic_items_visibility(self.path_lines, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_meshes, hrly_cart_bool)
        p4d_func.set_graphic_items_visibility(self.extrude_lines , hrly_cart_bool)
        
        #=============================================
        #retrieve the parking data
        #=============================================
        parking_meshes = self.parking_meshes
        parking_dir = self.parking_dir
        parking_mesh = p4d_func.retrieve_parking_data(backward, parking_dir, parking_meshes, self.view3d, self.min_val, self.max_val)
        if parking_mesh != None:
            p4d_func.viz_graphic_items([parking_mesh], self.view3d)
        
        self.parking_meshes = [parking_mesh]
        
        hrly_park_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Parking Spots").value()
        p4d_func.set_graphic_items_visibility(self.parking_meshes, hrly_park_bool)
        
        #=============================================
        #update the dates
        #=============================================
        self.current_index = backward
        self.current_date = backward_date
        str_date = backward_date.strftime("%Y-%m-%d %H:%M:%S")
        self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        self.params.param('Load Result').param('Date of Interest').param("Year:").setValue(int(backward_date.strftime("%Y")))
        self.params.param('Load Result').param('Date of Interest').param("Month:").setValue(int(backward_date.strftime("%m")))
        self.params.param('Load Result').param('Date of Interest').param("Day:").setValue(int(backward_date.strftime("%d")))
        self.params.param('Load Result').param('Date of Interest').param("Hour:").setValue(int(backward_date.strftime("%H")))
    
    def load_data_range(self):
        #get the start date
        s_year = self.params.param('Date Range').param('Start Date').param("Year:").value()
        s_mth = self.params.param('Date Range').param('Start Date').param("Month:").value()
        s_day = self.params.param('Date Range').param('Start Date').param("Day:").value()
        s_hour = self.params.param('Date Range').param('Start Date').param("Hour:").value()
        s_min = 0
        s_sec = 0
        str_sp_date = str(s_year) + "-" + str(s_mth) + "-" + str(s_day) + "-" +\
                        str(s_hour) + ":" + str(s_min) + ":" + str(s_sec)
                                
        #sdate = parse(str_sp_date)
        
        #get the end date
        e_year = self.params.param('Date Range').param('End Date').param("Year:").value()
        e_mth = self.params.param('Date Range').param('End Date').param("Month:").value()
        e_day = self.params.param('Date Range').param('End Date').param("Day:").value()
        e_hour = self.params.param('Date Range').param('End Date').param("Hour:").value()
        e_min = 0
        e_sec = 0
        str_e_date = str(e_year) + "-" + str(e_mth) + "-" + str(e_day) + "-" +\
                        str(e_hour) + ":" + str(e_min) + ":" + str(e_sec)
                                
        #edate = parse(str_e_date)
        
        self.str_start_date = str_sp_date
        self.str_end_date = str_e_date
        
        self.params.param('Date Range').param('Data Range Loaded').setValue(str_sp_date + " to " + str_e_date)
    
    def play_data(self):
        import subprocess
        str_start_date = self.str_start_date
        str_end_date = self.str_end_date
        current_path = os.path.dirname(__file__)
        ani_file = os.path.join(current_path, "p4d_animation.py")
        
        terrain_bool = self.params.param('Layers').param('Static Layer').param("Terrain").value()
        building_bool = self.params.param('Layers').param('Static Layer').param("Buildings").value()
        tree_bool = self.params.param('Layers').param('Static Layer').param("Trees").value()
        road_bool = self.params.param('Layers').param('Static Layer').param("Roads").value()
        
        #get all the settings for dynamic layers
        hrly_solar_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Grd Solar Irradiation").value()
        hrly_cart_bool = self.params.param('Layers').param('Extrusion Layer').param("Hourly Cart Travel Behaviour").value()
        hrly_park_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Parking Spots").value()
        
        #get all the visible layers
        layer_list = []
        
        if terrain_bool:
            layer_list.append("terrains")
        
        if tree_bool:
            layer_list.append("trees")
        
        if road_bool:
            layer_list.append("roads")
        
        if building_bool:
            layer_list.append("buildings")
        
        if hrly_solar_bool:
            layer_list.append("irradiations")
            
        if hrly_cart_bool:
            layer_list.append("travels")
            
        if hrly_park_bool:
            layer_list.append("parkings")
            
        
        call_list = ["python", ani_file, str_start_date, str_end_date, str(self.min_val), str(self.max_val)]
        for lay in layer_list:
            call_list.append(lay)
            
        subprocess.call(call_list)
        
    def change_min_max(self):
        solar_dir = self.solar_dir
        self.min_val = self.params2.param('Min Max').param('Min Value').value()
        self.max_val = self.params2.param('Min Max').param('Max Value').value()
        
        #change the falsecolour bar first 
        param2 = self.params2
        p4d_func.edit_falsecolour(param2, self.min_val, self.max_val)
        
        #then change the colours on the model
        hour_index = self.current_index 
        solar_mesh = self.colour_meshes
        p4d_func.retrieve_solar_data(solar_mesh[0], hour_index, solar_dir, self.min_val, self.max_val)
        
        parking_meshes = self.parking_meshes
        parking_dir = self.parking_dir
        parking_mesh = p4d_func.retrieve_parking_data(hour_index, parking_dir, parking_meshes, self.view3d, self.min_val, self.max_val)
        if parking_mesh != None:
            p4d_func.viz_graphic_items([parking_mesh], self.view3d)
        
        self.parking_meshes = [parking_mesh]
        hrly_park_bool = self.params.param('Layers').param('Falsecolour Layer').param("Hourly Parking Spots").value()
        p4d_func.set_graphic_items_visibility(self.parking_meshes, hrly_park_bool)
        
    def load_analyse_data_range(self):
        #get the start date
        s_year = self.params.param('Analysis').param('Start Date').param("Year:").value()
        s_mth = self.params.param('Analysis').param('Start Date').param("Month:").value()
        s_day = self.params.param('Analysis').param('Start Date').param("Day:").value()
        s_hour = self.params.param('Analysis').param('Start Date').param("Hour:").value()
        s_min = 0
        s_sec = 0
        str_sp_date = str(s_year) + "-" + str(s_mth) + "-" + str(s_day) + "-" +\
                        str(s_hour) + ":" + str(s_min) + ":" + str(s_sec)
                                
        #sdate = parse(str_sp_date)
        
        #get the end date
        e_year = self.params.param('Analysis').param('End Date').param("Year:").value()
        e_mth = self.params.param('Analysis').param('End Date').param("Month:").value()
        e_day = self.params.param('Analysis').param('End Date').param("Day:").value()
        e_hour = self.params.param('Analysis').param('End Date').param("Hour:").value()
        e_min = 0
        e_sec = 0
        str_e_date = str(e_year) + "-" + str(e_mth) + "-" + str(e_day) + "-" +\
                        str(e_hour) + ":" + str(e_min) + ":" + str(e_sec)
                                
        self.str_analysis_start_date = str_sp_date
        self.str_analysis_end_date = str_e_date
        
        self.params.param('Analysis').param('Data Range Loaded').setValue(str_sp_date + " to " + str_e_date)
         
    def find_parking(self):
        start_date = parse(self.str_analysis_start_date)
        end_date = parse(self.str_analysis_end_date)
        start_index = p4d_func.date2index(start_date)
        end_index = p4d_func.date2index(end_date)
        
        parking_radius = self.params.param('Analysis').param('Parking Radius').value()
        parking_time = self.params.param('Analysis').param('Parking Time Threshold').value()
        
        solar_dir = self.solar_dir
        travel_shp_dir = self.travel_shp_dir
        parking_dir = self.parking_dir
        p4d_func.find_potential_parkings(start_index, end_index, solar_dir, travel_shp_dir, parking_dir, parking_radius, stop_time_threshold = parking_time)
        
        #add a new analysis layer to the layer tab
        if not self.is_parking_layer:
            parking_layer = dict(name = 'Hourly Parking Spots', type = 'bool', value=True)
            self.params.param('Layers').param("Falsecolour Layer").addChild(parking_layer)
            self.params.param('Layers').param("Falsecolour Layer").param('Hourly Grd Solar Irradiation').setValue(False)
            self.change_visibility()
        
        self.params.param('Load Result').param('Date of Interest').param("Year:").setValue(int(start_date.strftime("%Y")))
        self.params.param('Load Result').param('Date of Interest').param("Month:").setValue(int(start_date.strftime("%m")))
        self.params.param('Load Result').param('Date of Interest').param("Day:").setValue(int(start_date.strftime("%d")))
        self.params.param('Load Result').param('Date of Interest').param("Hour:").setValue(int(start_date.strftime("%H")))
        self.load_data()
        
    def load_export_data_range(self):
        #get the start date
        s_year = self.params.param('Export').param('Start Date').param("Year:").value()
        s_mth = self.params.param('Export').param('Start Date').param("Month:").value()
        s_day = self.params.param('Export').param('Start Date').param("Day:").value()
        s_hour = self.params.param('Export').param('Start Date').param("Hour:").value()
        s_min = 0
        s_sec = 0
        str_sp_date = str(s_year) + "-" + str(s_mth) + "-" + str(s_day) + "-" +\
                        str(s_hour) + ":" + str(s_min) + ":" + str(s_sec)
                                
        #sdate = parse(str_sp_date)
        
        #get the end date
        e_year = self.params.param('Export').param('End Date').param("Year:").value()
        e_mth = self.params.param('Export').param('End Date').param("Month:").value()
        e_day = self.params.param('Export').param('End Date').param("Day:").value()
        e_hour = self.params.param('Export').param('End Date').param("Hour:").value()
        e_min = 0
        e_sec = 0
        str_e_date = str(e_year) + "-" + str(e_mth) + "-" + str(e_day) + "-" +\
                        str(e_hour) + ":" + str(e_min) + ":" + str(e_sec)
                                
        self.str_export_start_date = str_sp_date
        self.str_export_end_date = str_e_date
        
        self.params.param('Export').param('Data Range Loaded').setValue(str_sp_date + " to " + str_e_date)
        
    def choose_filepath(self):
        fn = pg.QtGui.QFileDialog.getOpenFileName(self, "Choose File Path", "")
        self.params.param('Export').param('Result File Chosen').setValue(str(fn[0]))
        self.result_filepath = str(fn[0])
        if fn == '':
            return
        
    def export_data(self):
        start_date =  parse(self.str_export_start_date)
        start_index = p4d_func.date2index(start_date)
        
        end_date = parse(self.str_export_end_date)
        end_index = p4d_func.date2index(end_date)
        
        res_filepath = self.result_filepath
        res_str = p4d_func.export_data(start_index, end_index, self.travel_shp_dir, self.parking_dir)
        f = open(res_filepath, "w")
        f.write(res_str)
        f.close()
        
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = Dashboard()
    win.setWindowTitle("Solar + Travel Visualiser (Alpha)")
    win.show()
    win.showMaximized()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()