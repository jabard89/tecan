#!/usr/bin/env python
#Jared Bard 2019-01-14
#Script to process tecan data into tidy_data
#Written for python 3.7
#Export to ascii file settings: Decimal = point, Delimiter = Tabulator, Encoding = Unicode
#export options: Direction=horizontal, result=matrix(separated)
#insert data names=yes, add kinetic time stamps=yes, add temperatures=yes
#date/time of measurement=yes,filter wavelength=yes, measurement params=yes
#usage: python asc_to_tidy_96well.py n_channels filepath
#usage example: 'python asc_to_tidy_96well.py 1 190129-1.asc'

#For a different plates size, chance the n_rows and n_cols appropriately


import sys
import os
import numpy as np
import csv
import pathlib
n_rows = 8
n_cols = 12

def main():
	# This basic command line argument parsing code is provided.
	# Add code to call your functions below.

	# Make a list of command line arguments, omitting the [0] element
	# which is the script itself.
	args = sys.argv[1:]
	if not args:
		print('ERROR! Usage: n_channels filepath')
		sys.exit(1)
	elif len(args) > 2:
		print('ERROR! Usage: n_channels filepath')
		sys.exit(1)
		
	try:
		n_channels = int(args[0])
	except:
		print('ERROR! Usage: n_channels filepath')
		sys.exit(1)
		
	filename = pathlib.Path(args[1])
	if filename.suffix != '.asc':
		print('ERROR! Please provide a .asc file')
		sys.exit(1)
	
	#initalize storage variables
	block_size = n_rows + 2
	channels = [] # names of channels
	time = [] # all of the time stamps
	data = [] #list of each matrix of data
	temperature = [] # list of all temperatures
	date = ''
	start_time = ''

	with open(filename, 'rt',encoding='utf-16') as f:
		for line_num, line in enumerate(f):
			line = line.strip('\n')
			columns = line.split('\t')
			
			c1 = columns[0]
			if c1: #look for the measurement parameters
				first_word = c1.split()[0]
				if first_word == 'Date':
					date = c1.split()[3][0:10]
					start_time = c1.split()[6]
					break
					
			block_i = (line_num - n_channels) % block_size
			if line_num == n_channels:
				if columns[0] != '0s':
					print('ERROR! Possibly the number of channels is incorrect.')
					sys.exit(1)
			if line_num < n_channels: #the first few lines are the names of the channels
				channels.append(columns[0])        
			elif block_i == 0:
				time.append(columns[0][0:-1]) #removes the trailing s        
				data_temp = np.zeros((n_rows,n_cols),dtype = np.float_) #initialze the data array for this block
			elif block_i == 1:
				temperature.append(columns[0].split(' ')[0]) #extract just the number
			elif block_i > 1:
				row_i = block_i - 2 #which row of the data are we in
				for column_i,c in enumerate(columns):
					if c:
						data_temp[row_i,column_i] = float(c)
				if block_i == (block_size - 1): #for the last row, add the matrix to the list of all data
					data.append(data_temp)
	#Determine how many measurements were made
	n_measurements = divmod(len(data),n_channels)[0]
	measured_wells_i = np.transpose(np.nonzero(data[0][:,:])) #extract the locations of all non-zero measurements
	alphabet = ('A','B','C','D','E','F','G','H','I')
	measured_wells = []

	for well_i in measured_wells_i:
		alpha_i = well_i[0]
		num_i = well_i[1]
		measured_wells.append(alphabet[alpha_i]+str(num_i+1)) #creates a list of which wells were measured
		
	# Goal is to make a table in tidy format. Go through each channel
	# Extract the correct time, temp and value, and assign to a list
	col_headers = ('Well', 'Time(s)', 'Temp(C)', 'Channel', 'Value','Date','Start_Time')
	tidy_data = [col_headers]
	for which_channel, channel in enumerate(channels):
		for which_well, well_i in enumerate(measured_wells_i):
			for which_read in range(n_measurements):
				read_index = which_channel*n_measurements+which_read
				value_temp = data[read_index][well_i[0],well_i[1]]
				time_temp = time[read_index]
				temperature_temp = temperature[read_index]
				well_temp = measured_wells[which_well]
				tidy_data.append([well_temp,time_temp,temperature_temp,
									channel,value_temp,date,start_time])
		
	file_to_write = filename.parent / (filename.name[0:-4] + '.csv')
	with open(file_to_write, 'w',newline='') as f:
		writer = csv.writer(f)
		writer.writerows(tidy_data)
	print('Output file = ',end='')
	print(file_to_write)
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

	


	
	
	
