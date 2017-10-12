import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication, QDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt
from main_windows_resizable_GG import Ui_MainWindow
from pyqtgraph.parametertree import Parameter, ParameterTree
import shutil
import os

if os.name == 'nt': # Windows
    basepath = 'C:\\Users\\'
else:
    basepath = '.'   # current directory

##############################
#####    Functions    #####
##############################

###########
# Classes #
###########


class Curve(object):
    """
    A curve is simple object which contains basically: 
    * filename (full_path)
    * graph object 
    * item in the list
    * short_name
    all together
      
    """
    def __init__(self, filename=None, name=None):
        """
        Constructor of the class: 
        
        @param filename: name of the file containing the spectrum
        """
        self.graph = None
        self.data = None
        self.item = None
        if filename:
            self.full_path = os.path.abspath(filename)
            self.load_curve()
        else:
            self.full_path = self.filename = ""

        if name:
            self.name = name
        else:
            self.name = os.path.basename(self.full_path) or "Undefined"
        self.item = QtGui.QStandardItem(self.name)
        self.item.setCheckable(True)
        self.item.setCheckState(2)

    def __repr__(self):
        """ how I represent myself"""
        return self.name

    def load_curve(self):
        self.data = np.genfromtxt(self.full_path, skip_header=18, skip_footer=1, usecols=(0, 1), autostrip=True)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.curves = {} #key: filename, value: graph object
        self.clicked_spectrum = []

        self.model = QtGui.QFileSystemModel()
        filters = QStringList("*.txt")
        self.model.setNameFilters(filters) # allows to "grey" files that have not the right extension
        root = self.model.setRootPath(basepath)
        self.ui.files_treeView.setModel(self.model)
        self.ui.files_treeView.setSelectionMode(QTreeView.ExtendedSelection) # allows multiple file selection for loading
        self.ui.files_treeView.setRootIndex(root)
        self.ui.files_treeView.setHeaderHidden(1)
        self.ui.files_treeView.hideColumn(1)
        self.ui.files_treeView.hideColumn(2)
        self.ui.files_treeView.hideColumn(3)

#QtCore.QObject.connect(ui.files_treeView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), file_selection)
        self.ui.files_treeView.doubleClicked.connect(self.on_treeview_clicked)

###List of loaded files####

        self.list = QtGui.QListView()

        self.model_list = QtGui.QStandardItemModel(self.list)
        self.ui.listView.setSelectionMode(QAbstractItemView.ExtendedSelection) # allows multiple file selection for unloading


# This will be used for loading spectrum in the pyqtgraph and for filling the legend of the graph
        self.ui.listView.setModel(self.model_list)

        self.model_list.itemChanged.connect(self.on_item_changed)


# print model_list.itemFromIndex(QtGui.QModelIndex(2)).text()

        self.ui.load_pushButton.clicked.connect(self.load_selected_files) # --> has to be edited to load files that are selected in the browser
        self.ui.plot_pushButton.clicked.connect(self.plot_selected_data)
#ui.graphicsView.setBackground(None) # if None --> the background is transparent

###Setting the path for saving graphs####

        self.ui.PathToFile_lineEdit.setText('/path/to/my_saved_graph.png')
        self.ui.pushButton_2.clicked.connect(self.save_the_graph)

###Setting graphs rendering####

        self.ui.graphicsView.setLabel('left', text='Absorption [OD]')
        self.ui.graphicsView.setLabel('bottom', text='Wavelength [nm]')
#ui.graphicsView.setLabel('right', text='Fluorescence [Counts]')
#ui.graphicsView.setBackground('w')

