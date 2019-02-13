import shapefile
import uuid
import datetime

import numpy as np

import PyQt5
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
from lxml.etree import Element, ElementTree,  SubElement, tostring
import os, sys


class RelativityGUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupGUI()
        
        self.objectGroup = ShapefileGroup(self)
        self.params = Parameter.create(name='ParmX', type='group', children=[self.objectGroup, dict(name='Build Citygml', type='action'), dict(name='Save Citygml', type='action')])
        self.tree.setParameters(self.params, showTop=False)
        self.params.param('Save Citygml').sigActivated.connect(self.save_citygml)
        self.params.param('Build Citygml').sigActivated.connect(self.build_citygml)
        
    def setupGUI(self):
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        self.tree = ParameterTree(showHeader=False)
        self.splitter.addWidget(self.tree)

        self.view3d = gl.GLViewWidget()
        #self.view3d.opts['distance'] = 10000
        
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

    def build_citygml(self):
        shptype = self.objectGroup.param('Shapefile').param("Type").value()
        filename = self.objectGroup.param('Shapefile').param("Shapefile Loaded").value()
        sf = shapefile.Reader(filename)
        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType

        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType
        #shapetype 3 is polyline, shapetype 5 is polygon
        
        display, start_display, add_menu, add_function_to_menu = init_display(backend_str="wx")
        
        count_shapes = 0
        for rec in shapeRecs:
            shape=rec.shape
            if shapetype == 5:
                #A ring is a connected sequence of four or more
                #points that form a closed, non-self-intersecting loop
                #The rings of a polygon are referred to as its parts
                parts=shape.parts
                num_parts=len(parts)
                points=shape.points
                #=======================================================================================================
                #part is a surface in each landuse
                #=======================================================================================================
                count_parts=0
                for part in parts:
                    part_s = parts[count_parts]
                    if count_parts==num_parts-1:
                        part_e=len(points)
                    else:
                        part_e=parts[count_parts+1]
                    part_points=points[part_s:part_e]
                    #=======================================================================================================
                    
                    pt_array = []
                    count_points = 0
                    for point in part_points:
                        gp_pt = gp_Pnt(point[0], point[1], 0)
                        pt_array.append(gp_pt)
                        count_points+= 1
                        
                    poly = BRepBuilderAPI_MakePolygon()
                    map(poly.Add, pt_array)
                    poly.Build()
                    poly.Close()
                    wire = poly.Wire()
                    shape = BRepBuilderAPI_MakeFace(wire).Shape()
                    
                    display.DisplayShape(shape, update=True)
                    
                    brepmesh_Mesh(shape, 0.8)
                    builder = BRep_Builder()
                    comp = TopoDS_Compound()
                    builder.MakeCompound(comp)
                    ex = TopExp_Explorer(shape, TopAbs_FACE)
                    
                    while ex.More():
                        face = topods_Face(ex.Current())
                        location = TopLoc_Location()
                        facing = (BRep_Tool_Triangulation(face, location)).GetObject()
                        tabs = facing.Nodes()
                        tris = facing.Triangles()
                        tpt_array = []
                        index_array = []
                        
                        for t in range (1, tabs.Length() + 1):
                            tx = tabs.Value(t).X()
                            ty = tabs.Value(t).Y()
                            tz = tabs.Value(t).Z()
                            tpt = [tx,ty,tz]
                            tpt_array.append(tpt)
                            
                        for i in range(1, facing.NbTriangles()+1):
                            tri = tris.Value(i)
                            index = [tri.Get()[0]-1,tri.Get()[1]-1,tri.Get()[2]-1]
                            index_array.append(index)

                        
                        verts = np.array(tpt_array)
                        print verts
                        mfaces = np.array(index_array)
                        m1 = gl.GLMeshItem(vertexes=verts, faces=mfaces, smooth=False)
                        #m1.setGLOptions('additive')
                        #self.view3d.addItem(m1)
                        ex.Next()
                        
                    count_parts+=1
                    #=======================================================================================================
    
                count_shapes += 1
        start_display()
        print "done"

    def save_citygml(self):
        fn = str(pg.QtGui.QFileDialog.getSaveFileName(self, "Save State..", "untitled.gml", "Citygml (*.gml)"))
        if fn == '':
            return
        
        shptype = self.objectGroup.param('Shapefile').param("Type").value()
        filename = self.objectGroup.param('Shapefile').param("Shapefile Loaded").value()
        
        schemaLocation="http://www.opengis.net/citygml/landuse/1.0\
                        http://schemas.opengis.net/citygml/landuse/1.0/landUse.xsd http://www.opengis.net/citygml/cityfurniture/1.0\
                        http://schemas.opengis.net/citygml/cityfurniture/1.0/cityFurniture.xsd http://www.opengis.net/citygml/appearance/1.0\
                        http://schemas.opengis.net/citygml/appearance/1.0/appearance.xsd http://www.opengis.net/citygml/texturedsurface/1.0\
                        http://schemas.opengis.net/citygml/texturedsurface/1.0/texturedSurface.xsd http://www.opengis.net/citygml/transportation/1.0\
                        http://schemas.opengis.net/citygml/transportation/1.0/transportation.xsd http://www.opengis.net/citygml/waterbody/1.0\
                        http://schemas.opengis.net/citygml/waterbody/1.0/waterBody.xsd http://www.opengis.net/citygml/building/1.0\
                        http://schemas.opengis.net/citygml/building/1.0/building.xsd http://www.opengis.net/citygml/relief/1.0\
                        http://schemas.opengis.net/citygml/relief/1.0/relief.xsd http://www.opengis.net/citygml/vegetation/1.0\
                        http://schemas.opengis.net/citygml/vegetation/1.0/vegetation.xsd http://www.opengis.net/citygml/cityobjectgroup/1.0\
                        http://schemas.opengis.net/citygml/cityobjectgroup/1.0/cityObjectGroup.xsd http://www.opengis.net/citygml/generics/1.0\
                        http://schemas.opengis.net/citygml/generics/1.0/generics.xsd"
        
        if shptype == 'Plots':
            root = Element("CityModel",
               attrib={"{" + XMLNamespaces.xsi + "}schemaLocation" : schemaLocation},
               nsmap={None:"http://www.opengis.net/citygml/1.0",
                      'xsi':XMLNamespaces.xsi,
                      'trans':XMLNamespaces.trans,
                      'wtr': XMLNamespaces.wtr,
                      'gml': XMLNamespaces.gml,
                      'smil20lang': XMLNamespaces.smil20lang,
                      'xlink': XMLNamespaces.xlink,
                      'grp': XMLNamespaces.grp,
                      'luse': XMLNamespaces.luse,
                      'frn': XMLNamespaces.frn,
                      'app': XMLNamespaces.app,
                      'tex': XMLNamespaces.tex,
                      'smil20': XMLNamespaces.smil20,
                      'xAL': XMLNamespaces.xAL,
                      'bldg': XMLNamespaces.bldg,
                      'dem': XMLNamespaces.dem,
                      'veg': XMLNamespaces.veg,
                      'gen': XMLNamespaces.gen})

            et = ElementTree(root)
            cityObjectMember = SubElement(root,'cityObjectMember')
            sf = shapefile.Reader(filename)

            shapeRecs=sf.shapeRecords()
            shapetype = shapeRecs[0].shape.shapeType

            shapeRecs=sf.shapeRecords()
            shapetype = shapeRecs[0].shape.shapeType
            #shapetype 3 is polyline, shapetype 5 is polygon

            count_shapes = 0
            for rec in shapeRecs:
               shape=rec.shape
               if shapetype == 5:
                  #A ring is a connected sequence of four or more
                  #points that form a closed, non-self-intersecting loop
                  #The rings of a polygon are referred to as its parts
                  parts=shape.parts
                  num_parts=len(parts)
                  points=shape.points

                  luse = SubElement(cityObjectMember, "{" + XMLNamespaces.luse+ "}" +'LandUse')
                  luse.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'plot' + str(count_shapes)

                  gml_name = SubElement(luse, "{" + XMLNamespaces.gml+ "}" + 'name')
                  gml_name.text = 'simpleplot' + str(count_shapes)

                  gml_boundedBy = SubElement(luse, "{" + XMLNamespaces.gml+ "}" + 'boundedBy')

                  gml_Envelope = SubElement(gml_boundedBy, "{" + XMLNamespaces.gml+ "}" + 'Envelope')
                  #gml_Envelope.attrib['srsDimension'] = '3'
                  #gml_Envelope.attrib['srsName'] = 'urn:ogc:def:crs,crs:EPSG:6.12:3068,crs:EPSG:6.12:5783'

                  gml_lowerCorner = SubElement(gml_Envelope, "{" + XMLNamespaces.gml+ "}" + 'lowerCorner')
                  gml_upperCorner = SubElement(gml_Envelope,"{" + XMLNamespaces.gml+ "}" + 'upperCorner')

                  creationDate = SubElement(luse, 'creationDate')
                  creationDate.text = str(datetime.datetime.now())

                  luse_lod1MultiSurface = SubElement(luse, "{" + XMLNamespaces.luse+ "}" + 'lod1MultiSurface')

                  gml_MultiSurface = SubElement(luse_lod1MultiSurface, "{" + XMLNamespaces.gml+ "}" + 'MultiSurface')
                  gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())
                  #=======================================================================================================
                  #attrib of each land parcel
                  #=======================================================================================================
                  poly_attribs=rec.record
                  plot_ratio = poly_attribs[1]
                  landusefunction = poly_attribs[2]

                  luse_function = SubElement(luse, "{" + XMLNamespaces.luse+ "}" +'function')
                  if landusefunction == "residential":
                     luse_function.text = "1010"

                  else:
                     luse_function.text = "1020"

                  gen_plot_ratio = SubElement(luse, "{" + XMLNamespaces.gen + "}" +'doubleAttribute')
                  gen_plot_ratio.attrib['name'] = 'plot ratio'

                  gen_value = SubElement(gen_plot_ratio, "{" + XMLNamespaces.gen + "}" +'value')
                  gen_value.text = str(plot_ratio)
                  
                  
                  #=======================================================================================================
                  #part is a surface in each landuse
                  #=======================================================================================================
                  count_parts=0
                  for part in parts:
                     part_s = parts[count_parts]
                     if count_parts==num_parts-1:
                         part_e=len(points)
                     else:
                         part_e=parts[count_parts+1]
                         
                     part_points=points[part_s:part_e]
                     #=======================================================================================================
                     gml_surfaceMember = SubElement(gml_MultiSurface, "{" + XMLNamespaces.gml+ "}" + 'surfaceMember')

                     gml_Polygon = SubElement(gml_surfaceMember,"{" + XMLNamespaces.gml+ "}" + 'Polygon')
                     gml_Polygon.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

                     gml_exterior = SubElement(gml_Polygon, "{" + XMLNamespaces.gml+ "}" + 'exterior')

                     gml_LinearRing = SubElement(gml_exterior, "{" + XMLNamespaces.gml+ "}" + 'LinearRing')
                     gml_LinearRing.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

                     gml_posList = SubElement(gml_LinearRing, "{" + XMLNamespaces.gml+ "}" + 'posList')
                     gml_posList.attrib['srsDimension'] = '3'

                     position = ""
                     count_points = 0
                     for point in part_points:
                         if count_points == 0:
                             position=position + str(point[0]) + " " + str(point[1]) + " 0"
                         else:
                             position=position + " " + str(point[0]) + " " + str(point[1]) + " 0"
                         count_points+= 1

                     gml_posList.text = position
                     count_parts+=1
                     #=======================================================================================================
                     count_shapes += 1

            outFile = open(fn, 'w')
            et.write(outFile,pretty_print = True, xml_declaration = True, encoding="UTF-8", standalone="yes")
            outFile.close()
            print "done"


