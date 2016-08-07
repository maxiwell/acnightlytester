
import os, re
from .html import *
from . import utils

class Nightly ():

    def __init__(self, archc, simulators, cross):
        self.indexpage = IndexPage()
        self.testspage = TestsPage()
        
        self.archc      = archc
        self.simulators = simulators
        self.cross      = cross
        
    def building_archc(self):
        line = self.archc.build_archc();
        self.testspage.update_archc_table(line)

    def running_simulators (self):
        for simulator in self.simulators:
            env.archc_envfile = self.archc.archc_prefix+'/etc/env.sh'
            line  = simulator.gen_and_build();
            line += simulator.run_tests()
            self.testspage.update_tests_table(line)

    def finalize(self):

        self.testspage.update_archc_table(self.cross.get_crosscsvline())
        self.testspage.close_tests_page()

        test_results = ""
        if self.testspage.tests_had_failed():
            test_results = HTML.fail()
        else:
            test_results = HTML.success()
        
        csvline =  env.testnumber + ';' + gettime() + ';'
        csvline += test_results + "(" + HTML.href("log", self.testspage.get_page()) + ');'
        csvline += "-;-;"
       
        self.indexpage.update_index_table(csvline)


    def git_hashes_changed(self):
        last_page = env.htmloutput + "/" + str(int(env.testnumber)-1) + TestsPage.suffix;
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

    


