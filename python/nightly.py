
import os, re, shutil
from .html import *
from . import utils
import pickle

class Nightly ():

    def __init__(self, archc, simulators):
        self.indexpage = IndexPage()
        self.testspage = TestsPage()
        
        self.archc      = archc
        self.simulators = simulators
        
    def building_archc(self):
        line = self.archc.build_archc();
        self.testspage.update_archc_table(line)

    def running_simulators (self):
        for simulator in self.simulators:
            self.running_simulator(simulator)

    def running_simulator(self, simulator):
        env.archc_envfile = self.archc.archc_prefix+'/etc/env.sh'
        line  = simulator.gen_and_build();
        line += simulator.run_tests()
        self.testspage.update_tests_table(line)

    def condor_runnning_simulator(self, simulator):
        envobj        = env.condorfolder + 'env.p'
        archcobj      = env.condorfolder + 'archc.p'
        simulatorobj  = env.condorfolder + simulator.name + '.p'
        condorexec = env.condorfolder + 'acnightly_condor.py'
        condorfile = env.condorfolder + simulator.name + '.condor'
        
        pickle.dump( simulator,  open (simulatorobj, "wb" ))
        pickle.dump( env,        open (envobj, "wb" ))
        pickle.dump( self.archc, open (archcobj, "wb" ))
        shutil.copyfile(env.scriptroot + 'condor/acnightly_condor.py', condorexec)
        shutil.copyfile(env.scriptroot + 'condor/tmpl.condor', condorfile)

        search_and_replace(condorfile, '{EXECUTABLE}', condorexec)
        search_and_replace(condorfile, '{ARGUMENTS}', envobj + ' ' + archcobj + ' ' + simulatorobj)
        search_and_replace(condorfile, '{TESTROOT}', env.workspace)
        search_and_replace(condorfile, '{PREFIX}', simulator.name)
        exec_to_var ('cd ' + env.condorfolder + ' && condor_submit ' + condorfile)

    def finalize(self):
        
        # Get cross csv lines:
        crosslines = ''
        # The dict is just to show one cross per model
        models = {}
        for s in self.simulators:
            if not s.model in models:
                crosslines += 'Cross ' + s.model + ';' + s.crosslink + ';-;' + HTML.success() + '\n'
                models[s.model] = s.crosslink
        self.testspage.update_archc_table(crosslines)

        self.testspage.close_tests_page()

        test_results = ""
        if self.testspage.tests_had_failed():
            test_results = HTML.fail()
        else:
            test_results = HTML.success()
        
        csvline =  env.testnumber + ';' + gettime() + ';'
        csvline += test_results + "(" + HTML.lhref("log", self.testspage.get_page()) + ');'
        csvline += "-;-;"
       
        self.indexpage.update_index_table(csvline)
        cleanup()


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

class Condor:

    def __init__(self, archc, simulator):
        self.archc      = archc
        self.simulator = simulator
        
    def running_simulator (self, simulator):
        env.archc_envfile = self.archc.archc_prefix+'/etc/env.sh'
        line  = simulator.gen_and_build();
        line += simulator.run_tests()
#        self.testspage.update_tests_table(line)





