
from python import utils
import os, re
from random import randint
from .html import *

class Env:
    random     = ""
    scriptroot = ""
    workspace  = ""

    htmloutput = ""
    testnumber = "0"


    def __init__(self):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd()

    def set_workspace(self, workspace):
        self.workspace = self.resolvenv(workspace)

    def set_htmloutput(self, htmloutput):
        self.htmloutput = self.resolvenv(htmloutput)

    def resolvenv(self,cmd):
        cmd = re.sub(r"\$\{RANDOM\}", str(self.random), cmd)
        cmd = re.sub(r"\$\{SCRIPTROOT\}", str(self.scriptroot), cmd)
        return cmd

    def printenv(self):
        print("Environment: ")
        print("| workspace: "+self.workspace)
        print("| scriptroot: "+self.scriptroot)
        print("| htmloutput: "+self.htmloutput)
    
class Nightly:

    env        = None
    archc      = None
    simulators = []
    mibench    = None
    spec2006   = None
    cross      = None

    nightlypage   = None
    alltestspage  = None

    def __init__(self):
        self.env        = None
        self.archc      = None
        self.simulators = []
        self.mibench    = None
        self.spec2006   = None
        self.cross      = None

    def init_htmlindex(self):
        self.nightlypage  = NightlyPage(self.env)

    def init_htmllog(self):
        self.alltestspage = AllTestsPage(self.env)

    def build_and_install_archc(self):
        htmlline = self.archc.build_archc();
        self.alltestspage.append_tablearchc(htmlline)
        self.alltestspage.append_tablearchc(self.cross.get_crosscsvline())
        self.alltestspage.close()

    def gen_and_build_simulator (self, simulator):
        archc_env = self.archc.archc_prefix+'/etc/env.sh'
        simulator.gen_and_build(archc_env);

#    def execute_simulator(self, simulator):

    


