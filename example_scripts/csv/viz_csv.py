import csv
from dateutil.parser import parse

from py4design import pyoptimise

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox2\\coldtube_blue_tank_tankt.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox2\\coldtube_blue_tank_tankreturnt.csv"
img_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\chaosbox2\\coldtube_blue_tank_tankt.png"
#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
def csv2plot(csv_path, pt_list, colour_list, pt_area_list, colour):
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ",")
    cnt = 0
    for r in csv_reader:
        if cnt!=0:
            pt = [parse(r[0]), float(r[1])]
            pt_list.append(pt)
            colour_list.append(colour)
            pt_area_list.append(1)
        cnt+=1
        
    f.close()
#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
    
colour_list = []
pt_area_list = []
pt_list = []
    
csv2plot(csv_path, pt_list, colour_list, pt_area_list, "blue")
csv2plot(csv_path2, pt_list, colour_list, pt_area_list, "red")

pyoptimise.draw_graph.scatter_plot(pt_list, colour_list, pt_area_list, savefile = img_path)