### Parameters Widget ###

        self.params = [
        {'name': 'Graphics Parameters', 'type': 'group', 'children': [
        {'name': 'Legend', 'type': 'bool', 'value': False },
        {'name': 'X_axis', 'type': 'bool', 'value': True },
        {'name': 'Y(left)_axis', 'type': 'bool', 'value': True },
        {'name': 'Y(right)_axis', 'type': 'bool', 'value': False },
        {'name': 'X_min', 'type': 'int', 'value': 200 },
        {'name': 'X_max', 'type': 'int', 'value': 1000 },
        {'name': 'Line_width', 'type': 'int', 'value':1 , 'suffix': 'px' },
        {'name': 'Line_style', 'type': 'list', 'values':{"solid": None, "dashed": QtCore.Qt.DashLine, "dotted": QtCore.Qt.DotLine}, 'value': None },
        ]},
        {'name': 'Background corrections', 'type': 'group', 'children': [
        {'name': 'x_left', 'type': 'str', 'value': '600', 'limits': (200, 1000) },
        {'name': 'x_right', 'type': 'str', 'value': '800', 'limits': (200, 1000) },
        {'name': 'Apply', 'type': 'action' }
        ]},
        {'name': 'Smoothing', 'type': 'group', 'children': [
        {'name': 'Algorythm', 'type': 'list', 'values':{"none": 0, "flat": 1, "hanning": 2, "hamming": 3, "bartlett": 4, "blackman": 5}, 'value': 0},
        {'name': 'Power', 'type': 'int', 'value':1 },
        {'name': 'Apply', 'type': 'action' }
        ]},
        {'name': 'Normalization', 'type': 'group', 'children': [
        {'name': 'Algorythm', 'type': 'list', 'values':{"none": 0, "flat": 1, "hanning": 2, "hamming": 3, "bartlett": 4, "blackman": 5}, 'value': 0},
        {'name': 'Power', 'type': 'int', 'value':1 },
        {'name': 'Apply', 'type': 'action' }
        ]},
        {'name': 'Update', 'type': 'action' }
        ]

        self.p = Parameter.create(name='params', type='group', children=self.params)

        self.ui.widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ui.widget.setParameters(self.p, showTop=False)



### Parameters signals ###
 # some examples ....
    def change_legend_on_off(self):
        if legonoff.value() == True:
            self.ui.graphicsView.addLegend()
        else:
            self.ui.graphicsView.clear() # --> has to be modified to replot only selected data or to remove legend item
        #ui.graphicsView.plot()

    def change_X_axis_on_off(self):
        if X_axis.value() == False:
            self.ui.graphicsView.showLabel('bottom', show=False)
        else:
            self.ui.graphicsView.showLabel('bottom', show=True)

    def change_Y_left_axis_on_off(self):
        if Y_left_axis.value() == False:
            self.ui.graphicsView.showLabel('left', show=False)
        else:
            self.ui.graphicsView.showLabel('left', show=True)

    def change_Y_right_axis_on_off(self):
        if Y_right_axis.value() == False:
            self.ui.graphicsView.showLabel('right', show=False)
            self.ui.graphicsView.showAxis('right', show=False)
        else:
            self.ui.graphicsView.showLabel('right', show=True)
            self.ui.graphicsView.showAxis('right', show=True)

    def change_X_axis_min_max(self):
        self.ui.graphicsView.setXRange(p.param('Graphics Parameters').param('X_min').value(), self.p.param('Graphics Parameters').param('X_max').value(), padding=None, update=True)

    def change_pen_width(self):
        pen_line_width = p.param('Graphics Parameters').param('Line_width').value()
        self.ui.graphicsView.replot(pen=pen_line_width) #replot is not working
        print pen_line_width

    def change_pen_style(self):
        global pen_line_style
        pen_line_style = p.param('Graphics Parameters').param('Line_style').value()
        print pen_line_style

    def change_colorization(self):
        nPts_list = model_list.rowCount()
        colorization.getLookupTable(nPts=nPts_list) # --> should be len() of graphs that are ploted
        print colorization.getLookupTable(nPts=nPts_list)

    def load_curve(self, curve):
        curve.graph = pg.PlotDataItem(curve.data, name=curve.item.text(),
                                      pen={'color': (255, 0, 0), 'width':self.p.param('Graphics Parameters').param('Line_width').value(),
                                           'style':self.p.param('Graphics Parameters').param('Line_style').value()})
        self.on_item_changed(curve.item)  # Here I send the item not the curve

    def on_item_changed(self, item):
        """
        @param item: the one changed ! 
        """
        print("on_item_changed")
        curve = self.curves.get(str(item.text()))
        print("curve: %s" % curve)
        if curve.item.checkState() == QtCore.Qt.Checked:
            self.ui.graphicsView.addItem(curve.graph, clickable=True)
            print("Add plot %s" % curve)
        else:
            self.ui.graphicsView.removeItem(curve.graph)
            print("Removed plot %s" % curve)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeview_clicked(self, index):

        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        fileName = str(fileName)

        filePath = self.model.filePath(indexItem)
        filePath = str(filePath)

        self.clicked_spectrum.append([(fileName), (filePath)])
        print(fileName, filePath)
        curve = Curve(filePath, fileName)
        self.curves[fileName] = curve
        self.load_curve(curve)
        self.model_list.appendRow(curve.item)

    def load_selected_files(self):
    #items = self.ui.files_treeView.selectedIndexes()
    #model = QtGui.QFileSystemModel()
    #indexItem = model.index(index.row(), 0, index.parent())
    #fileName = model.fileName(indexItem)
    #fileName = str(fileName)
    #filePath = model.filePath(indexItem)
    #filePath = str(filePath)
    #item = QtGui.QStandardItem(fileName)
    #for item in items:
    #    model_list.appendRow(item)
    #print self.ui.files_treeView.selectedIndexes()
        print 'yakalelo yakalelo'

    def plot_selected_data(self):
        print 'hello'

    def save_the_graph(self):
        exporter = pg.exporters.ImageExporter.ImageExporter(ui.graphicsView.plotItem)
        exporter.parameters()['width'] = 1920
        exporter.parameters()['background'] = 'w'
        exporter.export('graphique_exporte.png')
        src = 'graphique_exporte.png'
        dst = self.ui.PathToFile_lineEdit.text() #'C:\Users\ggotthar\Desktop\graphique_exporte.png'
        shutil.move(src, dst)
        print self.ui.PathToFile_lineEdit.text(), 'is the path where you saved the graph!'

        self.p = Parameter.create(name='params', type='group', children=self.params)

        self.ui.widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ui.widget.setParameters(self.p, showTop=False)



	graph_param = self.p.param('Graphics Parameters')
	legonoff = graph_param.param('Legend')
	legonoff.sigValueChanged.connect(change_legend_on_off)

	X_axis = graph_param.param('X_axis')
	X_axis.sigValueChanged.connect(change_X_axis_on_off)

	Y_left_axis = graph_param.param('Y(left)_axis')
	Y_left_axis.sigValueChanged.connect(change_Y_left_axis_on_off)

	Y_right_axis = graph_param.param('Y(right)_axis')
	Y_right_axis.sigValueChanged.connect(change_Y_right_axis_on_off)

	Xmin = graph_param.param('X_min')
	Xmax = graph_param.param('X_max')
	Xmin.sigValueChanged.connect(change_X_axis_min_max)
	Xmax.sigValueChanged.connect(change_X_axis_min_max)

	Pen_width = graph_param.param('Line_width')
	Pen_width.sigValueChanged.connect(change_pen_width)

	Pen_style = graph_param.param('Line_style')
	Pen_style.sigValueChanged.connect(change_pen_style)

	colorization = self.ui.graphicsView_2
	colorization.sigGradientChanged.connect(change_colorization)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
