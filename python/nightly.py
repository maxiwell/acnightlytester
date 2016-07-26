
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
        self.alltestspage.update_archc_table(htmlline)
        self.alltestspage.update_archc_table(self.cross.get_crosscsvline())

    def gen_and_build_simulator (self, simulator):
        archc_env = self.archc.archc_prefix+'/etc/env.sh'
        htmlline = simulator.gen_and_build(archc_env);
        self.alltestspage.update_tests_table(htmlline)

    def finalize(self):
        self.alltestspage.close()

        test_results = ""
        if self.alltestspage.had_failed():
            test_results = HTML.fail()
        else:
            test_results = HTML.success()

        csvline =  self.env.testnumber + ';' + utils.gettime() + ';'
        csvline += test_results + HTML.href("(log)", self.env.htmloutput + '/' + self.env.testnumber + \
                            AllTestsPage.htmlfile_suffix) + ';'
        csvline += "-;-;"
        self.nightlypage.update_table(csvline)


    def git_hashes_changed(self):
        last_page = self.env.htmloutput + "/" + str(int(self.env.testnumber)-1) + AllTestsPage.htmlfile_suffix;
        if not os.path.isfile(last_page):
            return True

        if self.archc.archc_hash == '-':
            return True
        for sim in self.simulators:
            if sim.model_hash == '-':
                return True

        with open(last_page, "r") as f:
            for l in f:

                # ArchC check
                s = re.search(r'<td>(%s)</td><td><a.*>([A-Za-z0-9]*)</a></td>' % self.archc.archc, l)
                if s:
                    if self.archc.archc_hash[0:7] != s.group(2):
                        return True
                # Simulators check
                for sim in self.simulators:
                    s = re.search(r'<td>(%s)</td><td><a.*>([A-Za-z0-9]*)</a></td>' % sim.linkpath, l)
                    if s:
                        if sim.model_hash[0:7] != s.group(2):
                            return True
        return False

    


