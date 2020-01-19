
import PyQt5
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg

import gdal
import numpy as np

from py4design import py3dmodel

img_path = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\golfcart\\model3d\\solar_travel_data\\context3d\\map2.tif"

def image2array(raster_path):
    # read raster records
    raster_dataset = gdal.Open(raster_path)
    
    (xmin, x_pxsize, x_rotation, ymax, y_rotation, y_pxsize) = raster_dataset.GetGeoTransform()
    xcols = raster_dataset.RasterXSize
    yrows = raster_dataset.RasterYSize
    
    sizex = x_pxsize*xcols
    sizey = y_pxsize*yrows
    if sizey < 0:
        sizey = sizey*-1
    
    xmax = xmin + sizex
    ymin = ymax - sizey
    
    rgbas = raster_dataset.ReadAsArray(0, 0, xcols, yrows)
    midpt = [xmin + ((xmax-xmin)/2), ymin + ((ymax-ymin)/2), 0]
    img3d_arr = rgbas.T
    
    cond1 = (img3d_arr == [0,0,0,255]).all(axis = 2)
    cond1_shape = cond1.shape
    cond2 = np.reshape(cond1, (cond1_shape[0],cond1_shape[1],1))
    cond3 = np.repeat(cond2, 4, axis=2)
    
    np.place(img3d_arr, cond3, np.array([255,0,0,255], dtype = 'uint8'))
    
    # x = np.where((img3d_arr == [0,0,0,0]).all(axis=2))
    
    # print(len(x[1]))
    # print(x[0][0], x[1][0])
    # print(img3d_arr[67][798])
    return img3d_arr, sizex, sizey, xcols, yrows, midpt

def img2glimage(img_path):
    imgarr, sizex, sizey, xcols, yrows, midpt = image2array(img_path)
    v1 = gl.GLImageItem(imgarr)
    sx = sizex/xcols
    sy = sizey/yrows
    v1.scale(sx, sy, 0)
    
    dx = sizex/2#sizex/2
    dy = sizey/2#sizey/2
    v1.translate(-1*dx, -1*dy, 0)
    v1.rotate(180, 0,1,0)
    v1.rotate(180, 0,0,1)
    
    v1.translate(midpt[0], midpt[1], 0)
    return v1

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 200
w.show()
w.setWindowTitle('pyqtgraph example: GLImageItem')

## Create three image items from textures, add to view

v1 = img2glimage(img_path)
w.addItem(v1)

ax = gl.GLAxisItem()
ax.setSize(100,100,100)
w.addItem(ax)

midpt = [529271.2807499999, 4466068.291999999, 0]


w.opts['center'] = PyQt5.QtGui.QVector3D(midpt[0], midpt[1], midpt[2])
w.opts['distance'] = 5000
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
