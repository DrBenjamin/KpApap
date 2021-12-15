## ./max.R
## R script

# Fetch command line arguments
myArgs <- commandArgs(trailingOnly = TRUE)

# Read csv file
#num <- read.csv("./data_plot.csv", header = TRUE)

# Convert to numerics
num <- as.numeric(myArgs)

# cat will write the result to the stdout stream
cat(max(num))
