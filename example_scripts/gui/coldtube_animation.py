import os
import sys
from dateutil.parser import parse

import PyQt5
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree

import coldtube_viz_functions as ct_func

class CTVisualiser(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.date_range = dict(name='Date Range', type='group', expanded = True, title = "",
                              children=[
                                        dict(name='Data Range Loaded', type = 'str', title = "Data Range Loaded", readonly = True),
                                        dict(name='Current Date', type = 'str', title = "Current Date", readonly = True),
                                        ]
                                )
        
                                     
        self.params = Parameter.create(name='ParmX', type='group', children=[self.date_range])
        
        self.tree.setParameters(self.params, showTop=False)
        
        self.current_index = 0
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
        
        start_date, end_date = self.retrieve_dates()
        data_dict, name_list, date_list = ct_func.read_data2memory(start_date, end_date)
        self.data = data_dict
        self.date_list = date_list
        self.ndates = len(date_list)
        self.data_keys = name_list
        
        date = date_list[self.current_index]
        
        mesh_list = ct_func.map_data23d(date, self.data, self.geometry, self.data_keys,
                                        self.min_val, self.max_val, self.view3d)
        
        ct_func.viz_mesh(mesh_list, self.view3d)
            
    
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
        
        #print image, self.tree
        
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
            
            panel_name = "panel" + str(i+1) 
            panel_path = os.path.join(model3d_path, panel_name+ ".dae")
            pmeshes = ct_func.collada2meshes(panel_path)
            geom_dict[panel_name] = pmeshes
                
        #get the floor
        floor_path = os.path.join(model3d_path, "floor.dae")
        fmeshes = ct_func.collada2meshes(floor_path)
        geom_dict["floor"] = fmeshes
        
        #get the tanks 
        red_tank_path = os.path.join(model3d_path, "red_tank.dae")
        rmeshes = ct_func.collada2meshes(red_tank_path)
        geom_dict["red_tank"] = rmeshes
        
        red_tank_supply_path = os.path.join(model3d_path, "red_tank_supply.dae")
        rsmeshes = ct_func.collada2meshes(red_tank_supply_path)
        geom_dict["red_tank_supply"] = rsmeshes
        
        red_tank_return_path = os.path.join(model3d_path, "red_tank_return.dae")
        rrmeshes = ct_func.collada2meshes(red_tank_return_path)
        geom_dict["red_tank_return"] = rrmeshes
        
        blue_tank_path = os.path.join(model3d_path, "blue_tank.dae")
        bmeshes = ct_func.collada2meshes(blue_tank_path)
        geom_dict["blue_tank"] = bmeshes
        
        blue_tank_supply_path = os.path.join(model3d_path, "blue_tank_supply.dae")
        bsmeshes = ct_func.collada2meshes(blue_tank_supply_path)
        geom_dict["blue_tank_supply"] = bsmeshes
        
        blue_tank_return_path = os.path.join(model3d_path, "blue_tank_return.dae")
        brmeshes = ct_func.collada2meshes(blue_tank_return_path)
        geom_dict["blue_tank_return"] = brmeshes
        self.geometry = geom_dict
        
    def retrieve_dates(self):
        arg_list = sys.argv
        start_date = parse(arg_list[1])
        end_date = parse(arg_list[2])
        #arg_list = ["", "2019-1-8-11:30:0+08:00", "2019-1-8-16:0:0+08:00"]
        #start_date = parse("2019-1-8-11:30:0+08:00")
        #end_date = parse("2019-1-8-16:0:0+08:00")
        self.params.param('Date Range').param('Data Range Loaded').setValue(arg_list[1] + " TO " + arg_list[2])
        return start_date, end_date
        
    def update(self):
        ndates = self.ndates
        cur_index = self.current_index
        nxt_index = cur_index + 1
        if nxt_index > ndates-1:
            nxt_index = 0
        
        self.current_index = nxt_index
        date = self.date_list[nxt_index]
        str_date = date.strftime("%Y-%m-%d %H:%M:%S")
        self.params.param('Date Range').param('Current Date').setValue(str_date)
        
        try:
            mesh_list = ct_func.map_data23d(date, self.data, self.geometry, self.data_keys,
                                            self.min_val, self.max_val, self.view3d)
            
            ct_func.viz_mesh(mesh_list, self.view3d)
            
            air, dew, globe = ct_func.get_env_temps(date, self.data)
            self.params2.param('Environment').param('Air Temp').setValue(str(air))
            self.params2.param('Environment').param('Dewpoint').setValue(str(dew))
            self.params2.param('Environment').param('Globe Temp').setValue(str(globe))
        
        except:
            print(self.current_index)
            
    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(100)
        self.start()
        
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
            
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = CTVisualiser()
    win.setWindowTitle("ColdTube Animation")
    win.show()
    win.showMaximized()
    win.animation()