# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window_resizable_GG.ui'
#
# Created: Mon Nov 24 14:48:27 2014
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1314, 894)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.spectra_splitter = QtGui.QSplitter(self.centralwidget)
        self.spectra_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.spectra_splitter.setObjectName(_fromUtf8("spectra_splitter"))
        self.gridLayoutWidget = QtGui.QWidget(self.spectra_splitter)
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.listView = QtGui.QListView(self.gridLayoutWidget)
        self.listView.setMaximumSize(QtCore.QSize(300, 16777215))
        self.listView.setObjectName(_fromUtf8("listView"))
        self.gridLayout_2.addWidget(self.listView, 1, 0, 1, 1)
        self.files_treeView = QtGui.QTreeView(self.gridLayoutWidget)
        self.files_treeView.setMaximumSize(QtCore.QSize(300, 16777215))
        self.files_treeView.setObjectName(_fromUtf8("files_treeView"))
        self.gridLayout_2.addWidget(self.files_treeView, 0, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = ParameterTree(self.gridLayoutWidget)
        self.widget.setMinimumSize(QtCore.QSize(250, 600))
        self.widget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout.addWidget(self.widget)
        self.graphicsView_2 = GradientWidget(self.gridLayoutWidget)
        self.graphicsView_2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.graphicsView_2.setObjectName(_fromUtf8("graphicsView_2"))
        self.verticalLayout.addWidget(self.graphicsView_2)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 2, 2, 1)
        self.graphicsView = PlotWidget(self.gridLayoutWidget)
        self.graphicsView.setMinimumSize(QtCore.QSize(800, 400))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 1, 2, 1)
        self.verticalLayout_3.addWidget(self.spectra_splitter)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 30, 30, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.load_pushButton = QtGui.QPushButton(self.centralwidget)
        self.load_pushButton.setObjectName(_fromUtf8("load_pushButton"))
        self.horizontalLayout_2.addWidget(self.load_pushButton)
        self.unload_pushButton = QtGui.QPushButton(self.centralwidget)
        self.unload_pushButton.setObjectName(_fromUtf8("unload_pushButton"))
        self.horizontalLayout_2.addWidget(self.unload_pushButton)
        self.plot_pushButton = QtGui.QPushButton(self.centralwidget)
        self.plot_pushButton.setObjectName(_fromUtf8("plot_pushButton"))
        self.horizontalLayout_2.addWidget(self.plot_pushButton)
        self.PathToFile_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.PathToFile_lineEdit.setObjectName(_fromUtf8("PathToFile_lineEdit"))
        self.horizontalLayout_2.addWidget(self.PathToFile_lineEdit)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1314, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuParameters = QtGui.QMenu(self.menubar)
        self.menuParameters.setObjectName(_fromUtf8("menuParameters"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        self.menuAnalysis = QtGui.QMenu(self.menubar)
        self.menuAnalysis.setObjectName(_fromUtf8("menuAnalysis"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionEdit_All = QtGui.QAction(MainWindow)
        self.actionEdit_All.setObjectName(_fromUtf8("actionEdit_All"))
        self.actionColorization = QtGui.QAction(MainWindow)
        self.actionColorization.setObjectName(_fromUtf8("actionColorization"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionCorrections = QtGui.QAction(MainWindow)
        self.actionCorrections.setObjectName(_fromUtf8("actionCorrections"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionQuit)
        self.menuParameters.addAction(self.actionEdit_All)
        self.menuParameters.addAction(self.actionColorization)
        self.menuAbout.addAction(self.actionAbout)
        self.menuAnalysis.addAction(self.actionCorrections)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAnalysis.menuAction())
        self.menubar.addAction(self.menuParameters.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionCorrections, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.show)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "SpeCuBE - Analysis", None))
        self.load_pushButton.setText(_translate("MainWindow", "load", None))
        self.unload_pushButton.setText(_translate("MainWindow", "unload", None))
        self.plot_pushButton.setText(_translate("MainWindow", "plot", None))
        self.pushButton_2.setText(_translate("MainWindow", "Save Graph", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuParameters.setTitle(_translate("MainWindow", "Parameters", None))
        self.menuAbout.setTitle(_translate("MainWindow", "Help", None))
        self.menuAnalysis.setTitle(_translate("MainWindow", "Analysis", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionEdit_All.setText(_translate("MainWindow", "Edit All", None))
        self.actionColorization.setText(_translate("MainWindow", "Colorization", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionCorrections.setText(_translate("MainWindow", "Corrections", None))

from pyqtgraph import GradientWidget, PlotWidget
from pyqtgraph.parametertree import ParameterTree

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

