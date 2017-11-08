import os
from pyliburo import py3dmodel, shp2citygml, urbangeom
import shapefile
import gdal
import numpy as np

import PyQt5
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtGui, QtCore
import sys

class Shp2DTo3DGUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.shapefile = dict(name='Shape File', type='group', title = "Specify Shape File",
                              children=[dict(name='Shapefile Loaded', type = 'str', value = "", readonly = True),
                                        dict(name='Load Shapefile', type='action')])
    
        self.height_attrib = dict(name='Height Attrib', type='group', title = "Specify Height Attribute of the Shape File",
                              children=[dict(name='Height Attribute', type = 'str', value = "")])
    
        self.dtmfile = dict(name='DTM File', type='group', title = "Specify DTM File",
                              children=[dict(name='DTM Loaded', type = 'str', value = "", readonly = True),
                                        dict(name='Load DTM', type='action')])
    
        self.result_directory = dict(name='Result Directory', type='group', title = "Specify Result Directory",
                              children=[dict(name='Result Directory Chosen', type = 'str', value = "", readonly = True),
                                        dict(name='Choose Result Directory', type='action')])
    
        #self.interactive_view = dict(name='Interactive View', type='group', expanded = True, title = "Turn on/off Interactive Viewer",
        #                      children=[dict(name='Viewer On', type = 'bool', value = True)])
        
        self.result_view = dict(name='Result View', type='group', expanded = True, title = "Result View",
                              children=[dict(name='Progress', type = 'str', value ="",  readonly = True, title = "Progress")])
                                        
        
        self.params = Parameter.create(name='ParmX', type='group', children=[self.shapefile,
                                                                             self.height_attrib,
                                                                             self.dtmfile,
                                                                             self.result_directory, 
                                                                             #self.interactive_view,
                                                                             dict(name='Convert', type='action', title="Convert!!!"),
                                                                             self.result_view])
        self.tree.setParameters(self.params, showTop=False)
        self.params.param('Shape File').param("Load Shapefile").sigActivated.connect(self.load_shpfile)
        self.params.param('DTM File').param('Load DTM').sigActivated.connect(self.load_dtm)
        self.params.param('Result Directory').param('Choose Result Directory').sigActivated.connect(self.choose_result_directory)
        self.params.param('Convert').sigActivated.connect(self.convert)
        
        self.progress = 0
        self.timer = pg.QtCore.QTimer()
        
    def setupGUI(self):
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        self.tree = ParameterTree(showHeader=False)
        self.progress_bar = QtGui.QProgressBar(self)
        self.progress_bar.setGeometry(200, 80, 250, 20)
        self.splitter.addWidget(self.tree)
        self.layout.addWidget(self.progress_bar)
        
    def load_shpfile(self):
        fn = pg.QtGui.QFileDialog.getOpenFileName(self, "Load Shapefile", "", "Shapefile (*.shp)")
        self.params.param('Shape File').param('Shapefile Loaded').setValue(str(fn[0]))
        
        if fn == '':
            return
        
    def load_dtm(self):
        fn = pg.QtGui.QFileDialog.getOpenFileName(self, "Load DTM", "", "DTM (*.tif)")
        self.params.param('DTM File').param('DTM Loaded').setValue(str(fn[0]))
        
        if fn == '':
            return
        
    def choose_result_directory(self):
        fn = pg.QtGui.QFileDialog.getExistingDirectory(self, "Choose Result Directory", "")
        self.params.param('Result Directory').param('Result Directory Chosen').setValue(fn)
        
        if fn == '':
            return
        
    def update_bar(self):
        progress_value = self.progress
        self.progress_bar.setValue(progress_value)
        
    def convert(self):
        import time
        QtGui.QApplication.processEvents()
        self.progress = 0
        self.update_bar()
        self.params.param('Result View').param('Progress').setValue("")
        #get the shpfile
        height_attrib = str(self.params.param('Height Attrib').param('Height Attribute').value())
        bldg_footprint_shp_file = self.params.param('Shape File').param('Shapefile Loaded').value()
        dtm_tif_file = self.params.param('DTM File').param('DTM Loaded').value()
        result_directory = self.params.param('Result Directory').param('Result Directory Chosen').value()
        #viewer = self.params.param('Interactive View').param('Viewer On').value()
        
        
        self.timer.timeout.connect(self.update_bar)
        self.timer.start(20)
        #===========================================================================================
        #FUNCTIONS
        #===========================================================================================
        def raster_reader(input_terrain_raster):
            '''
            __author__ = "Paul Neitzel, Kian Wee Chen"
            __copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
            __credits__ = ["Paul Neitzel", "Jimeno A. Fonseca"]
            __license__ = "MIT"
            __version__ = "0.1"
            __maintainer__ = "Daren Thomas"
            __email__ = "cea@arch.ethz.ch"
            __status__ = "Production"
            '''
            # read raster records
            raster_dataset = gdal.Open(input_terrain_raster)
            band = raster_dataset.GetRasterBand(1)
            a = band.ReadAsArray(0, 0, raster_dataset.RasterXSize, raster_dataset.RasterYSize)
            (y_index, x_index) = np.nonzero(a >= 0)
            (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster_dataset.GetGeoTransform()
            x_coords = x_index * x_size + upper_left_x + (x_size / 2)  # add half the cell size
            y_coords = y_index * y_size + upper_left_y + (y_size / 2)  # to centre the point
        
            return [(x, y, z) for x, y, z in zip(x_coords, y_coords, a[y_index, x_index])]

        #===========================================================================================
        #THE RESULT FILES
        #===========================================================================================
        north_facade_collada_filepath = os.path.join(result_directory, "north_facade.dae")
        south_facade_collada_filepath = os.path.join(result_directory, "south_facade.dae")
        east_facade_collada_filepath = os.path.join(result_directory, "east_facade.dae")
        west_facade_collada_filepath = os.path.join(result_directory, "west_facade.dae")
        roof_collada_filepath = os.path.join(result_directory, "roof.dae")
        footprint_collada_filepath = os.path.join(result_directory, "footprint.dae")
        terrain_collada_filepath = os.path.join(result_directory, "terrain.dae")
        
        try:
            #===========================================================================================
            #CONSTRUCT THE TERRAIN 
            #===========================================================================================
            
            time1 = time.clock()
            display_2dlist = []
            #read the tif terrain file and create a tin from it 
            pyptlist = raster_reader(dtm_tif_file)
            QtGui.QApplication.processEvents()
            self.params.param('Result View').param('Progress').setValue("Constructing the Terrain ... ...")
            self.progress = 10
            tin_occface_list = py3dmodel.construct.delaunay3d(pyptlist)
            terrain_shell = py3dmodel.construct.sew_faces(tin_occface_list)[0]
            #===========================================================================================
            #EXTRUDE THE BUILDING
            #===========================================================================================
            
            sf = shapefile.Reader(bldg_footprint_shp_file)
            shapeRecs=sf.shapeRecords()
            attrib_name_list = shp2citygml.get_field_name_list(sf)
            height_index = attrib_name_list.index(height_attrib) - 1
            
            solid_list = []
            face_list = []
            
            QtGui.QApplication.processEvents()
            self.params.param('Result View').param('Progress').setValue("Extruding the Buildings ... ...")
            self.progress = 20
            cnt = 0
            for rec in shapeRecs:
                
                QtGui.QApplication.processEvents()
                
                poly_attribs=rec.record
                height = poly_attribs[height_index]
                pypolygon_list2d = shp2citygml.get_geometry(rec)
                if pypolygon_list2d:
                    pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
                    occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
                    for occface in occface_list:
                        if height >0:
                            occsolid = py3dmodel.construct.extrude(occface, (0,0,1), height)
                            solid_list.append(occsolid)
                            face_list.append(occface)
                cnt+=1
            
            #move all the faces to a very high elevation and project them down onto the terrain so that we know where to place the buildings
            face_cmpd = py3dmodel.construct.make_compound(face_list)
            f_midpt = py3dmodel.calculate.get_centre_bbox(face_cmpd)
            loc_pt = [f_midpt[0], f_midpt[1], 1000]
            t_face_cmpd = py3dmodel.modify.move(f_midpt, loc_pt, face_cmpd)
            face_list2 = py3dmodel.fetch.topo_explorer(t_face_cmpd, "face")
            #face_list2 = face_list2[0:10]
            
            msolid_list = []
            
            QtGui.QApplication.processEvents()
            self.params.param('Result View').param('Progress').setValue("Placing the Buildings ... ...")
            self.progress = 50
            fcnt = 0
            for face2 in face_list2:
                pyptlist = py3dmodel.fetch.points_frm_occface(face2)
                #print "NUM PTS:", len(pyptlist)
                z_list = []
                for pypt in pyptlist:
                    
                    QtGui.QApplication.processEvents()
                    
                    interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(terrain_shell, pypt, (0,0,-1))
                    if interpt:
                        z = interpt[2]
                        z_list.append(z)
                if z_list:
                    min_z = min(z_list)
                    #print min_z
                    face = face_list[fcnt]
                    face_midpt = py3dmodel.calculate.face_midpt(face)
                    bldg_loc_pt = [face_midpt[0], face_midpt[1], min_z]
                    bsolid = solid_list[fcnt]
                    m_bsolid = py3dmodel.modify.move(face_midpt, bldg_loc_pt, bsolid)
                    msolid_list.append(m_bsolid)
                fcnt+=1
                        
            self.params.param('Result View').param('Progress').setValue("Classfying the Building Surfaces ... ...")
            QtGui.QApplication.processEvents()
            
            self.progress = 70
            total_facade_list = []
            total_roof_list = []
            total_footprint_list = []
            for solid in msolid_list:
                
                QtGui.QApplication.processEvents()
                
                facade_list, roof_list, footprint_list = urbangeom.identify_building_surfaces(solid)
                total_facade_list.extend(facade_list)
                total_roof_list.extend(roof_list)
                total_footprint_list.extend(footprint_list)
                
            n_list,s_list, e_list, w_list= urbangeom.identify_surface_direction(total_facade_list)
            
            QtGui.QApplication.processEvents()
            self.params.param('Result View').param('Progress').setValue("Writing the Building Surfaces ... ...")
            self.progress = 100
            py3dmodel.export_collada.write_2_collada(n_list, north_facade_collada_filepath)
            py3dmodel.export_collada.write_2_collada(s_list, south_facade_collada_filepath)
            py3dmodel.export_collada.write_2_collada(e_list, east_facade_collada_filepath)
            py3dmodel.export_collada.write_2_collada(w_list, west_facade_collada_filepath)
            py3dmodel.export_collada.write_2_collada(total_roof_list, roof_collada_filepath)
            py3dmodel.export_collada.write_2_collada(total_footprint_list, footprint_collada_filepath)
            py3dmodel.export_collada.write_2_collada([terrain_shell], terrain_collada_filepath)
            
            time2 = time.clock()
            time = (time2-time1)/60.0

            time_str = "Total Processing Time: " + str(round(time,2)) + " mins"
            QtGui.QApplication.processEvents()
            self.progress = 100
            self.params.param('Result View').param('Progress').setValue(time_str)
            #if viewer == True:
            #    cmpd = pyliburo.py3dmodel.construct.make_compound(msolid_list)
            #    display_2dlist.append([cmpd])
            #    display_2dlist.append([terrain_shell])
            #    pyliburo.py3dmodel.construct.visualise(display_2dlist, ["RED", "WHITE"])

            self.timer.stop()
        except:
            if self.progress == 10:
                self.params.param('Result View').param('Progress').setValue(str("there is an error at terrain construction !!!"))
            if self.progress == 20:
                self.params.param('Result View').param('Progress').setValue(str("there is an error at building extrusion !!!"))
            if self.progress == 50:
                self.params.param('Result View').param('Progress').setValue(str("there is an error at building placement !!!"))
            if self.progress == 70:
                self.params.param('Result View').param('Progress').setValue(str("there is an error at building classification !!!"))
            self.timer.stop()

#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = Shp2DTo3DGUI()
    win.setWindowTitle("Convert 2D shape files into 3D collada files")
    win.show()
    #win.showMaximized()
    win.resize(500,600)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()