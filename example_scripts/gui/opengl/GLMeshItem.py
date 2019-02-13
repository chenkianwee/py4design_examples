# -*- coding: utf-8 -*-
"""
Simple examples demonstrating the use of GLMeshItem.

"""

## Add path to library (just for examples; you do not need this)
#import initExample

import PyQt5
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLMeshItem')
w.setCameraPosition(distance=40)

g = gl.GLGridItem()
g.scale(2,2,1)
w.addItem(g)

import numpy as np


## Example 1:
## Array of vertex positions and array of vertex indexes defining faces
## Colors are specified per-face

verts = np.array([
    [0, 0, 0],
    [20, 0, 0],
    [1, 2, 0],
    [1, 1, 1],
])
faces = np.array([
    [0, 1, 2],
    [0, 1, 3],
    [0, 2, 3],
    [1, 2, 3]
])
colors = np.array([
    [0, 1, 1, 1],
    [1, 1, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
])

## Mesh item will automatically compute face normals.
m1 = gl.GLMeshItem(vertexes=verts, faceColors=colors, faces=faces, smooth=False,
                   drawFaces=False, drawEdges=True, edgeColor=(1, 1, 1, 1))
m1.translate(5, 5, 0)
#m1.setGLOptions('additive')
w.addItem(m1)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
