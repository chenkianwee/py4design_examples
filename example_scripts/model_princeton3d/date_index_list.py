import json

from datetime import timedelta
from dateutil.parser import parse
from dateutil import tz

td = timedelta(hours=8760)

str_sp_date = str(2019) + "-" + str(1) + "-" + str(1) + "-" +\
                str(0) + ":" + str(0) + ":" + str(0)
                        
str_ep_date = str(2019) + "-" + str(12) + "-" + str(31) + "-" +\
                str(23) + ":" + str(0) + ":" + str(0)
                
print str_ep_date
date1 = parse(str_sp_date)
#zone = tz.gettz()
#date1 = date1.replace(tzinfo=zone)

date2 = parse(str_ep_date)
#zone = tz.gettz()
#date = date.replace(tzinfo=zone)
td2 = date2-date1
hours = td2.total_seconds()
print hours/3600