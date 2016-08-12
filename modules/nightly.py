
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
        csvline = 'ArchC;' + self.archc.archc['link'] + ';' 
        if self.archc.archc['hash'] != '-' :
            csvline += HTML.href(self.archc.archc['hash'][0:7], \
                                 self.archc.archc['link'].replace('.git','') + '/commit/' + self.archc.archc['hash'] ) 
        else:
            csvline += self.archc.archc['hash'][0:7]
        csvline += HTML.running('archc', 1)
        self.testspage.update_archc_table(csvline)

        # --CrossCompiler
        crosslines = ''
        models = {}   # The dict is just to show one cross per model
        for s in self.simulators:
            if not s.model['name'] in models:
                crosslines += 'GCC Cross ' + s.model['name'] + ';' + s.cross['link'] + ';-;' + HTML.success() + '\n'
                models[s.model['name']] = s.cross['link']
        self.testspage.update_archc_table(crosslines)

        # environment
        ccpath     = exec_to_var('which gcc')
        cxxpath    = exec_to_var('which g++')
        ccversion  = exec_to_var("gcc --version | awk '/^gcc/ {print $4;}'")
        cxxversion = exec_to_var("g++ --version | awk '/^g++/ {print $4;}'")

        ccdump = create_rand_file()
        exec_to_log('gcc -v', ccdump)
        cxxdump = create_rand_file()
        exec_to_log('g++ -v', cxxdump)

        ccpage  = env.htmloutput + '/' + env.testnumber + '-gcc-version.html'  
        cxxpage = env.htmloutput + '/' + env.testnumber + '-g++-version.html'  

        HTML.log_to_html (ccdump,  ccpage,  "GCC Version")
        HTML.log_to_html (cxxdump, cxxpage, "G++ Version")

        envlines  = 'GCC Host;' + ccpath  + ';' + ccversion  + ';' + \
                HTML.success() + ' (' + HTML.lhref('version', ccpage) + ')\n'
        envlines += 'G++ Host;' + cxxpath + ';' + cxxversion + ';' + \
                HTML.success() + ' (' + HTML.lhref('version', cxxpage) + ')\n'
        self.testspage.update_archc_table(envlines)

        # -- Simulators
        for simulator in self.simulators:
            tableline = simulator.get_name() + ';' + simulator.get_modellink() + ';' ;
            if simulator.get_modelhash() != '-' :
                tableline += HTML.href(simulator.get_modelhash()[0:7], simulator.get_modellink().replace('.git','') \
                            + '/commit/' + simulator.model['hash']) + ';'
            else:
                tableline += '-' + ';'
            tableline += HTML.monospace(simulator.get_generator()) + ';' + HTML.monospace(simulator.get_options()) 
            tableline += HTML.running(simulator.get_name(), 3)
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

    def building_archc(self):
        line = self.archc.build_archc();
        search_and_replace(self.testspage.get_page(), \
                            '^.*tag=\'archc\'.*$', 
                            HTML.csvline_to_html(line))

    def running_simulators (self):
        for simulator in self.simulators:
            self.running_simulator(simulator)

    def running_simulator(self, simulator):
        env.archc_envfile = self.archc.archc['prefix']+'/etc/env.sh'
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
        cp(env.scriptroot + '/modules/', env.workspace + '/modules/')

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

        if self.archc.archc['hash'] == '-':
            return True
        for sim in self.simulators:
            if sim.model['hash'] == '-':
                return True

        with open(last_page, "r") as f:
            for l in f:

                # ArchC check
                s = re.search(r'<td>(%s)</td><td><a.*>([A-Za-z0-9]*)</a></td>' % self.archc.archc['link'], l)
                if s:
                    if self.archc.archc['hash'][0:7] != s.group(2):
                        return True
                # Simulators check
                for sim in self.simulators:
                    s = re.search(r'<td>(%s)</td><td><a.*>([A-Za-z0-9]*)</a></td>' % sim.get_modellink(), l)
                    if s:
                        if sim.get_modelhash()[0:7] != s.group(2):
                            return True
        return False



class Condor:

    def __init__(self, archc, simulator):
        self.archc      = archc
        self.simulator = simulator

        self.testspage = env.htmloutput + "/" + env.testnumber + TestsPage.suffix
        self.indexpage = env.htmloutput + "/" + env.indexhtml
        
    def running_simulator (self, simulator):
        try:
            env.archc_envfile = self.archc.archc['prefix']+'/etc/env.sh'
            line  = simulator.gen_and_build();
            line += simulator.run_tests()
            search_and_replace(self.testspage, \
                               '<td tag=\'' + simulator.name + '\'.*</td></td>', \
                               HTML.csvcells_to_html(line))
        except:
            abort_testspage("Unexpected error:", sys.exc_info()[0], self.testspage, simulator.name)
            raise


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

