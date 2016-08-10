
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

        # [TestsPage] Init the Tables
        # -- ArchC 
        csvline = 'ArchC;' + self.archc.archc + ';' 
        if self.archc.archc_hash != '-' :
            csvline += HTML.href(self.archc.archc_hash[0:7], \
                                 self.archc.archc.replace('.git','') + '/commit/' + self.archc.archc_hash ) 
        else:
            csvline += self.archc.archc_hash[0:7]
        csvline += HTML.running('archc', 1)
        self.testspage.update_archc_table(csvline)

        # --CrossCompiler
        crosslines = ''
        models = {}   # The dict is just to show one cross per model
        for s in self.simulators:
            if not s.model in models:
                crosslines += 'Cross ' + s.model + ';' + s.crosslink + ';-;' + HTML.success() + '\n'
                models[s.model] = s.crosslink
        self.testspage.update_archc_table(crosslines)

        # -- Simulators
        for simulator in self.simulators:
            tableline = simulator.name + ';' + simulator.linkpath + ';' ;
            if simulator.model_hash != '-' :
                tableline += HTML.href(simulator.model_hash[0:7], simulator.linkpath.replace('.git','') \
                            + '/commit/' + simulator.model_hash) + ';'
            else:
                tableline += '-' + ';'
            tableline += HTML.monospace(simulator.generator) + ';' + HTML.monospace(simulator.options) 
            tableline += HTML.running(simulator.name, 3)
            self.testspage.update_tests_table(tableline)
       
        # [TestsPage] Close 
        self.testspage.close_tests_page()

        # [IndexPage] Init 
        tags = "index"
        for s in self.simulators:
            tags += s.name
        csvline  =  env.testnumber + ';' + gettime() + '</td>' 
        csvline +=  HTML.running(tags, 1) 
        csvline += '<td> -- ('  + HTML.lhref('log', self.testspage.get_page()) + ');-;'
        csvline += gethostname() 
        self.indexpage.update_index_table(csvline)

        index_page_path = self.indexpage.get_page()

        
    def building_archc(self):
        line = self.archc.build_archc();
        search_and_replace(self.testspage.get_page(), \
                            '^.*tag=\'archc\'.*$', 
                            HTML.csvline_to_html(line))

    def running_simulators (self):
        for simulator in self.simulators:
            self.running_simulator(simulator)

    def running_simulator(self, simulator):
        env.archc_envfile = self.archc.archc_prefix+'/etc/env.sh'
        line  = simulator.gen_and_build();
        line += simulator.run_tests()
        search_and_replace(self.testspage.get_page(), \
                           '<td tag=\'' + simulator.name + '\'.*</td></td>', \
                           HTML.csvcells_to_html(line))
                                                           
    def condor_runnning_simulator(self, simulator):        
        envobj        = env.condorfolder + 'env.p'
        archcobj      = env.condorfolder + 'archc.p'
        simulatorobj  = env.condorfolder + simulator.name + '.p'
        condorexec    = env.condorfolder + 'condor.py'
        condorfile    = env.condorfolder + simulator.name + '.condor'
        
        pickle.dump( simulator,  open (simulatorobj, "wb" ))
        pickle.dump( env,        open (envobj, "wb" ))
        pickle.dump( self.archc, open (archcobj, "wb" ))
        shutil.copyfile(env.scriptroot + 'condor/condor.py', condorexec)
        shutil.copyfile(env.scriptroot + 'condor/tmpl.condor', condorfile)
        cp(env.scriptroot + '/python/', env.workspace + '/python/')

        search_and_replace(condorfile, '{EXECUTABLE}', condorexec)
        search_and_replace(condorfile, '{ARGUMENTS}', env.workspace + ' ' + envobj + ' ' + archcobj + ' ' + simulatorobj)
        search_and_replace(condorfile, '{TESTROOT}', env.workspace + '/')
        search_and_replace(condorfile, '{PREFIX}', simulator.name)
        exec_to_var ('cd ' + env.condorfolder + ' && condor_submit ' + condorfile)

    def finalize(self, simulator):
        status = 'OK'
        if had_failed (self.testspage.get_page()):
            status = 'FAILED'
        search_and_replace_first (self.indexpage.get_page(), simulator.name, status)

        csvline  = "(" + HTML.lhref("log", self.testspage.get_page()) + ')'
        
        search_and_replace_first (self.indexpage.get_page(), '<td tag=\'index[OK]*\'.*>log</a>\)</td>',  \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.success() + csvline))

        search_and_replace_first (self.indexpage.get_page(), '<td tag=\'index[OKFAILED]*\'.*>log</a>\)</td>', \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.fail() + csvline))
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

        self.testspage = env.htmloutput + "/" + env.testnumber + TestsPage.suffix
        self.indexpage = env.htmloutput + "/" + env.indexhtml
        
    def running_simulator (self, simulator):
        env.archc_envfile = self.archc.archc_prefix+'/etc/env.sh'
        line  = simulator.gen_and_build();
        line += simulator.run_tests()
        search_and_replace(self.testspage, \
                   '<td tag=\'' + simulator.name + '\'.*</td></td>', \
                   HTML.csvcells_to_html(line))

    def finalize(self, simulator):
        status = 'OK'
        if had_failed (self.testspage):
            status = 'FAILED'

        search_and_replace_first (self.indexpage, simulator.name, status)

        csvline  = "(" + HTML.lhref("log", self.testspage) + ')'
        
        search_and_replace_first (self.indexpage, '<td tag=\'index[OK]*\'.*>log</a>\)</td>',  \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.success() + csvline))

        search_and_replace_first (self.indexpage, '<td tag=\'index[OKFAILED]*\'.*>log</a>\)</td>', \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.fail() + csvline))

