
import os
import subprocess
from .utils import *
from .html import *
import hashlib

class ArchC ():

    archc   = {}
    systemc = {} 

    def update_paths(self):
        self.archc['src']       = env.workspace + "/archc/src"
        self.archc['prefix']    = env.workspace + "/archc/install"
        self.archc['hash']      = '-'

        self.systemc['src']     = env.workspace + "/systemc/src"
        self.systemc['prefix']  = env.workspace + "/systemc/install"
        self.systemc['hash']    = '-'

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
        env.binutils['link'] = linkpath
        env.binutils['src']  = get_tar_git_or_folder (linkpath, env.binutils['src'])

    def set_gdb(self, linkpath):
        env.gdb['link'] = linkpath
        env.gdb['src']  = get_tar_git_or_folder (linkpath, env.gdb['src'])

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
        if 'link' in env.binutils: 
            extra_csvline += 'Binutils;' + env.binutils['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-binutils=" + env.binutils['src']
        if 'link' in env.gdb:
            extra_csvline += 'GDB;' + env.gdb['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-gdb=" + env.gdb['src']
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

    module      = ""
    generator   = ""
    options     = ""
    desc        = ""

    crosslink   = ""
    cross       = ""
    endian      = ""

    run         = ""
    inputfile   = ""
    linkpath    = ""
    simfolder   = ""
    simsrc      = ""

    benchmarks  = []

    custom_links = {}

    def __init__(self, name, model, module, run, inputfile):
        super().__init__(name)
        self.name = name
        
        self.model['name'] = model
        self.model['hash'] = '-'

        self.inputfile = inputfile
        self.linkpath = ""
        self.benchmarks = []

        self.module    = module
        self.generator = ""
        self.options   = ""
        self.desc      = "mips"
        
        self.simfolder = env.workspace + "/" + name + '/'
        self.simsrc    = self.simfolder + "/src/"
        self.run       = self.simsrc + run
        
        self.custom_links = {} 

    def set_linkpath(self, linkpath):
        self.linkpath = linkpath
        if (self.linkpath.startswith("./")) or (self.linkpath.startswith("/")):
            get_local(self.linkpath, self.simsrc, self.name)
        else:
            git_clone(self.linkpath, self.simsrc, self.name)

        self.model['hash'] = get_githash(self.simsrc)
        with open(self.simsrc + self.inputfile, 'r') as f:
            for l in f:
                s = re.search(r'set_endian\("(.*)"\)', l)
                if s:
                    self.endian = s.group(1)

    def set_generator(self, generator):
        self.generator = generator

    def set_options(self, options):
        self.options = options

    def set_desc(self, desc):
        self.desc = desc

    def set_cross(self, path):
        self.crosslink = path

    def set_custom_links(self, link, cmdline):
        self.custom_links[link] = cmdline

    def append_benchmark(self, benchmark):
        benchmark.custom_links   = self.custom_links
        benchmark.simulator_name = self.name
        self.benchmarks.append(benchmark)

    def gen_and_build(self):
        cmd_source = 'source '+env.archc_envfile+' && '
        cmd_cd     = "cd " + self.simsrc + " && "
        cmd_acsim  = self.generator + " " + self.inputfile + " " \
                    + self.options + " && "
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
        self.cross = get_tar_git_or_folder(self.crosslink, env.xtoolsfolder)+'/bin/'
        for bench in self.benchmarks:
            print('|--- ' + bench.name + ' ---', flush=True)
            bench.download(self.simfolder+'/benchmark/')
            bench.run_tests(self.cross, self.endian, self.name, self.run)
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
        print("| - from " + self.linkpath)
        print("| module: "+ self.module)
        print("| - generator: " + self.generator)
        print("| - options: " + self.options )
        if (self.desc):
            print("| - desc: " + self.desc )
        print("| benchmark: ", end="")
        for b in self.benchmarks:
            print("["+b.name+"] ", end="")
        print()
            
