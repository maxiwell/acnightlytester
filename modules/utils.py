

import os, sys, signal, re
import tarfile, socket
import subprocess
import datetime as date
import fileinput
import urllib.request 
from random import randint
from .env import Env

version = "4.0"
env = Env()
timeout = 7200

def mkdir(directory):
    if not os.path.exists(directory+"/"):
        os.makedirs(directory+"/")
    return directory

def cp(src, dst):
    mkdir(dst)
    if exec_to_log("cp -r "+src+"/* "+dst, "/dev/null"):
        return True
    else:
        if exec_to_log("cp -r "+src+" "+dst, "/dev/null"):
            return True

    return False

def rm(dst):
    return exec_to_log("chmod 777 -R " + dst + " && rm -rf " + dst, "/dev/null")

def exec_to_log(cmd, log):
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,  \
                                            stdout=subprocess.PIPE, \
                                            stderr=subprocess.STDOUT, \
                                            shell=True)
    out, err = process.communicate(cmd.encode('utf-8'), timeout)
    f = open(log, 'w')
    f.write(out.decode('utf-8'))

    if process.returncode == 0:
        return True
    else:
        return False

def exec_to_var(cmd):
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate(cmd.encode('utf-8'), timeout)
    return out.strip().decode('utf-8')

def find_ext(filename):
    name = filename.split('.')
    ext = ''
    if len(name) == 2:
        ext = '.'+name[1]
    else:
        ext = '.'+name[1]+'.'+name[2]
    return ext

def gettime():
    now = date.datetime.now()
    return str(now.strftime("%a %Y/%m/%d %H:%M:%S"))

def gethostname():
    return socket.gethostname()

def get_githash(git):
    l = os.popen("cd "+git+" && ( git log --pretty=format:'%H' -n 1 ) 2>&1").read()
    if not l:
        l = '-'
    return l

def get_githash_online(link, branch):
    return exec_to_var ('git ls-remote ' + link + ' | grep ' + branch + ' | cut -f1')

def search_and_replace(filepath, pattern, string):
    with fileinput.input(filepath, inplace=True) as f:
        for l in f:
            res = re.sub(pattern, string, l)
            print (res, end='')  

def search_and_replace_first(filepath, pattern, string):
    repetition = 1;
    with fileinput.input(filepath, inplace=True) as f:
        for l in f:
            if repetition > 0:
                res = re.sub(pattern, string, l)
                print (res, end='')
                if res != l:
                    repetition -= 1
            else:
                print(l, end='')

def insert_line_before_once(filepath, newline, pattern):
    repetition = 1;
    with fileinput.input(filepath, inplace=True) as f:
        for l in f:
            if l.startswith(pattern):
                if repetition > 0:
                    print (newline)
                    repetition -= 1
            print ( l , end='')

def create_rand_file():
    return env.get_logfolder() + '/' + str(randint(0000,9999)) + '.log' 
   
def get_tar_git_or_folder(srclink, dstfolder):
    dstfolder = os.path.normpath(dstfolder) + '/'
    mkdir (dstfolder)
    filename = os.path.basename(os.path.normpath(srclink))
    prefix = dstfolder + filename
    if not os.path.isdir(prefix):
        if os.path.isdir(srclink):
            get_local(srclink, prefix)
        else:
            if not os.path.isfile(prefix):
                if srclink.startswith('git'):
                    git_clone (srclink, 'master', dstfolder)
                    return dstfolder
                elif srclink.startswith('http'):
                    if srclink.endswith('.git'):
                        git_clone (srclink, 'master', dstfolder)
                        return dstfolder
                    else:
                        get_http(srclink, dstfolder)
                else:
                    get_local(srclink, dstfolder)
            tar = tarfile.open(prefix)
            prefix = dstfolder + tar.getnames()[0].split('/')[0]
            if not os.path.isdir(prefix):
                tar.extractall(dstfolder)
            tar.close()
    return os.path.normpath(prefix) + '/' 

# Removing the 'workspace' from absolute path (to Condor approach)
def get_relative_path(absolute_path):
    ws = os.path.normpath(env.workspace)
    return absolute_path.replace(ws,'')
    
def had_failed(page):
   with open(page, 'r') as f:
       for l in f:
           if re.search("Failed", l):
               return True
   return False
           
                      
def get_http(url, dest):
    pkg = os.path.basename(url)
    mkdir(dest)
    if os.path.isfile(env.get_tarballpool() + pkg):
        print("Getting " + pkg + " from Tarball Pool... ", end="", flush=True)
        if ( cp(env.get_tarballpool() + pkg, dest) ):
            print("OK")
        else:
            print("FAILED")
    else:
        print("Getting " + pkg + " over HTTP... ", end="", flush=True)
        if ( urllib.request.urlretrieve(url, dest + "/" + pkg) ):
            print("OK");
        else:
            print("FAILED")
        
        if env.get_tarballpool():
            print("| copying to Tarball Pool folder...", end="", flush=True)
            if cp (dest + "/" + pkg, env.get_tarballpool()):
                print("OK")
            else:
                print("FAILED")

def get_local(path, dest, pkg = ""):
    print("Getting " + pkg + " from " + path + "... ", end="", flush=True)
    mkdir(dest)
    if ( cp(path, dest) ):
        print("OK");
    else:
        print("FAILED")

def git_clone(url, branch, dest, pkg = "" ):
    print("Cloning "+pkg + " from " + url + "... ", end="", flush=True)
    if exec_to_log("git clone --depth 1 -b " + branch + " " + url + " " + dest, "/dev/null"):
        print("OK")
    else:
        print("FAILED")


def cleanup():
    if env.debug_mode == False and env.condor_mode == False:
    	rm(env.workspace)

def abort ( string ):  
    print(string)
    cleanup()
    sys.exit(2)

def signal_handler(signal, frame):
    abort("You pressed CTRL+C!")

signal.signal(signal.SIGINT, signal_handler)


