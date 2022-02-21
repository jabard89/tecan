tecan_excel_to_tidy <- function(file_name) {
  library(tidyverse)
  
  #raw_sheet <- unname(as.data.frame(read_excel("C:/Users/jabar/Dropbox (Drummond Lab)/Data_JB/Plate/Disagg/201208/201208-2-disagg.xlsx",sheet="Result sheet")))
  raw_sheet <- unname(as.data.frame(read_excel(file_name,sheet="Result sheet")))
  channel_scan <- raw_sheet[,1]
  
  #scan to find row indices for channels
  read.flag <- FALSE #flag for whether a channel is being scanned
  
  tidy_data <- tibble(Well=character(),Channel=character(),Time_min=numeric(),
                      Cycle=numeric(),Value=numeric(),Temperature=numeric())
  
  for (i in 1:length(channel_scan)) {
    item <- channel_scan[i]
    row <- raw_sheet[i,]
    
    if (!read.flag) { #looking for the next channel
      if (is.na(item)) {next} #can't do == on NA, so need to skip them
      if(item == "Cycle Nr.") {
        channel_name <- channel_scan[[i-1]]
        wells <- row[seq(3,length(row),2)]
        read.flag <- TRUE #we found a channel!
      }
      # we were looking for the next Cycle Nr., so lets keep looking
      next
    }
    
    if(is.na(item)) {
      read.flag <- FALSE #done scanning this channel
    }
    
    #if its not the column headers, and its not the end, it must be data!
    cycle <- as.numeric(row[[1]])
    temperature <- as.numeric(row[[2]])
    times <- as.numeric(row[seq(4,length(row),2)])/1000/60
    values <- as.numeric(row[seq(3,length(row),2)])
    
    for (j in 1:length(wells)) {
      temp_row <- tibble_row(Well=wells[[j]],
                             Channel=channel_name,
                             Time_min=times[[j]],
                             Cycle=cycle,
                             Value=values[[j]],
                             Temperature=temperature)
      tidy_data <- tidy_data %>% bind_rows(temp_row)
    }
  }
  return(tidy_data)
}