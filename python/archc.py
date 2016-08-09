
import os
import subprocess
from .utils import *
from .html import *
import hashlib

class ArchC ():

    archc     = ""
    systemc   = ""
    binutils  = "" 
    gdb       = ""

    archc_src    = "archc/src"
    archc_prefix = "archc/install"
    archc_hash   = ""

    systemc_src    = "systemc/src"
    systemc_prefix = "systemc/install"
    systemc_hash   = ""

    binutils_src    = "binutils/src"
    binutils_prefix = "binutils/instsall"

    gdb_src         = "gdb/src"
    gdb_prefix      = "gdb/install"

    def update_paths(self):
        self.archc_src       = env.workspace + "/" + self.archc_src
        self.archc_prefix    = env.workspace + "/" + self.archc_prefix
        self.systemc_src     = env.workspace + "/" + self.systemc_src
        self.systemc_prefix  = env.workspace + "/" + self.systemc_prefix
        self.binutils_src    = env.workspace + "/" + self.binutils_src
        self.binutils_prefix = env.workspace + "/" + self.binutils_prefix
        self.gdb_src         = env.workspace + "/" + self.gdb_src
        self.gdb_prefix      = env.workspace + "/" + self.gdb_prefix

    def set_linkpath(self, linkpath):
        self.archc = linkpath
        if (linkpath.startswith("./")) or (linkpath.startswith("/")):
            get_local(linkpath, self.archc_src, "ArchC")
            self.archc_hash = '-'
        else:
            git_clone(linkpath, self.archc_src, "ArchC")
            self.archc_hash = get_githash(self.archc_src)

    def set_systemc(self, linkpath):
        self.systemc = linkpath
        if (linkpath.startswith("./")) or (linkpath.startswith("/")):
            get_local(linkpath, self.systemc_src, "SystemC")
            self.archc_hash = '-'
        else:
            git_clone(linkpath, self.systemc_src, "SystemC")
            self.systemc_hash = get_githash(self.systemc_src)

    def set_binutils(self, linkpath):
        self.binutils = linkpath
#        if self.binutils :
#            get_from( url_or_path = linkpath, \
#                    copy_to = self.binutils_src, pkg = "Binutils")

    def set_gdb(self, linkpath):
        self.gdb = linkpath
#        if self.gdb :
#            get_from( url_or_path = linkpath, \
#                    copy_to = self.gdb_src, pkg = "GDB")

    def build_systemc(self):
        if os.path.isdir(self.systemc_src+"/lib"):
            cp (self.systemc_src, self.systemc_prefix)
            csvline = 'SystemC;' + self.systemc + ";-;" + HTML.success() 
            return csvline
        else:
            cmd_1 = "cd "+self.systemc_src + " && " 
            cmd_2 = ""
            if (self.systemc_src+"/autogen.sh"):
                cmd_2 += "./autogen.sh && " 
            cmd_2 += "./configure --prefix=" + self.systemc_prefix 
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
            HTML.log_to_html(log, htmllog, "SystemC rev " + self.systemc_hash[0:7] + " build output")

            # Creating a csv line to add in the TestsPage (ArchC Table)
            csvline = 'SystemC;' + self.systemc + ';'
            csvline += HTML.href(self.systemc_hash[0:7], \
                                self.systemc.replace('.git','') + '/commit/' + \
                                self.systemc_hash) + ';'

            csvline += execstatus
            csvline += '(' + HTML.lhref('log', htmllog) + ')'
            return csvline

    def build_archc(self):

        systemc_csvline = ""
        if self.systemc:
            systemc_csvline = self.build_systemc()

        cmd_1 = "cd " + self.archc_src + " && "
        cmd_2 = "./autogen.sh && " + \
                "./configure --prefix=" + self.archc_prefix
        if self.systemc:
            cmd_2 += " --with-systemc=" + self.systemc_prefix
        if self.binutils: 
            cmd_2 += " --with-binutils=" + self.binutils_src
        if self.gdb:
            cmd_2 += " --with-gdb=" + self.gdb_src
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
        HTML.log_to_html(log, htmllog, "ArchC rev "+self.archc_hash[0:7]+" build output")
        
        # Creating a csv line to add in the TestsPage (ArchC Table)
        csvline = 'ArchC;' + self.archc + ';' 
        if self.archc_hash != '-' :
            csvline += HTML.href(self.archc_hash[0:7], \
                                 self.archc.replace('.git','') + '/commit/' + self.archc_hash ) + ';'
        else:
            csvline += self.archc_hash[0:7] + ';'

        csvline += execstatus
        csvline += '(' + HTML.lhref('log', htmllog) + ')'
        
        return csvline + '\n' + systemc_csvline


class Simulator (SimulatorPage):
    name        = ""
    model       = ""

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

    model_hash  = ""

    benchmarks  = []

    custom_links = {}

    def __init__(self, name, model, module, run, inputfile):
        super().__init__(name)
        self.name = name
        self.model = model
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
            self.model_hash = '-'
        else:
            git_clone(self.linkpath, self.simsrc, self.name)

        self.model_hash = get_githash(self.simsrc)
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
        HTML.log_to_html(log, buildpage, self.name + " rev "+self.model_hash[0:7]+" build output")

        tableline  = execstatus
        tableline += '(' + HTML.lhref('log', buildpage) + ')' + ';'
        return tableline

    def run_tests(self):
        self.cross = get_bz2_or_folder(self.crosslink, env.xtoolsfolder)+'/bin/'
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
        print("| model: " + self.model)
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
            
