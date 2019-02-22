import csv
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
formatter = DateFormatter('%H:%M:%S')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_experiment_leftchest_flux.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_experiment_leftchest_temp.csv"
img_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\left_chest_flux_temp.png"
#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
def csv2plot(csv_path):
    x_list = []
    y_list = []
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ",")
    csv_list = list(csv_reader)
    
    xmin = parse(csv_list[1][0])
    xmax = parse(csv_list[-1][0])
    cnt = 0
    for r in csv_list:
        if cnt!=0:
            x = parse(r[0])
            y = float(r[1])
            x_list.append(x)
            y_list.append(y)
        cnt+=1
        
    f.close()
    return x_list, y_list, xmin, xmax

#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
x_list1, y_list1, xmin, xmax = csv2plot(csv_path)
x_list2, y_list2, xmin, xmax = csv2plot(csv_path2)

fig, ax1 = plt.subplots()
ax1.plot(x_list1, y_list1, 'b-')
ax1.set_xlabel('time')
#ax1.set_ylim(-40, 70)
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('Watts ($W/m^2$)', color='b')
ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
ax2.plot(x_list2, y_list2, 'r-')
ax2.set_ylabel('Degree($^oC$)', color='r')
ax2.tick_params('y', colors='r')

fig.tight_layout()
ax1.xaxis.set_major_formatter(formatter)
plt.title("Left Chest", fontsize=10 )
plt.xlim(xmin, xmax) 

# beautify the x-labels
plt.gcf().autofmt_xdate()
plt.savefig(img_path, dpi = 300,transparent=True,papertype="a3")
plt.show()

plt.show()