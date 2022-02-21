"""
Created on 2/21/2022
@author: Jared Bard
Script for pulling data from excel timecourse data from Tecan Spark
"""

import sys, os, math, random, argparse, csv
from datetime import datetime
import pandas as pd
import numpy as np
import xlrd

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generate options")
	# Required arguments
	parser.add_argument(dest="input",default=None,type=str,help="input excel file")
	parser.add_argument(dest="output_file",default=None,type=str,help="file to export tsv data to")
	args = parser.parse_args()
	# args = parser.parse_args(["/home/jabard89/Dropbox/Data_JB/Plate/Disagg/220221/src/220221-disagg-1.xlsx",
	# 							"/home/jabard89/Dropbox/Data_JB/Plate/Disagg/220221/src/220221-disagg-1.tsv"])

	# Write out parameters
	with open(args.output_file,'w') as f:
		f.write("# Run started {}\n".format(datetime.now()))
		f.write("# Command: {}\n".format(' '.join(sys.argv)))
		f.write("# Parameters:\n")
		optdict = vars(args)
		for (k,v) in optdict.items():
			f.write("#\t{k}: {v}\n".format(k=k,v=v))

	raw = pd.read_excel(args.input,header=None,engine='openpyxl')
	channel_scan = raw.iloc[:,0]
  
  #scan to find row indices for channels
	read_flag = False #flag for whether a channel is being scanned
	data_rows=[]
	wells = []
	channel_name = ''

	for i in range(0,len(channel_scan)):
		item = channel_scan[i]
		row = raw.iloc[i,:]

		if not read_flag: #looking for the next channel
			if pd.isna(item): continue #can't do == on NA, so need to skip them
			if item == "Cycle Nr.":
				channel_name = channel_scan[i-1]
				wells = [row[i] for i in range(2,len(row)-1,2)]
				read_flag = True #we found a channel!
			else: continue # we were looking for the next Cycle Nr., so lets keep looking
		
		else: #if its not the column headers, and its not the end, it must be data!
			if pd.isna(item):
				read_flag = False #done scannign this channel
			cycle = float(row[0])
			temperature = float(row[1])
			times = [float(row[i])/1000/60 for i in range(3,len(row),2)]
			values = [row[i] for i in range(2,len(row),2)]
			for i in range(len(values)): #make sure all values are integers
				try:
					values[i] = float(values[i])
				except ValueError:
					values[i] = np.nan
			
			for i in range(len(wells)):
				temp_row = {"Well":wells[i],
					"Channel":channel_name,
					"Time_min":times[i],
					"Cycle":cycle,
					"Value":values[i],
					"Temperature":temperature}
				data_rows.append(temp_row)
	
	# now put everything together into a dataframe
	data_df = pd.DataFrame.from_dict(data_rows, orient='columns')
	data_df.to_csv(args.output_file,index=False,sep='\t',mode='a')