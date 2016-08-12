import os, re
from random import randint

class Env:

    indexhtml       = "index.html"

    logfolder       = '/log/'
    xtoolsfolder    = '/xtools/'

    archc_envfile   = ""

    debug_mode      = False
    condor_mode     = False

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd() + '/'
        self.debug_mode = False

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
        self.htmloutput = self.resolvenv(htmloutput) 
        self.testnumber = self.compute_testnumber() 

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
   


