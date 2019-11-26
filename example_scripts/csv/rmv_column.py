import csv
import os

from dateutil.parser import parse
from dateutil import tz
#=======================================================================================================
#SPECIFY THE DIRECTORY WHERE ALL THE COLDTUBE DATA IS STORED
#=======================================================================================================
csv_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\membrane_temp\\raw"
csv_dir2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\membrane_temp\\processed"

#=======================================================================================================
#FUNCTIONS
#=======================================================================================================
def str_is_float(strx):
    try:
        float(strx)
        return True
    except:
        return False
#=======================================================================================================
#THE DATE IS ALL IN UTC WE WILL CONVERT THEM TO SPORE LOCAL TIME
#=======================================================================================================
from_zone = tz.tzutc()
to_zone = tz.gettz("Asia/Singapore")

#=======================================================================================================
#GO THROUGH ALL THE FILES IN THE FOLDER AND RMV THE CHAOS COLUMN AND CHANGE THE DATE
#=======================================================================================================
fnames = os.listdir(csv_dir)
for fname in fnames:
    csv_path = os.path.join(csv_dir, fname)
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ",")
    csv_reader = list(csv_reader)
    nrows = len(csv_reader)
    strx = ""
    cnt = 0
    for r in csv_reader:
        if cnt == 0:
            strx += r[1] + "," + r[8] + "\n"
        
        is_float = str_is_float(r[8])
        if is_float:
            utc = parse(r[1])
            utc = utc.replace(tzinfo=from_zone)
            sporetime = utc.astimezone(to_zone)
            date_str = sporetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
            if cnt == nrows-1:
                strx += date_str  + "," + r[8]
            else:
                strx += date_str + "," + r[8] + "\n"        
        cnt+=1
    
    f.close()
    csv_path2 = os.path.join(csv_dir2, fname)
    print "*** Exporting ...", csv_path2
    f2 = open(csv_path2, "w")
    f2.write(strx)
    f2.close()