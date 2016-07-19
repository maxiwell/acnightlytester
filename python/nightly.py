
from .utils import *
import os, re
from random import randint

class Env:
    random     = ""
    scriptroot = ""
    workspace  = ""
    htmlroot   = ""
    htmlindex  = ""

    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd()

    def set_workspace(self, workspace):
        self.workspace = self.resolvenv(workspace)

    def set_htmlroot(self, htmlroot):
        self.htmlroot = self.resolvenv(htmlroot)
        self.htmlindex  = self.htmlroot + "/index.html"

    def resolvenv(self,cmd):
        cmd = re.sub(r"\$\{RANDOM\}", str(self.random), cmd)
        cmd = re.sub(r"\$\{SCRIPTROOT\}", str(self.scriptroot), cmd)
        return cmd

    def printenv(self):
        print("Environment: ")
        print("| workspace: "+self.workspace)
        print("| scriptroot: "+self.scriptroot)
        print("| htmlroot: "+self.htmlroot)
    
class Nightly:

    env        = None
    archc      = None
    simulators = []
    mibench    = None
    spec2006   = None

    def __init__(self):
        self.env        = None
        self.archc      = None
        self.simulators = []
        self.mibench    = None
        self.spec2006   = None


    def build_and_install_archc(self):
        self.archc.build();


    def gen_and_build_simulator (self, simulator):
        archc_env = self.archc.archc_prefix+'/etc/env.sh'
        simulator.gen_and_build(archc_env);

        
#    def execute_simulator(self, simulator):

    


