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
        #get the starting date
        st_year = self.params.param('Date Range').param('Start Date').param("Year:").value()
        st_mth = self.params.param('Date Range').param('Start Date').param("Month:").value()
        st_day = self.params.param('Date Range').param('Start Date').param("Day:").value()
        st_hour = self.params.param('Date Range').param('Start Date').param("Hour:").value()
        st_min = self.params.param('Date Range').param('Start Date').param("Minute:").value()
        st_sec = self.params.param('Date Range').param('Start Date').param("Second:").value()
        str_start_date = str(st_year) + "-" + str(st_mth) + "-" + str(st_day) + "-" +\
                        str(st_hour) + ":" + str(st_min) + ":" + str(st_sec) +\
                        "+08:00"
                        
        start_date = parse(str_start_date)
        str_start_date2 = start_date.strftime("%Y-%m-%d %H:%M:%S")
        self.str_start_date = str_start_date
        
        #get the ending date
        e_year = self.params.param('Date Range').param('End Date').param("Year:").value()
        e_mth = self.params.param('Date Range').param('End Date').param("Month:").value()
        e_day = self.params.param('Date Range').param('End Date').param("Day:").value()
        e_hour = self.params.param('Date Range').param('End Date').param("Hour:").value()
        e_min = self.params.param('Date Range').param('End Date').param("Minute:").value()
        e_sec = self.params.param('Date Range').param('End Date').param("Second:").value()
        str_end_date = str(e_year) + "-" + str(e_mth) + "-" + str(e_day) + "-" +\
                        str(e_hour) + ":" + str(e_min) + ":" + str(e_sec) +\
                        "+08:00"
                        
        end_date = parse(str_end_date)
        str_end_date2 = end_date.strftime("%Y-%m-%d %H:%M:%S")
        self.str_end_date = str_end_date
        
        data_dict, name_list, date_list = ct_func.read_data2memory(start_date, end_date)
        
        self.date_list = date_list
        self.ndates = len(date_list)
        self.data_keys = name_list
        self.data = data_dict
        self.params.param('Date Range').param('Data Range Loaded').setValue(str_start_date2 + " TO " + str_end_date2)
    
    def load_data(self):
        #get the specified date
        s_year = self.params.param('Load Result').param('Date of Interest').param("Year:").value()
        s_mth = self.params.param('Load Result').param('Date of Interest').param("Month:").value()
        s_day = self.params.param('Load Result').param('Date of Interest').param("Day:").value()
        s_hour = self.params.param('Load Result').param('Date of Interest').param("Hour:").value()
        s_min = self.params.param('Load Result').param('Date of Interest').param("Minute:").value()
        s_sec = self.params.param('Load Result').param('Date of Interest').param("Second:").value()
        str_sp_date = str(s_year) + "-" + str(s_mth) + "-" + str(s_day) + "-" +\
                        str(s_hour) + ":" + str(s_min) + ":" + str(s_sec) +\
                        "+08:00"
                        
        
        date = parse(str_sp_date)
        zone = tz.gettz("Asia/Singapore")
        date = date.replace(tzinfo=zone)
        
        mesh_list = ct_func.map_data23d(date, self.data, self.geometry, 
                                         self.data_keys, self.min_val, self.max_val,
                                         self.view3d)
        
        ct_func.viz_mesh(mesh_list, self.view3d)
        
        air, dew, globe = ct_func.get_env_temps(date, self.data)
        self.params2.param('Environment').param('Air Temp').setValue(str(air))
        self.params2.param('Environment').param('Dewpoint').setValue(str(dew))
        self.params2.param('Environment').param('Globe Temp').setValue(str(globe))
                     
        self.current_date = date
        str_date = date.strftime("%Y-%m-%d %H:%M:%S")
        
        self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        
    def play_data(self):
        import subprocess
        str_start_date = self.str_start_date
        str_end_date = self.str_end_date
        current_path = os.path.dirname(__file__)
        ani_file = os.path.join(current_path, "coldtube_animation.py")
        #cmd = "python " + ani_file + " " + str_start_date + " " + str_end_date
        subprocess.call(["python", ani_file, str_start_date, str_end_date])
    
    def forward(self):
        date_list = self.date_list
        current_date = self.current_date
        current_index = date_list.index(current_date)
        forward_index = current_index + 1
        if forward_index > self.ndates-1:
            forward_index = 0
        
        #print "CURRENT DATE:",date_list[current_index]
        forward_date = date_list[forward_index]
        #print "FORWARD DATE:",forward_date
        if self.data == None:
            print "Please specify the date range in step 1"
        try:
            mesh_list = ct_func.map_data23d(forward_date, self.data, self.geometry, 
                                         self.data_keys, self.min_val, self.max_val,
                                         self.view3d)
            
            ct_func.viz_mesh(mesh_list, self.view3d)
            
            air, dew, globe = ct_func.get_env_temps(forward_date, self.data)
            self.params2.param('Environment').param('Air Temp').setValue(str(air))
            self.params2.param('Environment').param('Dewpoint').setValue(str(dew))
            self.params2.param('Environment').param('Globe Temp').setValue(str(globe))
        
            self.current_date = forward_date
            str_date = forward_date.strftime("%Y-%m-%d %H:%M:%S")
        
            self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        except:
            self.current_date = forward_date
            str_date = forward_date.strftime("%Y-%m-%d %H:%M:%S")
            self.params.param('Load Result').param('Data Loaded').setValue(str_date)
    
    def backward(self):
        date_list = self.date_list
        current_date = self.current_date
        current_index = date_list.index(current_date)
        back_index = current_index - 1
        if back_index < 0:
            back_index = self.ndates-1
            
        back_date = date_list[back_index]
        try:
            mesh_list = ct_func.map_data23d(back_date, self.data, self.geometry, 
                                            self.data_keys, self.min_val, self.max_val,
                                            self.view3d)
            
            ct_func.viz_mesh(mesh_list, self.view3d)
            
            air, dew, globe = ct_func.get_env_temps(back_date, self.data)
            self.params2.param('Environment').param('Air Temp').setValue(str(air))
            self.params2.param('Environment').param('Dewpoint').setValue(str(dew))
            self.params2.param('Environment').param('Globe Temp').setValue(str(globe))
            
            self.current_date = back_date
            
            str_date = back_date.strftime("%Y-%m-%d %H:%M:%S")
            self.params.param('Load Result').param('Data Loaded').setValue(str_date)
        except:
            self.current_date = back_date
            
            str_date = back_date.strftime("%Y-%m-%d %H:%M:%S")
            self.params.param('Load Result').param('Data Loaded').setValue(str_date)
            
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = ColdtubeDashboard()
    win.setWindowTitle("ColdTube Dashboard 3D")
    win.show()
    win.showMaximized()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()