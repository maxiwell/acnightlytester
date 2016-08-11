import os, re
from random import randint

class Env:

    indexhtml       = "index.html"

    logfolder       = '/log/'
    xtoolsfolder    = '/xtools/'
    condorfolder    = '/condor/'

    archc_envfile   = ""

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd() + '/'

    def copy(self, env):
        self.indexhtml     = env.indexhtml
        self.logfolder     = env.logfolder
        self.xtoolsfolder  = env.xtoolsfolder
        self.condorfolder  = env.condorfolder
        self.archc_envfile = env.archc_envfile
        self.random        = env.random
        self.scriptroot    = env.scriptroot
        self.workspace     = env.workspace
        self.htmloutput    = env.htmloutput
        self.testnumber    = env.testnumber
        self.binutils      = env.binutils
        self.gdb           = env.gdb

    def setworkspace(self, workspace):
        self.workspace    = self.resolvenv(workspace) 
        self.logfolder    = self.workspace + self.logfolder
        self.xtoolsfolder = self.workspace + self.xtoolsfolder
        self.condorfolder = self.workspace + self.condorfolder

        for d in [ self.logfolder, self.xtoolsfolder, self.condorfolder ]:
            if not os.path.exists(d+"/"):
                os.makedirs(d+"/")     

    def sethtmloutput(self, htmloutput):
        self.htmloutput = self.resolvenv(htmloutput) 
        self.testnumber = self.gettestnumber() 

    def resolvenv(self,cmd):
        cmd = re.sub(r"\$\{RANDOM\}", str(self.random), cmd)
        cmd = re.sub(r"\$\{SCRIPTROOT\}", str(self.scriptroot), cmd)
        return cmd

    def gettestnumber(self):
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

    def printenv(self):
        print("Environment: ")
        print("| workspace: "+self.workspace)
        print("| scriptroot: "+self.scriptroot)
        print("| htmloutput: "+self.htmloutput)
   


