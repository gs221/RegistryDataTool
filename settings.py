# File Paths
DATA_PATH = './data/'
CONFIG_PATH = './configurations/'
TRAINING_PATH = 'training/'
TEMP_PATH = 'tmp/'

# Subset of column names for ucas and scl files, used to identify each file. 
# Should a column name change, edit here and the option should start to function again. 
UCAS_COLUMNS = ['School', 'Site code', 'Time stamp', 'School Name', 'Former name', 'Mailsort']
SCL_COLUMNS = ['School code', 'Short name', 'Full name', 'Hercules update timestamp']