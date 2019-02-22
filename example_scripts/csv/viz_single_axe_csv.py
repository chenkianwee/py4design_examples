import csv
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
formatter = DateFormatter('%H:%M:%S')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_experiment_leftchest_flux.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_experiment_leftchest_temp.csv"
img_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\left_chest_flux_temp.png"
