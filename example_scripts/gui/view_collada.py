import os
import sys

from py4design import py3dmodel
import numpy as np

import PyQt5
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl

class ColladaViewer(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.dae = dict(name='dae', type='group', title = "Specify Collada File",
                              children=[dict(name='Dae Loaded', type = 'str', value = "", readonly = True),
                                        dict(name='Load Collada (.dae)', type='action')])
        
        self.result_view = dict(name='Result View', type='group', expanded = True, title = "Result View",
                              children=[dict(name='Progress', type = 'str', value ="",  readonly = True, title = "Progress")])
                                        
        
        self.params = Parameter.create(name='ParmX', type='group', children=[self.dae,
                                                                             dict(name='View', type='action', title="Load!!!"),
                                                                             self.result_view])
        self.tree.setParameters(self.params, showTop=False)
        self.params.param('dae').param("Load Collada (.dae)").sigActivated.connect(self.load_collada)
        self.params.param('View').sigActivated.connect(self.view)
        
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
        
        self.view3d = gl.GLViewWidget()
        self.gx = gl.GLGridItem()
        self.gx.rotate(90, 0, 1, 0)
        self.gx.translate(-10, 0, 0)
        self.view3d.addItem(self.gx)
        self.gy = gl.GLGridItem()
        self.gy.rotate(90, 1, 0, 0)
        self.gy.translate(0, -10, 0)
        self.view3d.addItem(self.gy)
        self.gz = gl.GLGridItem()
        self.gz.translate(0, 0, -10)
        self.view3d.addItem(self.gz)
        self.splitter.addWidget(self.view3d)
    
    def load_collada(self):
        fn = pg.QtGui.QFileDialog.getOpenFileName(self, "Load Collada", "", "Collada (*.dae)")
        self.params.param('dae').param('Dae Loaded').setValue(str(fn[0]))
        
        if fn == '':
            return
        
    def view(self):
        filename = self.params.param('dae').param("Dae Loaded").value()
        display_list = self.read_collada(filename)
        viewer = self.view3d
        #display_list = display_list[0:1]
        for f in display_list:
            mesh = self.face2mesh(f)
            viewer.addItem(mesh)
    
    def face2mesh(self, occface):
        mesh_dict = py3dmodel.construct.face2mesh(occface)
        verts = mesh_dict["vertices"]
        faces = mesh_dict["indices"]
        verts = np.array(verts)
        faces = np.array(faces)
        fcolours = []
        for face in faces:
            fcolours.append([1,1,1,1])
            
        fcolours = np.array(fcolours)
        mesh = gl.GLMeshItem(vertexes=verts, faces=faces, faceColors=fcolours,
                             smooth=False, glOptions='opaque', shader='shaded',
                             drawEdges=True, edgeColor=(0, 0, 0, 1))
        
        return mesh
        
    def read_collada(self, filename):
        import collada
        from collada import polylist, triangleset
        mesh = collada.Collada(filename)
        unit = mesh.assetInfo.unitmeter or 1
        geoms = mesh.scene.objects('geometry')
        geoms = list(geoms)
        display_list = []
        g_cnt = 0
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
                                display_list.append(occpolygon)
                            g_cnt +=1
        
        return display_list
#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = ColladaViewer()
    win.setWindowTitle("Visualise Collada")
    win.show()
    win.showMaximized()
    #win.resize(500,600)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()