
import os, re, shutil
from .html import *
from . import utils
import pickle
import traceback

class Nightly ():

    def __init__(self, archc, simulators):
        self.archc      = archc
        self.simulators = simulators

    def init_pages(self):
        self.indexpage = IndexPage()
        self.testspage = TestsPage()
 
        # [TestsPage] Init the Tables
        # -- ArchC 
        csvline  = 'ArchC;' + self.archc.archc['link'] + ';' 
        csvline += self.archc.get_archc_hashtohtml()
        csvline += HTML.running('archc', 1)
        self.testspage.update_archc_table(csvline)

        # --CrossCompiler
        crosslines = ''
        models = {}   # The dict is just to show one cross per model
        for s in self.simulators:
            if not s.model['name'] in models:
                crosslines += s.get_cross_csvline()
                models[s.model['name']] = s.cross['link']
        self.testspage.update_archc_table(crosslines)

        # environment
        ccpath          = exec_to_var('which gcc')
        ccversion       = exec_to_var("gcc --version | awk '/^gcc/ {print $4;}'")
        retcode, ccdump = exec_to_log('gcc -v')
        ccpage  = env.get_htmloutput_fullstring() + 'gcc-version.html'  
        HTML.log_to_html (ccdump,  ccpage,  "GCC Version")
        envlines  = 'GCC Host;' + ccpath  + ';' + ccversion  + ';' + \
                HTML.success() + ' (' + HTML.lhref('version', ccpage) + ')\n'
        self.testspage.update_archc_table(envlines)


        # -- Description table
        desclines = ''
        modules = {}  # The dict is just to show one description per model
        for sim in self.simulators:
            if not sim.module['name'] in modules:
                desclines += '*-' + sim.module['name'] + ";" 
                desclines += HTML.monospace(sim.get_generator()) + ';' 
                desclines += HTML.monospace(sim.get_options()) + ';' 
                desclines += sim.get_desc() + ';\n'
                modules[sim.module['name']] = sim.get_desc()
        self.testspage.update_description_table(desclines)

        # -- Simulators
        for sim in self.simulators:
            tableline  = sim.get_name() + ';' + sim.get_modellink() + ';' + sim.get_modelbranch() + ';'
            tableline += sim.get_model_hashtohtml() + ';'
            tableline += HTML.monospace(sim.get_model_inputtohtml()) 
            tableline += HTML.running(sim.get_name(), 3)
            self.testspage.update_tests_table(tableline)
       
        # [TestsPage] Close 
        self.testspage.close_tests_page()

        # [IndexPage] Init 
        tags = "index"
        for s in self.simulators:
            tags += s.name
        csvline  =  env.testnumber + ';' + gettime() + '</td>' 
        csvline +=  HTML.running(tags, 1) 

        # Here I am using 'href' instead of 'lhref'. This was necessary
        # to adapt the code to use subfolder in the 'htmloutput' folder
        # 'lhref' always link with files in the same folder (./file.html)
        csvline += '<td> -- ('  + HTML.href('log', \
                                    self.testspage.get_page_relative()) + \
                            ');-;'
        csvline += gethostname() 
        self.indexpage.update_index_table(csvline)


    def building_archc(self):
        line = self.archc.build_and_install_archc();
        search_and_replace(self.testspage.get_page(), \
                            '^.*tag=\'archc\'.*$', 
                            HTML.csvline_to_html(line))

    def running_simulators (self):
        for simulator in self.simulators:
            self.running_simulator(simulator)

    def running_simulator(self, simulator):
        env.set_archcenv (self.archc.get_archc_prefix() + '/etc/env.sh')
        line  = simulator.gen_and_build();
        line += simulator.run_tests()
        search_and_replace(self.testspage.get_page(), \
                           '<td tag=\'' + simulator.name + '\'.*</td></td>', \
                           HTML.csvcells_to_html(line))
                                                           
    def condor_runnning_simulator(self, simulator):        
        envobj        = env.get_workspace() + 'env.p'
        archcobj      = env.get_workspace() + 'archc.p'
        simulatorobj  = env.get_workspace() + simulator.name + '.p'
        condorexec    = env.get_workspace() + 'condor.py'
        condorfile    = env.get_workspace() + simulator.name + '.condor'
        
        pickle.dump( simulator,  open (simulatorobj, "wb" ))
        pickle.dump( env,        open (envobj, "wb" ))
        pickle.dump( self.archc, open (archcobj, "wb" ))
        shutil.copyfile(env.scriptroot + 'condor/condor.py', condorexec)
        shutil.copyfile(env.scriptroot + 'condor/tmpl.condor', condorfile)
        cp(env.scriptroot + '/modules/', env.workspace + '/modules/')

        search_and_replace(condorfile, '{EXECUTABLE}', condorexec)
        search_and_replace(condorfile, '{ARGUMENTS}', 'env.p  archc.p  ' + simulator.name + '.p')
        search_and_replace(condorfile, '{TESTROOT}', env.get_workspace())
        search_and_replace(condorfile, '{PREFIX}', simulator.name)
        exec_to_var ('cd ' + env.get_workspace() + ' && condor_submit ' + condorfile)

    def finalize(self, simulator):
        status = 'OK'
        if had_failed (self.testspage.get_page()):
            status = 'FAILED'
        search_and_replace_first (self.indexpage.get_page(), simulator.name, status)

        csvline  = "(" + HTML.href("log", self.testspage.get_page_relative()) + ')'
        
        search_and_replace_first (self.indexpage.get_page(), '<td tag=\'index[OK]*\'.*>log</a>\)</td>',  \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.success() + csvline))

        search_and_replace_first (self.indexpage.get_page(), '<td tag=\'index[OKFAILED]*\'.*>log</a>\)</td>', \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.fail() + csvline))
        cleanup()



    def git_hashes_changed(self):
        last_page = env.get_htmloutput() + \
                    env.get_htmloutput_priorprefix() + \
                    TestsPage.suffix;
        if not os.path.isfile(last_page):
            return True

        if self.archc.archc['hash'] == '-':
            return True
        for sim in self.simulators:
            if sim.model['hash'] == '-':
                return True

        matches   = 0
        matchesOk = 0
        with open(last_page, "r") as f:
            for l in f:
                # ArchC check
                s = re.search(r'<td>(%s)</td><td><a.*>([A-Za-z0-9]*)</a></td>' % self.archc.archc['link'], l)
                if s:
                    matches += 1
                    if self.archc.archc['hash'][0:7] != s.group(2):
                        return True
                # Simulators check
                for sim in self.simulators:
                    s = re.search(r'<td>(%s)</td><td>.*</td><td><a.*>([A-Za-z0-9]*)</a></td>' % sim.get_modellink(), l)
                    if s:
                        matches += 1
                        if sim.get_modelhash()[0:7] != s.group(2):
                            return True

        if matches == len(self.simulators) + 1:
            return False
        else:
            return True


