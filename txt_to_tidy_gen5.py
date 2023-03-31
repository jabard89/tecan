#!/usr/bin/env python
# Jared Bard 2023-03-21
# Adapted from asc_to_tidy_384well.py
# Script to process biotek data into tidy_data
# Export to text file settings: 
# usage: python txt_to_tidy_gen5.py filein channel1 channel2 ...
# example: python txt_to_tidy_gen5.py /home/jabard89/Dropbox/Data_JB/Plate/Human/230321/230321-read1.txt 485,528
import sys
import os
import numpy as np
import pandas as pd
import csv
import pathlib

def get_sec(time_str):
		#Get seconds from time
		# courtesy of https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
		h, m, s = time_str.split(':')
		return int(h) * 3600 + int(m) * 60 + int(s)

def main():
	# This basic command line argument parsing code is provided.
	# Add code to call your functions below.

	# Make a list of command line arguments, omitting the [0] element
	# which is the script itself.
	args = sys.argv[1:]
	if not args:
		print('ERROR! Usage: exportfile channel1 channel2 ...')
		sys.exit(1)
	elif len(args) < 2:
		print('ERROR! Usage: exportfile channel1 channel2 ...')
		sys.exit(1)


	filein = pathlib.Path(args[0])
	channels = args[1:]
	
	#debug
	#channels = ["485,528"]
	#fileout = pathlib.Path("/home/jabard89/Dropbox/Data_JB/Plate/Human/230321/230321-read1.txt")
	
	channel_i = 0 # start off with the first channel
	channel_flag = 0
	skip_flag = 0 # flag to skip the next line
	data_out = [] # list of dataframes for each read

	with open(filein,'rt',encoding="latin-1") as f:
		for line_num,line in enumerate(f):
			if skip_flag:
				skip_flag = 0
				continue

			line = line.strip('\n')

			if channel_flag:
				if not line: # export the channel data						
					channel_flag = 0
					channel_i += 1
					if channel_i == len(channels):
						break # we found all the channels!
					continue

			if line:  # look for the measurement parameters
				first_word = line.split()[0]
				if first_word == channels[channel_i]:
					temp_channel = channels[channel_i]
					channel_flag = 1 # found the channel
					skip_flag = 1 # skip the next line
					data_temp = [] # list of dictionaries for each read
					continue
				if channel_flag:
					column = line.split('\t')
					if column[0] == 'Time':
						wells = column[2:]
						continue
					else:
						read_out = pd.DataFrame(list(zip(wells,column[2:])),columns=['Well','Value'])
						read_out['Value'].replace('', np.nan, inplace=True)
						read_out = read_out.dropna(subset=['Value'])
						read_out['Time_s'] =  get_sec(column[0])
						read_out['Temp_C'] = column[1]
						read_out['Channel'] = temp_channel
						data_out.append(read_out)
	
	file_to_write = filein.parent/(filein.name[0:-4] + '.csv')
	export = pd.concat(data_out,axis=0,ignore_index=True).to_csv(file_to_write,index=False)


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
	main()