##################### end of program#################




def remove_specific_graph():
    print 'stopped at remove_specific_graph'
    self.ui.graphicsView.removeItem(graph)





def plotClicked():
    print 'prout prout prout'



### Non implemented features ###
            #region = pg.LinearRegionItem(values=[600, 800], brush=None, movable=True, bounds=None)
            #ui.graphicsView.addItem(region)
#allows to add a region item on the graphicsView to select the range for baseline calculation
# check http://www.pyqtgraph.org/documentation/graphicsItems/linearregionitem.html#pyqtgraph.LinearRegionItem
# signal can be triggered

            #baseline_line = pg.InfiniteLine(pos=1.0, angle=0, pen=None, movable=True, bounds=None)
            #ui.graphicsView.addItem(baseline_line)
#allows to draw a line that could represent the newly calculated baseline or to draw slicing of kinetic curves (vertical mode)
#signal can also be triggered

#def plotClicked():
#    for i,c in enumerate(graph):
#        if c is graph:
#            c.setPen('rgb'[i], width=3)
#        else:
#            c.setPen('rgb'[i], width=1)
#    self.ui.graphicsView.addItem(graph)

#pg.plot.sigClicked.connect(plotClicked)
#add --> clickable=True when adding data
#can allow to select curves and higlight them to be manipulated

#self.ExpPar = self.TimingsPar.param('Set exposure time')
#self.FTMPar = self.TimingsPar.param('Frame Transfer Mode')
#self.HRRatePar = self.TimingsPar.param('Horizontal readout rate')
#changeExposure = lambda: self.changeParameter(self.setExposure)
#self.FTMPar.sigValueChanged.connect(changeExposure)
#self.HRRatePar.sigValueChanged.connect(changeExposure)


