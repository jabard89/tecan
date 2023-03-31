"""
Created on 2/21/2022
Modified 8/11/2022
@author: Jared Bard
Script for pulling data from excel timecourse data from Tecan Spark
should be channel agnostic
adapted to deal with matrix format
need to install openpyxl (on ubuntu: conda install openpyxl)
"""

import sys, os, math, random, argparse, csv
from datetime import datetime
import pandas as pd
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generate options")
	# Required arguments
	parser.add_argument(dest="input",default=None,type=str,help="input excel file")
	parser.add_argument(dest="output_file",default=None,type=str,help="file to export tsv data to")
	args = parser.parse_args()
	# args = parser.parse_args(["/home/jabard89/Dropbox/Data_JB/Plate/Luminescence/220811/src/220811-1-30min-lum.xlsx",
								# "/home/jabard89/Dropbox/Data_JB/Plate/Luminescence/220811/220811-1-30min-lum.tsv"])

	# Write out parameters
	with open(args.output_file,'w') as f:
		f.write("# Run started {}\n".format(datetime.now()))
		f.write("# Command: {}\n".format(' '.join(sys.argv)))
		f.write("# Parameters:\n")
		optdict = vars(args)
		for (k,v) in optdict.items():
			f.write("#\t{k}: {v}\n".format(k=k,v=v))

	raw = pd.read_excel(args.input,header=None,engine='openpyxl')
	column_1 = raw.iloc[:,0]
  
  	#scan to find row indices for channels
	read_flag = False #flag for whether a channel is being scanned
	data_rows=[]
	channel_name = ''

	for i in range(0,len(column_1)):
		item = column_1[i]
		row = raw.iloc[i,:]

		if not read_flag: #looking for the next channel
			if pd.isna(item): continue #can't do == on NA, so need to skip them
			if item == "Time [s]":
				channel_name = column_1[i-1]
				cycle_time = row[1]
				read_flag = True #we found a channel!
			else: continue # we were looking for the next Cycle Nr., so lets keep looking
		
		else: #scanning through the data
			if pd.isna(item):
				continue
				# need to figure out what multiple channels looks like!
			if item == "Time [s]":
				cycle_time = row[1]
				continue
			if item == "Temp. [°C]":
				cycle_temp = row[1]
				continue
			if item == "Cycle Nr.":
				cycle_num = row[1]
				continue
			if item == "<>":
				column_names = row[1:].astype("int").astype("string")
				continue
			if item == "End Time":
				continue
			else: # must be a row of data
				row_name = item
				row_data = row[1:].astype("float")
				row_dict = {
					'Channel':channel_name,
					"Time_min":float(cycle_time)/60,
					"Cycle":cycle_num,
					"Temperature":cycle_temp,
					"Value":row_data,
					"Well":row_name+column_names
					}
				row_df = pd.DataFrame(row_dict).dropna()
				data_rows.append(row_df)
	
	# now put everything together into a dataframe
	data_df = pd.concat(data_rows)
	data_df.to_csv(args.output_file,index=False,sep='\t',mode='a')