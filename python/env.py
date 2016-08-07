import os, re
from random import randint
from . import utils

class Env:

    indexhtml  = "index.html"

    logfolder       = '/log/'
    xtoolsfolder    = '/xtools/'

    archc_envfile   = ""

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd()

    def setworkspace(self, workspace):
        self.workspace       = self.resolvenv(workspace) 
        self.logfolder       = self.workspace + self.logfolder
        self.xtoolsfolder    = self.workspace + self.xtoolsfolder

        utils.mkdir(self.logfolder)
        utils.mkdir(self.xtoolsfolder)

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
   


