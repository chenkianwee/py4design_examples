import shpfile_utils
from py4design import shapeattributes
import numpy as np 


def clean_up_att(val_str):
    val_list = val_str.split(':')
    uniq = np.unique(val_list)
    strx = ''
    for cnt, u in enumerate(uniq):
        if u != 'yes':
            if cnt == 0:
                strx = str(u)
            else:
                if strx == '':
                    strx = str(u)
                else:
                    strx = strx + ':' + str(u)
    
    return strx

shpfile = 'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_roadline\\pu_main_roadline.shp'
shpfile2 = 'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_roadline\\pu_main_roadline1.shp'
shpatts = shpfile_utils.read_sf_lines(shpfile)

new_atts = []
for att in shpatts:
    name1 = att.get_value('name')
    name2 = att.get_value('PRIME_NAME')
    if name2:
        name = name2
    else:
        name = name1
    
    type1 = att.get_value('highway')
    if type1:
        typex = type1
    else:
        typex = 'road'
        
    new_att = shapeattributes.ShapeAttributes()
    new_att.set_shape(att.shape)
    new_att.set_key_value('rd_name', name)
    new_att.set_key_value('rd_type', typex)
    new_atts.append(new_att)
    
shpfile_utils.write_polylines_shpfile(new_atts, shpfile2)
