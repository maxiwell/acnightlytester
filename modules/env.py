import os, re
from random import randint

class Env:

    indexhtml       = "index.html"

    logfolder       = '/log/'
    xtoolsfolder    = '/xtools/'
    tarballpool     = None

    archc_envfile   = ""

    debug_mode      = False
    condor_mode     = False

    xtoolsdict      = {}

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd() + '/'
        self.debug_mode  = False
        self.condor_mode = False

    def copy(self, env):
        self.indexhtml     = env.indexhtml
        self.logfolder     = env.logfolder
        self.xtoolsfolder  = env.xtoolsfolder
        self.archc_envfile = env.archc_envfile
        self.random        = env.random
        self.scriptroot    = env.scriptroot
        self.workspace     = env.workspace
        self.htmloutput    = env.htmloutput
        self.testnumber    = env.testnumber
        self.debug_mode    = env.debug_mode
        self.condor_mode   = env.condor_mode
        self.tarballpool   = None
        self.xtoolsdict    = {}

    def set_workspace(self, workspace):
        self.workspace    = self.resolvenv(workspace) 

        for d in [ self.logfolder, self.xtoolsfolder ]:
            if not os.path.exists(self.workspace + d + "/"):
                os.makedirs(self.workspace + d + "/")     

    def get_workspace(self):
        return os.path.normpath(self.workspace) + '/'


    def get_logfolder(self):
        return self.workspace + self.logfolder

    def get_xtoolsfolder(self):
        return self.workspace + self.xtoolsfolder

    def set_htmloutput(self, htmloutput):
        self.htmloutput = os.path.normpath(self.resolvenv(htmloutput)) + '/'
        self.testnumber = self.compute_testnumber() 
        if not os.path.exists(self.htmloutput + self.testnumber + "/"):
            os.makedirs(self.htmloutput + self.testnumber + "/")     

    def get_htmloutput(self):
        return self.htmloutput 

    def get_htmloutput_priorprefix(self):
        return str(int(self.testnumber)-1) + "/"
    
    def get_htmloutput_prefix(self):
        return self.testnumber + '/' 

    def get_htmloutput_fullstring(self):
        return self.get_htmloutput() + self.get_htmloutput_prefix()

    def set_tarballpool(self, pool):
        self.tarballpool = os.path.normpath(self.resolvenv(pool)) + '/'
        if not os.path.exists(self.tarballpool + "/"):
            os.makedirs(self.tarballpool + "/")

    def get_tarballpool(self):
        return self.tarballpool

    def resolvenv(self,cmd):
        cmd = re.sub(r"\$\{RANDOM\}", str(self.random), cmd)
        cmd = re.sub(r"\$\{SCRIPTROOT\}", str(self.scriptroot), cmd)
        return cmd

    def compute_testnumber(self):
        testnumber = 0
        try:
            with open(self.htmloutput + "/" + self.indexhtml, "r") as f:
                for l in f:
                    s = re.search(r'^<tr><td>([0-9]*)</td>', l)
                    if s:
                        testnumber = int(s.group(1))+1
                        break
        except:
            testnumber = 1
        
        return str(testnumber)

    def get_indexhtml(self):
        return self.htmloutput + '/' + self.indexhtml

    def set_archcenv(self, archcenv):
        self.archc_envfile = archcenv

    def get_archcenv(self):
        return self.archc_envfile

    def printenv(self):
        print("Environment: ")
        print("| workspace: "+self.workspace)
        print("| scriptroot: "+self.scriptroot)
        print("| htmloutput: "+self.htmloutput)
   
    def enable_dbg(self):
        self.debug_mode = True

    def enable_condor(self):
        self.condor_mode = True

    def get_xtools_cache(self, linkpath):
        if linkpath in self.xtoolsdict:
            return self.xtoolsdict[linkpath]
        else:
            return None,None,None 

    def add_xtools_cache(self, linkpath, prefix, crossversion, crossdump):
        if linkpath in self.xtoolsdict:
            return False
        else:
            self.xtoolsdict[linkpath] = [prefix, crossversion, crossdump]
            return True






