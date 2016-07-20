

import os, sys, signal
import subprocess
import datetime as date

version = "4.0"
workspace = ""
debug = False

def mkdir(directory):
    if not os.path.exists(directory+"/"):
        os.makedirs(directory+"/")

def cp(src, dst):
    if ( os.system("cp -r "+src+"/* "+dst+" > /dev/null 2>&1") == 0 ):
        return True
    else:
        return False

def rm(dst):
    if ( os.system("rm -rf "+dst+" > /dev/null 2>&1") == 0 ):
        return True
    else:
        return False

def exec_to_log(cmd, log):
    if (os.system ( ' ( /bin/bash -c "' + cmd + '" ) >> '+log+' 2>&1' ) == 0):
        return True
    else:
        return False

def gettime():
    now = date.datetime.now()
    return str(now.strftime("%a %Y/%m/%d %H:%M:%S"))

def get_githash(git):
    l = os.popen("cd "+git+" && git log --pretty=format:'%H' -n 1").read()
    s = l[0:7]
    return l,s

def cleanup():
    if (debug == False):
        rm(workspace);

def abort(string):
    cleanup()
    print("ERROR: "+string)
    sys.exit(2)

def signal_handler(signal, frame):
    print("You pressed ctrl+c!")
    cleanup()
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


