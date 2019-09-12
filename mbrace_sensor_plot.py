##Written by James Curtis Addy

import array
import os
import math
import time
#import statistics as stat
import tkinter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#import talib as ta
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import numpy as np
#from ftplib import FTP
import ftplib
import datetime
import threading
import sys
from io import BytesIO
#from matplotlib import style

fig = plt.figure() 
    
def get_data_from_ftp_server(file_name):
    try:
        ftp = ftplib.FTP('ftp.mbrace.xyz')
        ftp.login('u305816916.datacollector','getdata')       
        data = BytesIO()
        ftp.retrbinary("RETR " + file_name ,data.write)
        data_matrix = create_byte_matrix_from_data(data)
        data.close()
        return data_matrix
    except ftplib.all_errors as e:
        print(e)  
    return None 

def create_byte_matrix_from_data(data):    
    time_stamp_period = (number_of_sensors * 10) + 8
    column_count = time_stamp_period   
    byte_matrix = array.array('B')
    byte_matrix.frombytes(data.getvalue())
    row_count = math.ceil(np.size(byte_matrix,0)/time_stamp_period)
    byte_matrix = np.asarray(byte_matrix, dtype=np.float16)
    byte_matrix = np.copy(byte_matrix)
    byte_matrix.resize(row_count,time_stamp_period)
    return byte_matrix

def get_columns_of_matrix(matrix, start_column, end_column):
    return matrix[:, (start_column-1):end_column]

def get_rows_of_matrix(matrix, start_row, end_row):
    return matrix[(start_row-1):end_row, :]

def get_millis_matrix(byte_matrix):
    return get_columns_of_matrix(byte_matrix, 3,6)

def get_sensor_matrix(byte_matrix):
    #Get every column after the 8th column
    byte_matrix = np.copy(byte_matrix[:,8:np.size(byte_matrix,1)])
    #Shape the matrix to be single row, n columns 
    byte_matrix = np.ravel(byte_matrix)    
    #Get the rows by dividing the total by the number of sensors
    row_count = math.ceil(np.size(byte_matrix)/number_of_sensors)
    byte_matrix = np.copy(byte_matrix)
    #Arrange the data to columns of data for each sensor
    byte_matrix.resize(row_count,number_of_sensors)
    return byte_matrix

def get_gape_matrix(sensor_matrix):
    return get_columns_of_matrix(sensor_matrix,1,6)

def get_temperature_matrix(sensor_matrix):
    return get_columns_of_matrix(sensor_matrix,7,7)

def converted_temp_readings(temp_matrix, degree_type = 'F'):
    converted_readings = np.ravel(temp_matrix)
    converted_readings /= 5.0
    if degree_type == 'F':
        converted_readings = (converted_readings * 1.8) + 32.0
    return converted_readings

def get_initial_gape_readings(initial_file):
    if initial_file != "none":
        byte_matrix = create_byte_matrix_from_data(initial_file)
        sensor_matrix = get_sensor_matrix(byte_matrix)
        gape_matrix = get_gape_matrix(sensor_matrix)
        return gape_matrix[0,:]
    return np.zeros(6)

def get_gape_matrix_minus_closed_position(current_gape_matrix, initial_gape_readings):
    return np.subtract(current_gape_matrix, initial_gape_readings)
              
def get_moving_average(array, window_size):
    weights = np.repeat(1.0, window_size)/window_size
    moving_average = np.convolve(array, weights, 'valid')
    return moving_average  

def get_moving_average_matrix(matrix, window_size):
    return np.apply_along_axis(get_moving_average, 0, matrix, window_size)

print("Mbrace Sensor Plot")
print("******************")

plot_line_colors = ['b','g','r','c','m','y']
server_initial_file = "something.bin"
server_file_name = "none"
local_initial_file = 'initial_readings.bin';
local_file_name = 'plot_file.bin';
number_of_sensors = 6
initial_gape_readings = np.zeros(number_of_sensors)
moving_average_window = 0
plot_is_live = False
#Using -1 to mean "all sensors"
sensor_to_plot = -1
byte_matrix = None

while True:
    print("Enter the filename of the data file (ex:84:F3:EB:B1:A2:88_2018-11-27.bin)")
    print("If file is being actively updated, the plot data will update live.")
    server_file_name = input("Enter here:")
    byte_matrix = get_data_from_ftp_server(server_file_name)
    if byte_matrix is not None: break
    
while True:
    print("\nEnter the closed values separated by space (ex: 1 2 3 4 5 6) or n for none")
    input_readings = input("Enter here:")
    if input_readings == 'n':
        initial_gape_readings = np.zeros(number_of_sensors)
        break
    try:
        input_array = [int(a) for a in input_readings.split()]
        initial_gape_readings = np.asarray(input_array)
        expected_array_length = 1
        if sensor_to_plot is -1:
            expected_array_length = number_of_sensors
        if len(initial_gape_readings) == expected_array_length:
            break
    except ValueError:
        pass
    print("The array should be n (number of sensors) integer values separated by a space.")
    
while True:
    change_window = input("\nApply a moving average?(Enter y/Y for yes):")
    if change_window == "y" or change_window == "Y":
        try:
            new_window = int(input("Enter moving average window size (must be an integer): "))
            moving_average_window = new_window
            break
        except ValueError:
            print("Moving average window must be an integer.")
    else:
        break
        
