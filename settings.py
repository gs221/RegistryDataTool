""" ----------- Whole-Program ----------- """

# File Paths 
DATA_PATH = './data/'
CONFIG_PATH = './configurations/'
TRAINING_PATH = 'training/'
TEMP_PATH = 'tmp/'



""" ---------- Menu Option One ---------- """

# File names
POTENTIAL_MATCHES = 'potential_matches.csv'
A_ONLY = 'a_only.csv'
B_ONLY = 'b_only.csv'

# Column names (subset) for file identification
UCAS_COLUMNS = ['School', 'Site code', 'Time stamp', 'School Name', 'Former name', 'Mailsort']
SCL_COLUMNS = ['School code', 'Short name', 'Full name', 'Hercules update timestamp']



""" ---------- Menu Option Two ---------- """

# File names
POTENTIAL_DUPLICATES = 'potential_duplicates.csv'



""" ---------- Menu Option Three ---------- """

# File names
LINKS_CHECKED = 'links_checked.csv'

# Request Options
REQUEST_TIMEOUT = 30
VERIFY_CERT = False

# Link check codes
EMPTY = 'EMP'
NO_RESPONSE = 'NOR'
WAYBACK_MACHINE = 'WBM'

# Wayback machine API
USE_WBM = False
WBM_API = 'https://archive.org/wayback/available?url='