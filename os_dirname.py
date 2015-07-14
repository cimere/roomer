import os
CURRENT_PATH = os.path.dirname(__file__)
FILENAME = 'prova.log'
MID_PATH = 'logs'
FULL_PATH = os.path.join(CURRENT_PATH, MID_PATH, FILENAME)
print FULL_PATH
f = open(FULL_PATH, 'w+')
f.close()