f = server_file_name.split(".")
plot_title = f[0]
d = f[0].split("_")
file_date = d[1]
dt = str(datetime.datetime.now())
cd = dt.split()
current_date = cd[0]

if current_date == file_date:
    plot_is_live = True
        
sensor_matrix = get_sensor_matrix(byte_matrix)
current_byte_size = np.size(byte_matrix, 0)

legend1 = mpatches.Patch(color='b', label = '1')
legend2 = mpatches.Patch(color='g', label = '2')
legend3 = mpatches.Patch(color='r', label = '3')
legend4 = mpatches.Patch(color='c', label = '4')
legend5 = mpatches.Patch(color='m', label = '5')
legend6 = mpatches.Patch(color='y', label = '6')

def set_plot_info():
    plt.title(plot_title + " (Moving Average Window = " + str(moving_average_window) + ")")
    plt.xlabel("Samples")
    plt.ylabel("Sample Values")
    plt.legend(handles=[legend1,legend2,legend3,legend4,legend5,legend6], bbox_to_anchor=(1,1), loc="upper left")

def set_gape_plot(sensor_matrix, initial_gape_readings, moving_average_window, sensor_to_plot): 
    #--Gape Readings--
    set_plot_info()
    gape_matrix = get_gape_matrix(sensor_matrix)
    
    gape_matrix = get_gape_matrix_minus_closed_position(gape_matrix, initial_gape_readings)
    if(moving_average_window > 0):
        gape_matrix = get_moving_average_matrix(gape_matrix, moving_average_window)
    if sensor_to_plot is -1:
        for i in range(np.size(gape_matrix,1)):
            sensor_values = gape_matrix[:,i]
            plt.plot(sensor_values,color = plot_line_colors[i], linewidth=.5)
    else:
        sensor_values = gape_matrix[:,(sensor_to_plot - 1)]
        plt.plot(sensor_values,color = plot_line_colors[sensor_to_plot - 1], linewidth=.5)

    #plt.gca().set_xlim(plt.gca().get_xlim()[0], np.size(gape_matrix,0) + 3000)
    
def set_temp_plot(sensor_matrix):
    #--Temperature Readings--
    temperature_matrix = get_temperature_matrix(sensor_matrix)
    temperature_matrix = converted_temp_readings(temperature_matrix)
    plt.plot(temperature_matrix,color = plot_line_colors[0])
    
#user_clicked will be used to pause the update so the user can more easily use the interface
user_clicked = False
ready_to_update = False

def set_terminal_display():
    if sensor_to_plot == -1:
        print("\nShowing all sensors")
    else:
        print("\nShowing sensor " + str(sensor_to_plot))
    print("Enter a value (1-6) to show an individual sensor or -1 to show all")
    print("Enter r/R to refresh (this will update the axis limits)")
    print("Enter q/Q to quit")

def get_file_thread():
    while plot_is_live:
        global current_byte_size
        global sensor_matrix
        global ready_to_update
        byte_matrix = get_data_from_ftp_server(server_file_name)       
        if current_byte_size != np.size(byte_matrix, 0):
            update_lock.acquire()
            current_byte_size = np.size(byte_matrix, 0)
            sensor_matrix = get_sensor_matrix(byte_matrix)
            ready_to_update = True
            update_lock.release()
            
def ask_user_for_command_thread():
    global sensor_to_plot
    
    while True:
        set_terminal_display()
        
        command = input("Enter here:")
        update_lock.acquire()
        if command is 'q' or command is 'Q':
            plt.close('all')
            update_lock.release()
            break
        elif command is 'r' or command is 'R':          
            fig.clear()
            set_gape_plot(sensor_matrix, initial_gape_readings, moving_average_window, sensor_to_plot)
        else:
            try:                    
                command_value = int(command)
                if command_value is -1 or (command_value > 0 and command_value <= number_of_sensors):
                    sensor_to_plot = command_value
                    fig.clear()
                    set_gape_plot(sensor_matrix, initial_gape_readings, moving_average_window, sensor_to_plot)
                else:
                    print("Only integers (1-6), -1, and q/Q are valid commands")
            except ValueError:
                print("Only integers (1-6), -1, and q/Q are valid commands")           
        update_lock.release()
              
def plot_update(i):
    global ready_to_update
    if not user_clicked:
        update_lock.acquire()
        if ready_to_update:
            ready_to_update = False              
            set_gape_plot(sensor_matrix, initial_gape_readings, moving_average_window, sensor_to_plot)
            plt.draw()
        update_lock.release()

def onclick(event):
    global user_clicked
    user_clicked = True
    
def onrelease(event):
    global user_clicked
    user_clicked = False
    
cid = fig.canvas.mpl_connect('button_press_event', onclick)
rid = fig.canvas.mpl_connect('button_release_event', onrelease)

update_lock = threading.Lock()

t = threading.Thread(target = get_file_thread)
t.daemon = True
t.start()
t2 = threading.Thread(target = ask_user_for_command_thread)
t2.daemon = True
t2.start()

set_gape_plot(sensor_matrix, initial_gape_readings, moving_average_window, sensor_to_plot)

ani = animation.FuncAnimation(fig, plot_update, interval=1000)

plt.show()

input("Press Enter to exit")
sys.exit()
        
                    
    
    

    
    