class ShapefileGroup(pTypes.GroupParameter ):
    def __init__(self, qtwidget, **kwds):
        defs = dict(name="Shapefiles", addText="Add Shapefile")
        pTypes.GroupParameter.__init__(self, **defs)
        self.restoreState(kwds, removeChildren=False)
        self.qtwidget = qtwidget
        self.no_shapefiles = 1
        
    def addNew(self):
        shapefile = Parameter.create(name='Shapefile', autoIncrementName=True, type=None, renamable=True, removable=True, children=[
            dict(name = 'Type', type = "list", values =["","Plots", "Building", "Roads&Rails", "Bus&Rail Stations"]),
            dict(name='Load Shapefile', type='action'),
            dict(name =  'Shapefile Loaded', type = 'str', value = "", readonly = True)
            ])
        
        self.addChild(shapefile)
        
        if self.no_shapefiles == 1:
            self.param('Shapefile').param('Load Shapefile').sigActivated.connect(self.load)
        else:
            self.param('Shapefile' + str(self.no_shapefiles)).param('Load Shapefile').sigActivated.connect(self.load)

        self.no_shapefiles+=1
        
    def load(self):
        fn = str(pg.QtGui.QFileDialog.getOpenFileName(self.qtwidget, "Load Shapefile", "", "Shapefile (*.shp)"))
        self.param('Shapefile').param('Shapefile Loaded').setValue(fn)
        
        if fn == '':
            return
        
