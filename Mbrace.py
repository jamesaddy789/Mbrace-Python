import numpy as np
from scipy import stats
import re

class Mbrace_Data:
    Timestamps = None
    Gape_Readings = None
    Temperature_Readings = None
    
    def __init__(self, filename):
        #Collect the bytes of data from the bin files
        byte_array = []
        with open(filename, 'rb') as d:
            byte_array = d.read()
        
        #Create a list of start indices for where the timestamp expressions are found
        regex = b"@@.{4}##"
        regex_match_list = re.finditer(regex, byte_array, re.DOTALL) #Dotall also counts bytes above 128
        regex_start_indices = []
        for m in regex_match_list:
            regex_start_indices.append(m.span()[0])


        #Get the most frequently occuring sequence length.
        sequence_lengths = [regex_start_indices[i + 1] - regex_start_indices[i] for i in range(0,len(regex_start_indices)-1)]
        sequence_lengths.append(len(byte_array) - regex_start_indices[len(regex_start_indices) - 1])
        expected_sequence_length = stats.mode(sequence_lengths)[0][0]
        #Create a list of indices that are the expected length apart
        sequence_start_indices = []
        for i in range(0, len(sequence_lengths)):
            if sequence_lengths[i] == expected_sequence_length:
                sequence_start_indices.append(regex_start_indices[i])

        #Create a numpy array from the byte array by converting the bytes into unsigned 8 bit integers
        np_bytes = np.frombuffer(byte_array,dtype=np.uint8)

        #Initialize a n-dimensional numpy array using the number of valid sequences as rows and the expected sequence length as columns
        row_count = len(sequence_start_indices)
        column_count = expected_sequence_length
        np_matrix = np.zeros((row_count, column_count), dtype=np.uint8)

        #Fill the numpy matrix with the data
        for i in range(0, row_count):
            start = sequence_start_indices[i]
            end = start + expected_sequence_length
            #Modify the ith row of the matrix to be the corresponding sequence from the numpy byte array
            np_matrix[i] = np_bytes[start : end]

        #Get timestamps
        timestamps_as_bytes = np_matrix[:,2:6]
        #Convert timestamp values to decimal
        self.Timestamps = np.zeros((timestamps_as_bytes.shape[0], 1), dtype = np.uint32)
        for i in range(0,self.Timestamps.shape[0]):
            shift_24 = np.uint32(timestamps_as_bytes[i, 0]) << 24
            shift_16 = np.uint32(timestamps_as_bytes[i, 1]) << 16
            shift_8 = np.uint32(timestamps_as_bytes[i, 2]) << 8
            shift_0 = np.uint32(timestamps_as_bytes[i, 3])
            combined = shift_24 | shift_16 | shift_8 | shift_0
            self.Timestamps[i, 0] = combined
        
        #Set up sensor reading matrices
        sensor_readings = np_matrix[:, 8:end]     
        sensor_count = int(sensor_readings.shape[1]/10)      
        try:
            sensor_readings = sensor_readings.reshape(row_count*10, sensor_count)
        except(ValueError):
            print("Error reshaping values for " + filename)
            return
        #Average the sensor data 10 times
        times_averaged = 10
        averaged_row_count = int(sensor_readings.shape[0] / times_averaged)
        averaged_matrix = np.zeros((averaged_row_count, sensor_count))
        for i in range(0,averaged_row_count):
            submatrix_to_avg = sensor_readings[i:i+times_averaged, :]
            averaged_submatrix = np.mean(submatrix_to_avg, axis = 0)
            averaged_matrix[i] = averaged_submatrix
        sensor_readings = averaged_matrix
        self.Gape_Readings = sensor_readings[:, 0:6]
  
        #Set up temperature readings if available        
        if sensor_count == 7:
            self.Temperature_Readings = sensor_readings[:,6] / 5

              





    


    
    









