#!/bin/bash
filepath="src"
files="${filepath}/*.xlsx" #for just one file, use files="${filepath}/file1.xlsx" instead
script="/home/jabard89/Dropbox/code_JB/repos/tecan/extract_from_excel.py"
for f in $files
do
	filename=$(basename $f .xlsx)
	# need to skip any temporary files from excel (that start with ~)
	fstart=${filename:0:1}
	if [[ "${fstart}" == "~" ]]
	then
		continue
	fi
	
	inputfile="${filepath}/${filename}.xlsx"
	outputfile="${filepath}/${filename}.tsv"
	echo "input=${inputfile}"
	echo "output=${outputfile}"
	python $script $inputfile $outputfile
done