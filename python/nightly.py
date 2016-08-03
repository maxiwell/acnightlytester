
from python import utils
import os, re
from random import randint
from .html import *

class Env:
    random     = ""
    scriptroot = ""
    workspace  = ""
    indexhtml  = "index.html"

    htmloutput = ""
    testnumber = "0"

    def __init__(self, workspace, htmloutput):
        self.random     = randint(0000,9999)
        self.scriptroot = os.getcwd()
        self.workspace  = self.resolvenv(workspace)
        self.htmloutput = self.resolvenv(htmloutput)
        utils.workspace = self.workspace 
        self.testnumber = self.gettestnumber()

        self.logfolder  = self.workspace + "/log/"
        utils.mkdir(self.logfolder)

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
   

class Nightly ():

    def __init__(self, env, archc, simulators, cross):
        self.indexpage = IndexPage(env)
        self.testspage = TestsPage(env)
        
        self.env        = env
        self.archc      = archc
        self.simulators = simulators
        self.cross      = cross
        
    def building_archc(self):
        line = self.archc.build_archc();
        self.testspage.update_archc_table(line)

    def running_simulators (self):
        for simulator in self.simulators:
            archc_env = self.archc.archc_prefix+'/etc/env.sh'
            line  = simulator.gen_and_build(archc_env);
            line += simulator.run_tests()
            self.testspage.update_tests_table(line)

    def finalize(self):

        self.testspage.update_archc_table(self.cross.get_crosscsvline())
        
        for simulator in self.simulators:
            simulator.close_sim_page()
        
        self.testspage.close_tests_page()

        test_results = ""
        if self.testspage.tests_had_failed():
            test_results = HTML.fail()
        else:
            test_results = HTML.success()
        
        csvline =  self.env.testnumber + ';' + utils.gettime() + ';'
        csvline += test_results + HTML.href("(log)", self.testspage.get_tests_page()) + ';'
        csvline += "-;-;"
       
        self.indexpage.update_index_table(csvline)


    def git_hashes_changed(self):
        last_page = self.env.htmloutput + "/" + str(int(self.env.testnumber)-1) + TestsPage.suffix;
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

    


