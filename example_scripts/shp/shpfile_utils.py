# ==================================================================================================
#
#    Copyright (c) 2020, CHEN Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of gen3dcitywiz
#
#    gen3dcitywiz is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    gen3dcitywiz is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gen3dcitywiz.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import shapefile
from py4design import py3dmodel, shp2citygml, shapeattributes

#===============================================================
#READ SHPFILES
#===============================================================
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def read_sf_lines(sf_filepath):
    sf = shapefile.Reader(sf_filepath)    
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    for rec in shapeRecs:
        poly_atts=rec.record
        part_list = shp2citygml.get_geometry(rec)
        for part in part_list:
            part3d = shp2citygml.pypt_list2d_2_3d(part, 0.0)
            wire = py3dmodel.construct.make_wire(part3d)
            shpatt = shapeattributes.ShapeAttributes()
            shpatt.set_shape(wire)
            att2shpatt(shpatt, attrib_name_list, poly_atts)
            shpatt_list.append(shpatt)

    return shpatt_list

def read_sf_pt(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pts = shp2citygml.get_geometry(rec)
        if pts:
            for pt in pts:
                pypt = (pt[0], pt[1], 0.0)
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(pypt)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)

#===============================================================
#WRITE SHPFILES
#===============================================================
def write_record(shpatt_list, shp_filepath, shp_type):
    w = shapefile.Writer(shp_filepath, shapeType = shp_type)
    att_name_list = list(shpatt_list[0].dictionary.keys())
    att_name_list.remove("shape")
    n_att_name_list = []
    for name in att_name_list:
        val = shpatt_list[0].dictionary[name]
        vtype = type(val)
        if vtype == int:
            w.field(name,'N')
            n_att_name_list.append(name)
        elif vtype == float:
            w.field(name, 'N', decimal=6)
            n_att_name_list.append(name)
        elif vtype == str:
            w.field(name,'C', size=250)
            n_att_name_list.append(name)
        else:
            print('not sure what is the type going to just string it')
            w.field(name,'C', size=50)
            n_att_name_list.append(name)
            
    return w, att_name_list

def write_rec2shp(att, att_name_list, shp_writer):
    d = att.dictionary
    val_list = []
    for attname in att_name_list:
        value = d[attname]
        val_list.append(value)

    shp_writer.record(*val_list)

def write_poly_shpfile(shpatt_list, shp_filepath):
    w, att_name_list = write_record(shpatt_list, shp_filepath, 5)
    for att in shpatt_list:
        occface = att.shape
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.poly(poly_shp_list)
            
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(occface)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if is_anticlockwise:
                pyptlist.reverse()
            pyptlist2d = []
            for pypt in pyptlist:
                x = pypt[0]
                y = pypt[1]
                pypt2d = [x,y]
                pyptlist2d.append(pypt2d)
        
            w.poly([pyptlist2d])
        
        write_rec2shp(att, att_name_list, w)
        
    w.close()
    
def write_polylines_shpfile(shpatt_list, shp_filepath):
    w, att_name_list = write_record(shpatt_list, shp_filepath, 3)
    
    for att in shpatt_list:
        wire = att.shape
        vlist = py3dmodel.fetch.topo_explorer(wire, "vertex")
        occpts = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
        pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpts)
        pyptlist2d = []
        for pypt in pyptlist:
            x = pypt[0]
            y = pypt[1]
            pypt2d = [x,y]
            pyptlist2d.append(pypt2d)
    
        w.line([pyptlist2d])
        write_rec2shp(att, att_name_list, w)
        
    w.close()

def write_pt_shpfile(shpatt_list, shp_filepath):
    w, att_name_list = write_record(shpatt_list, shp_filepath, 1)
    
    for att in shpatt_list:
        pypt = att.shape
        w.point(pypt[0], pypt[1])
        write_rec2shp(att, att_name_list, w)
        
    w.close()
    
def shp2shpatt(occshape, att_d):
    shpatt = shapeattributes.ShapeAttributes()
    shpatt.set_shape(occshape)
    
    for key, val in att_d.items():
        shpatt.set_key_value(key, val)
    
    return shpatt