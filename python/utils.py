

import os

def mkdir(directory):
    if not os.path.exists(directory+"/"):
        os.makedirs(directory+"/")

def cp(src, dst):
    if ( os.system("cp -r "+src+"/* "+dst+" > /dev/null 2>&1") == 0 ):
        return True
    else:
        return False

def parselist(_list):
    _modules = _list.replace(" ","")
    _modules = _modules.replace("[","") 
    _modules = _modules.replace("]","")
    return _modules.split(",")

def exec_to_log(cmd, log):
    if (os.system ( " ( " + cmd + " ) >> "+log+" 2>&1" ) == 0):
        return True
    else:
        return False



