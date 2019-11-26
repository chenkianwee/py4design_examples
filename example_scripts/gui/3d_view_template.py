import os
import sys
import csv
from dateutil.parser import parse
from dateutil import tz

import numpy as np
from py4design import py3dmodel
import PyQt5
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree

import coldtube_viz_functions as ct_func

class ColdtubeDashboard(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.date_range = dict(name='Date Range', type='group', expanded = True, title = "Step 1: Specify the Date Range of the Data",
                              children=[dict(name='Start Date', type = 'group', title = "Specify Start Date", 
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 15),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 8),
                                                         dict(name='Minute:', type= 'int', limits = (0,59), value = 45),
                                                         dict(name='Second:', type= 'int', limits = (0,59), value = 00)]
                                                                       
                                             ),
                                        dict(name='End Date', type = 'group', title = "Specify End Date",
                                             children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                         dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                         dict(name='Day:', type= 'int', limits = (1,31), value = 15),
                                                         dict(name='Hour:', type= 'int', limits = (0,23), value = 18),
                                                         dict(name='Minute:', type= 'int', limits = (0,59), value = 0),
                                                         dict(name='Second:', type= 'int', limits = (0,59), value = 0)]
                                                         
                                             ),
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Load Data Range', type = 'action', title = "Load!!!"),
                                        dict(name = 'Play Data', type = 'action', title = 'Play!!!'),
                                        ]
                                )
        
        self.load_result = dict(name='Load Result', type='group', expanded = True, title = "Step 2: Specify a Data and Load It !!!",
                                children=[dict(name='Date of Interest', type = 'group', title = "Specify Date of Interest", 
                                               children = [dict(name='Year:', type= 'list', values= [2018, 2019], value=2019),
                                                           dict(name='Month:', type= 'int', limits = (1,12), value = 1),
                                                           dict(name='Day:', type= 'int', limits = (1,31), value = 15),
                                                           dict(name='Hour:', type= 'int', limits = (0,23), value = 14),
                                                           dict(name='Minute:', type= 'int', limits = (0,59), value = 0),
                                                           dict(name='Second:', type= 'int', limits = (0,59), value = 0)]
                                               ),
                                        
                                          dict(name='Data Loaded', type = 'str', title = "Data Loaded", readonly = True),
                                          dict(name='Load Data', type = 'action', title = "Load!!!"),
                                          dict(name = 'Forward', type = 'action', title = 'Step Forward!!!'),
                                          dict(name = 'Backward', type = 'action', title = 'Step Backward!!!')
                                          ]
                                )
        
        self.params = Parameter.create(name='ParmX', type='group', children=[self.date_range,
                                                                             self.load_result])
        
        self.tree.setParameters(self.params, showTop=False)
        
        #generate falsecolour bar
        self.min_val = 10
        self.max_val = 33
        self.falsecolour = ct_func.gen_falsecolour_bar(self.min_val, self.max_val)
        
        self.env_parm = dict(name='Environment', type='group', expanded = True, title = "The Environment (C)",
                                children=[
                                          dict(name='Air Temp', type = 'str', title = "Air Temp", readonly = True),
                                          dict(name='Dewpoint', type = 'str', title = "Dewpoint", readonly = True),
                                          dict(name='Globe Temp', type = 'str', title = "Globe Temp", readonly = True)
                                          ]
                                )
        self.params2 = Parameter.create(name = "Parmx2", type = "group", children = [self.falsecolour,
                                                                                     self.env_parm])
        self.tree2.setParameters(self.params2, showTop=False)
        
        self.params.param('Date Range').param("Load Data Range").sigActivated.connect(self.load_data_range)
        self.params.param('Load Result').param("Load Data").sigActivated.connect(self.load_data)
        self.params.param('Date Range').param("Play Data").sigActivated.connect(self.play_data)
        self.params.param('Load Result').param("Forward").sigActivated.connect(self.forward)
        self.params.param('Load Result').param("Backward").sigActivated.connect(self.backward)
        
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
        self.view3d.opts['distance'] = 10
        self.splitter.addWidget(self.view3d)
        
        #load the coldtube 3d model
        #get the 3d model directory
        current_path = os.path.dirname(__file__)
        model3d_path = os.path.join(current_path, "coldtube_viz")
        #get the panel model
        geom_dict = {}
        for i in range(10):
            membrane_name = "panel_membrane_" + str(i+1) 
            membrane_path = os.path.join(model3d_path, membrane_name+ ".dae")
            mmeshes = ct_func.collada2meshes(membrane_path)
            geom_dict[membrane_name] = mmeshes
            ct_func.viz_mesh(mmeshes, self.view3d)
            
            panel_name = "panel" + str(i+1) 
            panel_path = os.path.join(model3d_path, panel_name+ ".dae")
            pmeshes = ct_func.collada2meshes(panel_path)
            geom_dict[panel_name] = pmeshes
            ct_func.viz_mesh(pmeshes, self.view3d)
                
        #get the floor
        floor_path = os.path.join(model3d_path, "floor.dae")
        fmeshes = ct_func.collada2meshes(floor_path)
        geom_dict["floor"] = fmeshes
        ct_func.viz_mesh(fmeshes, self.view3d)
        
        #get the tanks 
        red_tank_path = os.path.join(model3d_path, "red_tank.dae")
        rmeshes = ct_func.collada2meshes(red_tank_path)
        geom_dict["red_tank"] = rmeshes
        ct_func.viz_mesh(rmeshes, self.view3d)
        
        red_tank_supply_path = os.path.join(model3d_path, "red_tank_supply.dae")
        rsmeshes = ct_func.collada2meshes(red_tank_supply_path)
        geom_dict["red_tank_supply"] = rsmeshes
        ct_func.viz_mesh(rsmeshes, self.view3d)
        
        red_tank_return_path = os.path.join(model3d_path, "red_tank_return.dae")
        rrmeshes = ct_func.collada2meshes(red_tank_return_path)
        geom_dict["red_tank_return"] = rrmeshes
        ct_func.viz_mesh(rrmeshes, self.view3d)
        
        blue_tank_path = os.path.join(model3d_path, "blue_tank.dae")
        bmeshes = ct_func.collada2meshes(blue_tank_path)
        geom_dict["blue_tank"] = bmeshes
        ct_func.viz_mesh(bmeshes, self.view3d)
        
        blue_tank_supply_path = os.path.join(model3d_path, "blue_tank_supply.dae")
        bsmeshes = ct_func.collada2meshes(blue_tank_supply_path)
        geom_dict["blue_tank_supply"] = bsmeshes
        ct_func.viz_mesh(bsmeshes, self.view3d)
        
        blue_tank_return_path = os.path.join(model3d_path, "blue_tank_return.dae")
        brmeshes = ct_func.collada2meshes(blue_tank_return_path)
        geom_dict["blue_tank_return"] = brmeshes
        ct_func.viz_mesh(brmeshes, self.view3d)
        self.geometry = geom_dict
        
    def load_data_range(self):
        pass
    
    def load_data(self):
        pass
        
    def play_data(self):
        pass
    
    def forward(self):
        pass
    
    def backward(self):
        pass
            
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = ColdtubeDashboard()
    win.setWindowTitle("ColdTube Dashboard 3D")
    win.show()
    win.showMaximized()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()