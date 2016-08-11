
import os
import subprocess
from .utils import *
from .html import *
import hashlib

class ArchC ():

    archc       = {}
    systemc     = {} 
    binutils    = {}
    gdb         = {}

    def update_paths(self):
        self.archc['src']       = env.workspace + "/archc/src"
        self.archc['prefix']    = env.workspace + "/archc/install"
        self.archc['hash']      = '-'

        self.systemc['src']     = env.workspace + "/systemc/src"
        self.systemc['prefix']  = env.workspace + "/systemc/install"
        self.systemc['hash']    = '-'

        self.binutils['src'] = env.workspace + '/binutils/src/'
        self.gdb['src']      = env.workspace + '/gdb/src/'


    def set_linkpath(self, linkpath):
        self.archc['link'] = linkpath
        get_tar_git_or_folder (linkpath, self.archc['src'])
        if (linkpath.endswith(".git")):
            self.archc['hash'] = get_githash(self.archc['src'])

    def set_systemc(self, linkpath):
        self.systemc['link'] = linkpath
        get_tar_git_or_folder (linkpath, self.systemc['src'])
        if (linkpath.endswith(".git")):
            self.systemc['hash'] = get_githash(self.systemc['src'])

    def set_binutils(self, linkpath):
        self.binutils['link'] = linkpath
        self.binutils['src']  = get_tar_git_or_folder (linkpath, self.binutils['src'])

    def set_gdb(self, linkpath):
        self.gdb['link'] = linkpath
        self.gdb['src']  = get_tar_git_or_folder (linkpath, self.gdb['src'])

    def build_systemc(self):
        if os.path.isdir(self.systemc['src']+"/lib"):
            cp (self.systemc['src'], self.systemc['prefix'])
            csvline = 'SystemC;' + self.systemc['link'] + ";-;" + HTML.success() 
            return csvline
        else:
            cmd_1 = "cd "+self.systemc['src'] + " && " 
            cmd_2 = ""
            if (self.systemc['src']+"/autogen.sh"):
                cmd_2 += "./autogen.sh && " 
            cmd_2 += "./configure --prefix=" + self.systemc['prefix'] 
            cmd_2 += " && make && make install"
            print("SystemC:")
            print("| " + cmd_2)
            print("| Building and Installing...", end="", flush=True)
            cmd = cmd_1 + cmd_2

            log = create_rand_file()
            execstatus = ''
            if exec_to_log(cmd, log):
                print("OK")
                execstatus = HTML.success()
            else:
                print("FAILED")
                execstatus = HTML.fail()

            # Creating the Build Page
            htmllog = env.htmloutput + "/" + env.testnumber + "-systemc-build-log.html"
            HTML.log_to_html(log, htmllog, "SystemC rev " + self.systemc['hash'][0:7] + " build output")

            # Creating a csv line to add in the TestsPage (ArchC Table)
            csvline = 'SystemC;' + self.systemc['link'] + ';'
            csvline += HTML.href(self.systemc['hash'][0:7], \
                                self.systemc['link'].replace('.git','') + '/commit/' + \
                                self.systemc['hash']) + ';'

            csvline += execstatus
            csvline += '(' + HTML.lhref('log', htmllog) + ')'
            return csvline

    def build_archc(self):

        extra_csvline = ""

        cmd_1 = "cd " + self.archc['src'] + " && "
        cmd_2 = "./autogen.sh && " + \
                "./configure --prefix=" + self.archc['prefix']
        if 'link' in self.systemc:
            extra_csvline += self.build_systemc() + '\n'
            cmd_2 += " --with-systemc=" + self.systemc['prefix']
        if 'link' in self.binutils: 
            extra_csvline += 'Binutils;' + self.binutils['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-binutils=" + self.binutils['src']
        if 'link' in self.gdb:
            extra_csvline += 'GDB;' + self.gdb['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-gdb=" + self.gdb['src']
        cmd_2 += " && make && make install"
        print("ArchC:")
        print("| "+cmd_2)
        print("| Building and Installing... ", end="", flush=True)
        cmd = cmd_1 + cmd_2

        log = create_rand_file()
        execstatus = ''
        if exec_to_log(cmd, log): 
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()

        # Creating the Build Page
        htmllog = env.htmloutput + "/" + env.testnumber + "-archc-build-log.html"
        HTML.log_to_html(log, htmllog, "ArchC rev "+self.archc['hash'][0:7]+" build output")
        
        # Creating a csv line to add in the TestsPage (ArchC Table)
        csvline = 'ArchC;' + self.archc['link'] + ';' 
        if self.archc['hash'] != '-' :
            csvline += HTML.href(self.archc['hash'][0:7], \
                                 self.archc['link'].replace('.git','') + '/commit/' + self.archc['hash'] ) + ';'
        else:
            csvline += self.archc['hash'][0:7] + ';'

        csvline += execstatus
        csvline += '(' + HTML.lhref('log', htmllog) + ')'
       
        return csvline + '\n' + extra_csvline


class Simulator (SimulatorPage):
    name        = ""

    model       = {}
    cross       = {}
    module      = {}

    benchmarks  = []

    custom_links = {}

    def __init__(self, model, module, run, inputfile):
        self.name = model + '-' + module
        super().__init__(self.name)
        
        self.simfolder = env.workspace + "/" + self.name + '/'
        self.simsrc    = self.simfolder + "/src/"
        
        self.model['name']   = model
        self.model['hash']   = '-'
        self.model['endian'] = '' 
        self.model['run']    = self.simsrc + run
        self.model['inputfile']  = inputfile
        self.model['link']   = ''

        self.cross['link']   = ''
        self.cross['prefix'] = ''

        self.benchmarks = []

        self.module['name'] = module
        self.module['generator'] = ""
        self.module['options']   = ""
        self.module['desc']      = None
        
        self.custom_links = {} 

    def get_name(self):
        return self.name

    def set_modellink(self, linkpath):
        self.model['link'] = linkpath
        if (self.model['link'].startswith("./")) or (self.model['link'].startswith("/")):
            get_local(self.model['link'], self.simsrc, self.name)
        else:
            git_clone(self.model['link'], self.simsrc, self.name)

        self.model['hash'] = get_githash(self.simsrc)
        with open(self.simsrc + self.model['inputfile'], 'r') as f:
            for l in f:
                s = re.search(r'set_endian\("(.*)"\)', l)
                if s:
                    self.model['endian'] = s.group(1)

    def get_modellink(self):
        return self.model['link'] 

    def set_generator(self, generator):
        self.module['generator'] = generator

    def get_generator(self):
        return self.module['generator'] 

    def set_options(self, options):
        self.module['options'] = options

    def get_options(self):
        return self.module['options'] 

    def set_desc(self, desc):
        self.module['desc'] = desc

    def get_desc(self):
        return self.module['desc']

    def set_crosslink(self, path):
        self.cross['link'] = path

    def get_crosslink(self):
        return self.cross['link']

    def set_modelhash(self, githash):
        self.model['hash'] = githash

    def get_modelhash(self):
        return self.model['hash'] 

    def set_custom_links(self, link, cmdline):
        self.custom_links[link] = cmdline

    def append_benchmark(self, benchmark):
        benchmark.custom_links   = self.custom_links
        benchmark.simulator_name = self.name
        self.benchmarks.append(benchmark)

    def gen_and_build(self):
        cmd_source = 'source '+env.archc_envfile+' && '
        cmd_cd     = "cd " + self.simsrc + " && "
        cmd_acsim  = self.module['generator'] + " " + self.model['inputfile'] + " " \
                    + self.module['options'] + " && "
        cmd_make   = "make "

        cmd = cmd_source + cmd_cd + cmd_acsim + cmd_make 
        print(self.name + ":")
        print("| "+cmd)
        print("| Generating and Building... ", end="", flush=True)

        log = create_rand_file()
        execstatus = ''
        if exec_to_log(cmd, log):
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()

        # Creating the Build Page
        buildpage = env.htmloutput + "/" + env.testnumber + "-" + self.name + "-build-log.html"
        HTML.log_to_html(log, buildpage, self.name + " rev "+self.model['hash'][0:7]+" build output")

        tableline  = execstatus
        tableline += '(' + HTML.lhref('log', buildpage) + ')' + ';'
        return tableline

    def run_tests(self):
        self.cross['prefix'] = get_tar_git_or_folder(self.cross['link'], env.xtoolsfolder)+'/bin/'
        for bench in self.benchmarks:
            print('|--- ' + bench.name + ' ---', flush=True)
            benchfolder = self.simfolder + '/benchmark/' + bench.name
            mkdir(benchfolder)
            bench.download(benchfolder)
            bench.run_tests(self.cross['prefix'], self.model['endian'], self.name, self.model['run'])
            self.create_benchmark_table(bench)

        self.close_sim_page()

        test_results = ""
        if had_failed(self.page):
            test_results = HTML.fail()
        else:
            test_results = HTML.success()

        hostname = gethostname()
        cpuinfofile = env.htmloutput + "/" + env.testnumber + "-" + self.name + "-cpuinfo.txt"
        meminfofile = env.htmloutput + "/" + env.testnumber + "-" + self.name + "-meminfo.txt"

        exec_to_log("cat /proc/cpuinfo", cpuinfofile)        
        exec_to_log("cat /proc/meminfo", meminfofile)        
        
        # Finishing the csv line with the tests results to add in the TestsPage (Tests Table)
        tableline = test_results + '(' + HTML.lhref('report', self.page) + ');' + hostname + \
                                   ' (' + HTML.lhref('cpuinfo', cpuinfofile) + ', ' + \
                                          HTML.lhref('meminfo', meminfofile) + ');'
        return tableline


    def printsim(self):
        print("Simulator: " + self.name)
        print("| model: " + self.model['name'])
        print("| - from " + self.model['link'])
        print("| module: "      + self.module['name'])
        print("| - generator: " + self.module['generator'])
        print("| - options: "   + self.module['options'] )
        if self.module['desc'] != None:
            print("| - desc: " + self.module['desc'] )
        print("| benchmark: ", end="")
        for b in self.benchmarks:
            print("["+b.name+"] ", end="")
        print()
            