class Condor:

    def __init__(self, archc, simulator):
        self.archc     = archc
        self.simulator = simulator

        self.testspage = env.get_htmloutput_fullstring() + TestsPage.suffix
        self.indexpage = env.get_htmloutput() + "/" + env.indexhtml
        
    def running_simulator (self, simulator):
        try:
            self.archc.reinstall_archc()
            env.set_archcenv(self.archc.get_archc_prefix() + '/etc/env.sh')
            line  = simulator.gen_and_build();
            line += simulator.run_tests()
            search_and_replace(self.testspage, \
                               '<td tag=\'' + simulator.name + '\'.*</td></td>', \
                               HTML.csvcells_to_html(line))
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.pre_abort(''.join('!! ' + line for line in lines))
            abort('Aborting')
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

    def pre_abort(self, string):
        log = string_to_log ("=== Abort===\n\n" + string)

        abortpage = env.get_htmloutput_fullstring() + self.simulator.name + '-system-error.html'
        HTML.log_to_html (log, abortpage, self.simulator.name + ' System Traceback')

        search_and_replace_first (self.testspage, '<td tag=\'' + self.simulator.name + '\'.*</td></td>', \
                                  HTML.colspan(3, HTML.fail() + '(' +  HTML.lhref('Exception Log', abortpage) \
                                  + ')' ))
        
        search_and_replace_first (self.indexpage, self.simulator.name, 'FAILED')
        
        search_and_replace_first (self.indexpage, '<td tag=\'index[OKFAILED]*\'.*>log</a>\)</td>', \
                                HTML.csvcells_to_html(gettime() + ';' + HTML.fail() + ' (' + \
                                HTML.lhref('log', self.testspage) + ')' ))
        return '' 

