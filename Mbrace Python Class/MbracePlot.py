#Program by James Curtis Addy

import Mbrace
import numpy as np
import matplotlib.pyplot as plt

filename = input("Enter file name in current folder : ")

mb_data = Mbrace.Mbrace_Data(filename)

server_timestamps = mb_data.Server_Timestamps
hour_to_seconds = server_timestamps[:, 0] * 3600.0
min_to_seconds = server_timestamps[:, 1] * 60.0
seconds = hour_to_seconds + min_to_seconds + server_timestamps[:, 2]
date_fmt = '%H:%m:%S'
#Create a base matrix filled with NaN
readingsVStime = np.full((86400, 6),np.nan)
gap_points = np.full((86400, 6),np.nan)
#For every second in the server timestamps,
#put the readings at that second into the
#readingsVStime dataset
for i in range(seconds.shape[0]):
    row_number = int(seconds[i])  
    readings = mb_data.Gape_Readings[i, :]
    readingsVStime[row_number,:] = readings

#Plot with both hours and seconds on x axis
fig, ax = plt.subplots()
step = 1/3600
hour_axis = np.arange(0, 24, step)
ax.plot(hour_axis, readingsVStime)
ax.set_ylabel("Gape Readings")
ax.set_xlabel("Hours of Day")
ax2 = ax.twiny()
ax2.plot(readingsVStime)
ax2.set_xlabel("Seconds of Day")
plt.show()



