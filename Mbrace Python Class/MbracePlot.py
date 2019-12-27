#Program by James Curtis Addy

import Mbrace
import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
from matplotlib.widgets import RadioButtons

#Get data from user specified file
filename = input("Enter file name in current folder : ")

file_date_string = re.findall(r"\d{4}-\d{2}-\d{2}", filename)[0]
file_datetime = datetime.datetime.strptime(file_date_string, '%Y-%m-%d')
mb_data = Mbrace.Mbrace_Data(filename)

#Get server timestamps in seconds
server_timestamps = mb_data.Server_Timestamps
hour_to_seconds = server_timestamps[:, 0] * 3600.0
min_to_seconds = server_timestamps[:, 1] * 60.0
seconds = hour_to_seconds + min_to_seconds + server_timestamps[:, 2]

#Create a matrix filled with NaN
readingsVStime = np.full((86400, 6),np.nan)

#For every second in the server timestamps,
#put the readings at that second into the
#readingsVStime dataset
for i in range(seconds.shape[0]):
    row_number = int(seconds[i])  
    readings = mb_data.Gape_Readings[i, :]
    readingsVStime[row_number,:] = readings

### create data
time_axis = [file_datetime + datetime.timedelta(seconds=i) for i in range(len(readingsVStime))]

#Setup plot lines
fig, ax = plt.subplots()
l1, = ax.plot(time_axis, readingsVStime[:,0], color='y')
l2, = ax.plot(time_axis, readingsVStime[:,1], visible = False, color='r')
l3, = ax.plot(time_axis, readingsVStime[:,2], visible = False, color='g')
l4, = ax.plot(time_axis, readingsVStime[:,3], visible = False, color='b')
l5, = ax.plot(time_axis, readingsVStime[:,4], visible = False, color='m')
l6, = ax.plot(time_axis, readingsVStime[:,5], visible = False, color='c')

lines = [l1,l2,l3,l4,l5,l6]

#Set title and axis labels
plt.title("Gape Readings vs. Time\n" + file_date_string)
plt.ylabel("Gape Readings")
plt.xlabel("Time")
plt.gcf().autofmt_xdate()

#Setup radio buttons
box_color = 'lightgoldenrodyellow'
radio_ax = plt.axes([.9, .2, .2, .2], facecolor = box_color)
radio = RadioButtons(radio_ax, ('1','2','3','4','5','6'))
label_dict = {'1':0, '2':1, '3':2, '4':3, '5':4, '6':5}

def set_visible_sensor(label):
    index = label_dict[label]
    for line in lines:
        line.set_visible(False)
    lines[index].set_visible(True)
    plt.draw()
    
radio.on_clicked(set_visible_sensor)

#Show plot
plt.show()



