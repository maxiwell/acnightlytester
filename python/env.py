
import os, re
from random import randint

class Env:
    random     = ""
    scriptroot = ""
    workspace  = ""
    htmlroot   = ""

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd()

    def set_workspace(self, workspace):
        self.workspace = self.resolvenv(workspace)

    def set_htmlroot(self, htmlroot):
        self.htmlroot = self.resolvenv(htmlroot)

    def resolvenv(self,cmd):
        cmd = re.sub(r"\$\{RANDOM\}", str(self.random), cmd)
        cmd = re.sub(r"\$\{SCRIPTROOT\}", str(self.scriptroot), cmd)
        return cmd

    def printenv(self):
        print("Environment: ")
        print("| workspace: "+self.workspace)
        print("| scriptroot: "+self.scriptroot)
        print("| htmlroot: "+self.htmlroot)
    


