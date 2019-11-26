import sys
from dateutil.parser import parse
from datetime import timedelta

from py4design import py3dmodel
import PyQt5
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree

import p4d_function as p4d_func

class AnimationVisualiser(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        arg_list = self.retrieve_arg()
#        arg_list = [u'F:/kianwee_work/spyder_workspace/py4design_examples/example_scripts/model_princeton3d\\p4d_animation.py', '2019-9-2-10:0:0', '2019-9-10-18:0:0', '133.0', '914.0', 
#                    'terrains', 'trees', 'roads', 'buildings', 'travels', 'parkings']
        self.arg_list = arg_list
        self.setupGUI()
        
        self.date_range = dict(name='Date Range', type='group', expanded = True, title = "",
                               children=[
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Current Date', type = 'str', title = "Current Date", readonly = True),
                                        dict(name='Pause/Play', type = 'action', title = "Pause/Play"),
                                        dict(name='Rewind', type = 'action', title = "Rewind"),
                                        dict(name='Forward', type = 'action', title = "Forward"),
                                        dict(name='Play Status', type = 'str', title = "Play Status", value = "Forward", readonly = True),
                                        dict(name='Seconds/Frame', type = 'float', title = "Seconds/Frame", value = 1.0),
                                        dict(name='Change Playback Speed', type = 'action', title = "Change Playback Speed")
                                        ]
                               
                                )
                                     
        self.params = Parameter.create(name='ParmX', type='group', children=[self.date_range])
        
        s_date_str = arg_list[1]
        e_date_str = arg_list[2]
        date = parse(s_date_str)
        end_date = parse(e_date_str)
        
        self.rewind_status = False
        self.current_date = date
        start_index = p4d_func.date2index(date)
        self.current_index = start_index
        self.start_index = start_index
        self.start_date = date
        
        self.end_index = p4d_func.date2index(end_date)
        self.end_date = end_date
        
        self.params.param('Date Range').param('Data Range Loaded').setValue(s_date_str + " to " + e_date_str)
        self.tree.setParameters(self.params, showTop=False)
        
        self.min_val = float(arg_list[3])
        self.max_val = float(arg_list[4])
        
        self.falsecolour = p4d_func.gen_falsecolour_bar(self.min_val, self.max_val)
        
        self.params2 = Parameter.create(name = "Parmx2", type = "group", children = [self.falsecolour])
        
        self.tree2.setParameters(self.params2, showTop=False)
        
        self.params.param('Date Range').param("Pause/Play").sigActivated.connect(self.pause)
        self.params.param('Date Range').param("Rewind").sigActivated.connect(self.rewind)
        self.params.param('Date Range').param("Forward").sigActivated.connect(self.forward)
        self.params.param('Date Range').param("Change Playback Speed").sigActivated.connect(self.change_speed)
        
    def setupGUI(self):
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        #self.layout.addWidget(self.splitter)
        
        self.tree = ParameterTree(showHeader=False)
        self.splitter.addWidget(self.tree)
        
        self.progress_bar = QtGui.QProgressBar(self)
        self.progress_bar.setGeometry(200, 50, 250, 20)
        
        self.splitter2 = QtGui.QSplitter()
        self.splitter2.setOrientation(QtCore.Qt.Horizontal)
        
        self.tree2 = ParameterTree(showHeader=False)
        self.splitter2.addWidget(self.splitter)
        self.splitter2.addWidget(self.tree2)
        self.splitter2.setStretchFactor(0, 3)
        
        self.layout.addWidget(self.splitter2)
        
        self.view3d = gl.GLViewWidget()
        self.view3d.opts['distance'] = 10
        self.splitter.addWidget(self.view3d)
        
        self.playback_speed = 1000
        self.solar_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\viz"
        self.travel_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\travel_extrude4carts"
        self.parking_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\parking4carts"
        
        arg_list = self.arg_list
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
        if "buildings" in arg_list:
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
        if "trees" in arg_list:
            tree_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\trees.json"
            tree_meshes = p4d_func.read_meshes_json(tree_mesh_json, shader = "shaded", gloptions = "additive")
            tree_meshes[0].setColor([0,0.5,0,1])
            
            self.tree_meshes = tree_meshes
        #========================================================================
        #load roads 
        #========================================================================
        if "roads" in arg_list:
            road_mesh_json = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\roads.json"
            road_meshes = p4d_func.read_meshes_json(road_mesh_json)
            for mesh in road_meshes:
                mesh.setColor([0.5,0.5,0.5,1])
            
            self.road_meshes = road_meshes
        #========================================================================
        #load irrad results 
        #========================================================================
        if "irradiations" in arg_list:
            #get all the geometries 
            json_mesh_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\solar_grd.json"      
            
            falsecolour_mesh_list = p4d_func.read_meshes_json(json_mesh_filepath, shader = "balloon", gloptions = "translucent")
            self.colour_meshes = falsecolour_mesh_list
        else:
            self.colour_meshes = None
        #========================================================================
        #load travel results 
        #========================================================================
        if "travels" in arg_list:
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
        #load parking results 
        #========================================================================
        self.parking_meshes = [None]
        #========================================================================
        #determine the back and front of each geometry 
        #========================================================================
        if "terrains" in arg_list:
            p4d_func.viz_graphic_items(terrains_mesh_list, self.view3d)
        
        if "roads" in arg_list:
            p4d_func.viz_graphic_items(road_meshes , self.view3d)
        
        if "irradiations" in arg_list:
            p4d_func.viz_graphic_items(falsecolour_mesh_list, self.view3d)
        
        if "trees" in arg_list:
            p4d_func.viz_graphic_items(tree_meshes, self.view3d)
        
        if "buildings" in arg_list:
            p4d_func.viz_graphic_items(facade_mesh_list, self.view3d)
            p4d_func.viz_graphic_items(line_list, self.view3d)
            p4d_func.viz_graphic_items(roof_mesh_list, self.view3d)
        
        if "travels" in arg_list:
            p4d_func.viz_graphic_items(path_lines, self.view3d)
            p4d_func.viz_graphic_items(extrude_meshes, self.view3d)
            p4d_func.viz_graphic_items(extrude_lines, self.view3d)
        
        #========================================================================
        #configure the camera to orbit around the terrain
        #========================================================================
        self.view3d.opts['center'] = PyQt5.QtGui.QVector3D(midpt[0], midpt[1], midpt[2])
        self.view3d.opts['distance'] = 5000
        
    def retrieve_arg(self):
        arg_list = sys.argv
        return arg_list
        
    def update(self):        
        cur_index = self.current_index
        cur_date = self.current_date
        rewind_status = self.rewind_status
        
        if rewind_status == True:
            nxt_index = cur_index - 1
            nxt_date = cur_date - timedelta(hours=1)
            
#            self.params.param('Date Range').param('Play Status').setValue(str(nxt_index) + "nxt " + str(self.start_index)+ "start end" + str(self.end_index))
            
            if nxt_index < self.start_index:
                nxt_index = self.end_index
                nxt_date = self.end_date
                
        else:
            nxt_index = cur_index + 1
            nxt_date = cur_date + timedelta(hours=1)
            self.params.param('Date Range').param('Play Status').setValue("Forward")
            
#            self.params.param('Date Range').param('Play Status').setValue(str(nxt_index) + "nxt " + str(self.start_index)+ "start end" + str(self.end_index))
            
            if nxt_index > self.end_index:
                nxt_index = self.start_index
                nxt_date = self.start_date
             
        str_date = nxt_date.strftime("%Y-%m-%d %H:%M:%S")
        
        self.current_index = nxt_index
        self.current_date = nxt_date
        self.params.param('Date Range').param('Current Date').setValue(str_date)
        
        #=============================================
        #retrieve the solar data
        #=============================================
        solar_dir = self.solar_dir
        solar_mesh = self.colour_meshes
        if solar_mesh !=None:
            p4d_func.retrieve_solar_data(solar_mesh[0], nxt_index, solar_dir, self.min_val, self.max_val)
        
        #=============================================
        #retrieve the travel data
        #=============================================
        if "travels" in self.arg_list:
            path_lines = self.path_lines 
            extrude_meshes = self.extrude_meshes
            extrude_lines = self.extrude_lines 
            
            travel_dir = self.travel_dir
            mesh_vis, bdry_vis, path_vis = p4d_func.retrieve_travel_data(nxt_index, travel_dir, extrude_meshes, extrude_lines, path_lines, self.view3d)
            
            if mesh_vis !=None:
                p4d_func.viz_graphic_items([mesh_vis], self.view3d)
                p4d_func.viz_graphic_items([bdry_vis], self.view3d)
                
            if path_vis !=None:
                p4d_func.viz_graphic_items([path_vis], self.view3d)
                
            self.path_lines = [path_vis]
            self.extrude_meshes = [mesh_vis]
            self.extrude_lines = [bdry_vis]
            
        #=============================================
        #retrieve the parking data
        #=============================================
        if "parkings" in self.arg_list:
            parking_meshes = self.parking_meshes
            parking_dir = self.parking_dir
            parking_mesh = p4d_func.retrieve_parking_data(nxt_index, parking_dir, parking_meshes, self.view3d, self.min_val, self.max_val)
            if parking_mesh != None:
                p4d_func.viz_graphic_items([parking_mesh], self.view3d)
            
            self.parking_meshes = [parking_mesh]
        
    def animation(self):
        timer = QtCore.QTimer()
        self.timer = timer
        timer.timeout.connect(self.update)
        timer.start(self.playback_speed)
        self.timer_status = True
        self.start()
    
    def pause(self):
        cur_status = self.timer_status
        if cur_status:
            self.timer.stop()
            self.timer_status = False
            self.params.param('Date Range').param('Play Status').setValue("Pause")
        else:
            self.timer.start(self.playback_speed)
            self.timer_status = True
            rewind_state = self.rewind_status
            if rewind_state :
                self.params.param('Date Range').param('Play Status').setValue("Rewind")
            else:
                self.params.param('Date Range').param('Play Status').setValue("Forward")
    
    def rewind(self):
        cur_status = self.timer_status
        if cur_status:
            self.timer.stop()
            self.timer_status = False
        
        self.rewind_status = True
        self.params.param('Date Range').param('Play Status').setValue("Rewind")
        
    def forward(self):
        cur_status = self.timer_status
        if cur_status:
            self.timer.stop()
            self.timer_status = False
        
        self.rewind_status = False
        self.params.param('Date Range').param('Play Status').setValue("Forward")
        
    def change_speed(self):
        cur_status = self.timer_status
        if cur_status:
            self.timer.stop()
            self.timer_status = False
            
        seconds = self.params.param('Date Range').param('Seconds/Frame').value()
        self.playback_speed = seconds*1000       
        
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
            
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = AnimationVisualiser()
    win.setWindowTitle("Animation")
    win.show()
    win.showMaximized()
    win.animation()
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#            QtGui.QApplication.instance().exec_()