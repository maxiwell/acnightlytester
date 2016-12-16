

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

def inflate(arg):
    # In condor environment nproc is not the same. So it's necessary
    # get the cpuinfo in each inflate call
    nproc   = exec_to_var("cat /proc/cpuinfo | grep \"^processor\" | wc -l")
    if arg == "make":
        return " make -j" + nproc + " " 
    if arg == "make install":
        return " make -j" + nproc + " install " 

def mkdir(directory):
    if not os.path.exists(directory+"/"):
        os.makedirs(directory+"/")
    return directory

def cp(src, dst):
    mkdir(dst)
    if exec_to_log("cp -r "+src+"/* "+dst)[0]:
        return True
    else:
        if exec_to_log("cp -r "+src+" "+dst)[0]:
            return True

    return False

def rm(dst):
    return exec_to_log("chmod 777 -R " + dst + " && rm -rf " + dst, "/dev/null")[0]

def _exec(cmd, errors_in_stdout=True):
    try:
        err = subprocess.STDOUT
        if not errors_in_stdout:
            err = subprocess.PIPE

        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,  \
                                                stdout=subprocess.PIPE, \
                                                stderr=err, \
                                                shell=True)

        out, err = process.communicate(cmd.encode('utf-8'), timeout)
        retcode  = process.returncode
        return out, err, retcode

    except OSError as e:
        print ("OSError > ",e.errno)
        print ("OSError > ",e.strerror)
        print ("OSError > ",e.filename)
        #return e.strerror, err, 255
        return "OSError", err, 255
    except subprocess.CalledProcessError as e:
        print("CalledProcessError > ", e.output)
        #return e.output, err, 255
        return "CalledProcessError", err, 255
    except subprocess.TimeoutExpired as e:
        print("TimeoutExpired > "+str(timeout)+"s")
        process.terminate()
        return "TimeoutExpired > "+str(timeout)+"s", err, 255
    except:
        print ("Error > ",sys.exc_info()[0])
        #return sys.exc_info()[0]
        return "Error", err, 255 
        
def exec_to_log(cmd, log = None):
    if not log:
        log = create_rand_file()

    out, err, retcode = _exec(cmd)

    dump  = "===========\n"
    dump += "$ " + cmd + '\n'
    dump += "===========\n\n"
    try:
        dump += out.decode('utf-8')
    except:
        dump += "Except Error"
        print ("Error > ", sys.exc_info()[0])

    f = open(log, 'w')
    f.write(dump)
    f.close()

    if retcode == 0:
        return True, log
    else:
        return False, log

def exec_to_var(cmd):
    out, err, retcode = _exec(cmd, errors_in_stdout=False)
    return out.strip().decode('utf-8')


def string_to_log(string):
    log = create_rand_file ()
    f = open(log, 'w')
    f.write(string)
    f.close()
    return log


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

def get_githash(directory):
    l = os.popen("cd "+directory+" && ( git log --pretty=format:'%H' -n 1 ) 2>&1").read()
    if not l:
        l = '-'
    return l

def get_githash_online(link, branch):
    return exec_to_var ('git ls-remote ' + link + ' | grep ' + branch + ' | cut -f1')

def get_first_line_with_pattern(filepath, pattern):
    with open(filepath) as f:
        for l in f:
            if pattern in l:
                return l

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
    return env.get_logfolder() + '/' + get_random() + '.log' 

def get_random():
    return str(randint(0000,9999))

def is_linkpath_a_git (link):
    if link.startswith('git'):
        return True
    if link.startswith('http') and link.endswith('.git'):
        return True
    return False

def is_linkpath_a_local (link):
    if os.path.isdir(link):
        return True
    # in case of local tarball file
    if os.path.isfile(link):
        return True
    return False

def get_tar_git_or_folder(srclink, dstfolder):
    dstfolder = os.path.normpath(dstfolder) + '/'
 
    if is_linkpath_a_git(srclink):
        git_clone (srclink, 'master', dstfolder)
        return dstfolder

    if is_linkpath_a_local(srclink):
        get_local(srclink, dstfolder)
    
        if os.path.isdir (srclink):
            return dstfolder
        else:
            filename = os.path.basename(srclink)
            return untar(dstfolder + filename, dstfolder)

    else:
        if srclink.startswith('http'):
            get_http(srclink, dstfolder)
            filename = os.path.basename(srclink)
            return untar(dstfolder + filename, dstfolder) 
    
    return None

# Removing the 'workspace' from absolute path (to Condor approach)
def get_relative_path(absolute_path):
    ws = os.path.normpath(env.workspace)
    return absolute_path.replace(ws,'')
    
def had_failed(page, linematch = ''):
    if linematch != '':
        line = get_first_line_with_pattern(page, linematch)
        if re.search("Failed", line):
            return True
    else:
        with open(page, 'r') as f:
            for l in f:
                if re.search("Failed", l):
                    return True
    return False
    
def untar (tarfile_, dstfolder):
    print("| Extracting Tarball... ", end="", flush=True)
    tar = tarfile.open(tarfile_)
    if not tar:
        print("FAILED")
    prefix = dstfolder + tar.getnames()[0].split('/')[0]
    # check if the folder already exist 
    if os.path.isdir(prefix):
       rm (prefix)
    tar.extractall(dstfolder)
    tar.close()
    print("OK")
    return os.path.normpath(prefix) + '/'

def get_http(url, dest):
    mkdir(dest)
    
    pkg = os.path.basename(url)
    tarballpool = env.get_tarballpool()
    
    if tarballpool and os.path.isfile(tarballpool + pkg):
        print("Getting " + pkg + " from Tarball Pool... ", end="", flush=True)
        if ( cp(tarballpool + pkg, dest) ):
            print("OK")
        else:
            print("FAILED")
    else:
        print("Getting " + pkg + " over HTTP... ", end="", flush=True)
        if ( urllib.request.urlretrieve(url, dest + "/" + pkg) ):
            print("OK");
        else:
            print("FAILED")
        
        if tarballpool:
            print("| copying to Tarball Pool folder...", end="", flush=True)
            if cp (dest + "/" + pkg, tarballpool):
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
    if exec_to_log("git clone --depth 1 -b " + branch + " " + url + " " + dest)[0]:
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


