

import os, sys, signal
from random import randint
import subprocess
import datetime as date
import fileinput
import urllib.request 
from .env import Env

version = "4.0"
env = Env()
debug = False

def mkdir(directory):
    if not os.path.exists(directory+"/"):
        os.makedirs(directory+"/")
    return directory

def cp(src, dst):
    mkdir(dst)
    if ( os.system("cp -r "+src+"/* "+dst+" > /dev/null 2>&1") == 0 ):
        return True
    else:
        if ( os.system("cp -r "+src+" "+dst+" > /dev/null 2>&1") == 0 ):
            return True

    return False

def rm(dst):
    if ( os.system("rm -rf "+dst+" > /dev/null 2>&1") == 0 ):
        return True
    else:
        return False

def exec_to_log(cmd, log):
    if (os.system ( ' ( /bin/bash -c "' + cmd + '" ) > '+log+' 2>&1' ) == 0):
        return True
    else:
        return False


def gettime():
    now = date.datetime.now()
    return str(now.strftime("%a %Y/%m/%d %H:%M:%S"))

def get_githash(git):
    l = os.popen("cd "+git+" && ( git log --pretty=format:'%H' -n 1 ) 2>&1").read()
    if not l:
        l = '-'
    return l

def insert_line_before_once(filepath, newline, pattern):
    repetition = 1;
    with fileinput.input(filepath, inplace=True) as f:
        for l in f:
            if l.startswith(pattern):
                if repetition > 0:
                    print (newline + '\n')
                    repetition -= 1
            print ( l )

def create_rand_file():
    return env.logfolder + '/' + str(randint(0000,9999)) + '.log' 
    


def get_http(url, dest):
    pkg = os.path.basename(url)
    print("Getting " + pkg + " over HTTP... ", end="", flush=True)
    mkdir(dest)
    if ( urllib.request.urlretrieve(url, dest + "/" + pkg) ):
        print("OK");
    else:
        print("FAILED")

def get_local(path, dest, pkg = ""):
    print("Getting " + pkg + " from " + path + "... ", end="", flush=True)
    mkdir(dest)
    if ( cp(path, dest) ):
        print("OK");
    else:
        print("FAILED")

def git_clone(url, dest, pkg = "" ):
    print("Cloning "+pkg + " from " + url + "... ", end="", flush=True)
    if (os.system("git clone "+url+" " \
            +dest+" > /dev/null 2>&1") == 0):
        print("OK")
    else:
        print("FAILED")


def cleanup():
    if (debug == False):
        rm(env.workspace);

def abort(string):
    cleanup()
    print("ERROR: "+string)
    sys.exit(2)

def signal_handler(signal, frame):
    print("You pressed ctrl+c!")
    cleanup()
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