pTypes.registerParameterType('ShapefileGroup', ShapefileGroup)

class XMLNamespaces:
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    trans="http://www.opengis.net/citygml/transportation/1.0"
    wtr = "http://www.opengis.net/citygml/waterbody/1.0"
    gml = "http://www.opengis.net/gml"
    smil20lang = "http://www.w3.org/2001/SMIL20/Language"
    xlink = "http://www.w3.org/1999/xlink"
    grp = "http://www.opengis.net/citygml/cityobjectgroup/1.0"
    luse = "http://www.opengis.net/citygml/landuse/1.0"
    frn="http://www.opengis.net/citygml/cityfurniture/1.0"
    app="http://www.opengis.net/citygml/appearance/1.0"
    tex="http://www.opengis.net/citygml/texturedsurface/1.0"
    smil20="http://www.w3.org/2001/SMIL20/"
    xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
    bldg="http://www.opengis.net/citygml/building/1.0"
    dem="http://www.opengis.net/citygml/relief/1.0"
    veg="http://www.opengis.net/citygml/vegetation/1.0"
    gen="http://www.opengis.net/citygml/generics/1.0"

#=====================================================================================================================================================================================================================
if __name__ == '__main__':
    pg.mkQApp()
    win = RelativityGUI()
    win.setWindowTitle("Shape2Citygml")
    win.show()
    win.resize(1100,700)
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        
