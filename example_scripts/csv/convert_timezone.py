from dateutil.parser import parse
from dateutil import tz
from datetime import timedelta


from_zone = tz.tzutc()
to_zone = tz.gettz("Asia/Singapore")

utc = parse('2019-01-14T15:58:56.6Z')
utc = utc.replace(tzinfo=from_zone)
sporetime = utc.astimezone(to_zone)
dstr = sporetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
stime = parse(dstr)
print utc, sporetime, stime