
import os
import subprocess
from .utils import *
from .html import *
import hashlib
from .benchbase import SimulatorInfo

class ArchC ():

    archc         = {}
    systemc       = {} 
    binutils      = {}
    gdb           = {}
    external_libs = []

    def __init__(self, _env):
        self.archc = {}
        self.archc['src']       = "/archc/src"
        self.archc['prefix']    = "/archc/install"
        self.archc['hash']      = '-'

        self.systemc = {}
        self.systemc['src']     = "/systemc/src"
        self.systemc['prefix']  = "/systemc/install"
        self.systemc['hash']    = '-'

        self.binutils = {}
        self.binutils['src'] = '/binutils/src/'
        self.gdb = {}
        self.gdb['src']      = '/gdb/src/'

        self.external_libs = []
        #self.external_libs['src']    = '/external/src'
        #self.external_libs['prefix'] = '/external/install'
        #self.external_libs['list']   = []

    def get_archc_src(self):
        return env.workspace + self.archc['src']

    def get_archc_prefix(self):
        return env.workspace + self.archc['prefix']

    def get_systemc_src(self):
        return env.workspace + self.systemc['src']

    def get_systemc_prefix(self):
        return env.workspace + self.systemc['prefix']

    def get_binutils_src(self):
        return env.workspace + self.binutils['src']

    def get_gdb_src(self):
        return env.workspace + self.gdb['src']

    def get_external_lib_src(self, lib):
        return env.workspace + lib['src']

    def get_external_lib_prefix(self, lib):
        return env.workspace + lib['prefix']

    def set_linkpath(self, linkpath):
        self.archc['link'] = linkpath
        get_tar_git_or_folder (linkpath, self.get_archc_src())
        if linkpath.endswith(".git") or linkpath.startswith("git"):
            self.archc['hash'] = get_githash(self.get_archc_src())

    def set_systemc(self, linkpath):
        self.systemc['link'] = linkpath
        get_tar_git_or_folder (linkpath, self.get_systemc_src())
        if linkpath.endswith(".git") or linkpath.startswith("git"):
            self.systemc['hash'] = get_githash(self.get_systemc_src())

    def set_binutils(self, linkpath):
        self.binutils['link'] = linkpath
        self.binutils['src']  = get_relative_path ( \
                    get_tar_git_or_folder (linkpath, self.get_binutils_src()))

    def set_gdb(self, linkpath):
        self.gdb['link'] = linkpath
        self.gdb['src']  = get_relative_path (\
                    get_tar_git_or_folder (linkpath, self.get_gdb_src()))

    def set_external_libs(self, name, link):
        lib = {}
        lib['name'  ] = name
        lib['link'  ] = link
        lib['hash'  ] = '-'
        lib['src'   ] = '/external/src/' + name
        lib['prefix'] = '/external/install/' + name
        self.external_libs.append(lib)

    def build_external_lib(self, lib):
        src    = self.get_external_lib_src(lib)
        prefix = self.get_external_lib_prefix(lib) 
        rm (src)
        get_tar_git_or_folder(lib['link'], src)
        if lib['link'].endswith(".git") or lib['link'].startswith("git"):
            lib['hash'] = get_githash(src)

        cmd_1  = "cd " + src + " && "
        cmd_2  = "autoreconf -vif && "
        cmd_2 += "./configure --prefix=" + prefix + " --enable-maintainer-mode && "
        cmd_2 += "make install"
        cmd = cmd_1 + cmd_2

        print(lib['name'] + ':')
        print("| " + cmd_2)
        print("| Building and Installing...", end="", flush=True)

        log = create_rand_file()
        execstatus = ''
        if exec_to_log(cmd, log):
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()
            
        # Creating the Build Page
        htmllog = env.htmloutput + "/" + env.testnumber + "-" + lib['name'] + "-build-log.html"
        HTML.log_to_html(log, htmllog,  lib['name'] + " build output")

        # Creating a csv line to add in the TestsPage (ArchC Table)
        csvline  = lib['name'] + ';' + lib['link'] + ';'
        csvline += lib['hash'][0:7] + ';' + execstatus
        csvline += '(' + HTML.lhref('log', htmllog) + ')'
        return csvline

    def build_systemc(self):
        if os.path.isdir(self.get_systemc_src()+"/lib"):
            cp (self.get_systemc_src(), self.get_systemc_prefix())
            csvline = 'SystemC;' + self.systemc['link'] + ";-;" + HTML.success() 
            return csvline
        else:
            cmd_1 = "cd "+self.get_systemc_src() + " && " 
            cmd_2 = ""
            if (self.get_systemc_src()+"/autogen.sh"):
                cmd_2 += "./autogen.sh && " 
            cmd_2 += "./configure --prefix=" + self.get_systemc_prefix() 
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

    def build_and_install_archc(self):

        extra_csvline = ""

        cmd_1 = "cd " + self.get_archc_src() + " && "
        cmd_2 = "./autogen.sh && " + \
                "./configure --prefix=" + self.get_archc_prefix()
        if 'link' in self.systemc:
            extra_csvline += self.build_systemc() + '\n'
            cmd_2 += " --with-systemc=" + self.get_systemc_prefix()
        if 'link' in self.binutils: 
            extra_csvline += 'Binutils;' + self.binutils['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-binutils=" + self.get_binutils_src()
        if 'link' in self.gdb:
            extra_csvline += 'GDB;' + self.gdb['link'] + ';-;' + HTML.success() + '\n'
            cmd_2 += " --with-gdb=" + self.get_gdb_src()
        for l in self.external_libs:
            extra_csvline += self.build_external_lib(l) + '\n'

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

    def reinstall_archc(self):
        for l in self.external_libs:
            cmd  = "cd " + self.get_external_lib_src(l) + " && "
            cmd += "./configure --prefix=" + self.get_external_lib_prefix(l) + " --enable-maintainer-mode && "
            cmd += "make install"
            exec_to_var ( cmd )

        cmd  = "cd "+self.get_systemc_src() + " && " 
        cmd += "./configure --prefix=" + self.get_systemc_prefix() + ' && '
        cmd += "make && make install"
        exec_to_var ( cmd ) 

        # Each model will change the GDB and BINUTILS folders
        cmd  = "cd " + self.get_archc_src() + " && "
        cmd += "./configure --prefix=" + self.get_archc_prefix()
        if 'link' in self.systemc:
            cmd += " --with-systemc=" + self.get_systemc_prefix()
        if 'link' in self.binutils: 
            cmd += " --with-binutils=" + self.get_binutils_src()
        if 'link' in self.gdb:
            cmd += " --with-gdb=" + self.get_gdb_src()
        cmd += " && make && make install"
        exec_to_var ( cmd )



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
        
        self.simfolder = "/" + self.name + '/'
        self.simsrc    = "/src/"

        self.model = {} 
        self.model['name']   = model
        self.model['hash']   = '-'
        self.model['endian'] = '' 
        self.model['run']    = run
        self.model['inputfile']  = inputfile
        self.model['link']   = ''
        self.model['branch'] = 'master'

        self.cross = {}
        self.cross['link']   = ''
        self.cross['prefix'] = ''

        self.benchmarks = []

        self.module = {}
        self.module['name'] = module
        self.module['generator'] = ""
        self.module['options']   = ""
        self.module['desc']      = None
        
        self.custom_links = {} 

    def get_name(self):
        return self.name

    def get_simfolder(self):
        return env.workspace + self.simfolder

    def get_simsrc(self):
        return self.get_simfolder() + self.simsrc

    def get_run_fullpath(self):
        return self.get_simsrc() + self.model['run']

    def set_modellink(self, linkpath, branch):
        self.model['link'] = linkpath
        if (self.model['link'].startswith("./")) or (self.model['link'].startswith("/")):
            self.model['hash']   = '-'
            self.model['branch'] = '-'
        else:
            self.model['hash']   = get_githash_online(linkpath, branch)
            self.model['branch'] = branch 

    def get_modellink(self):
        return self.model['link'] 

    def get_modelbranch(self):
        return self.model['branch']

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

    def download_modellink(self):
        if (self.model['link'].startswith("./")) or (self.model['link'].startswith("/")):
            get_local(self.model['link'], self.get_simsrc(), self.name)
        else:
            git_clone(self.model['link'], self.model['branch'], self.get_simsrc(), self.name)

        with open(self.get_simsrc() + self.model['inputfile'], 'r') as f:
            for l in f:
                s = re.search(r'set_endian\("(.*)"\)', l)
                if s:
                    self.model['endian'] = s.group(1)

    def gen_and_build(self):
        self.download_modellink()
        cmd_source = 'source '+env.get_archcenv()+' && '
        cmd_cd     = "cd " + self.get_simsrc() + " && "
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
        self.cross['prefix'] = get_tar_git_or_folder(self.cross['link'], env.get_xtoolsfolder())+'/bin/'
        for bench in self.benchmarks:
            print('|--- ' + bench.name + ' ---', flush=True)
            benchfolder = self.get_simfolder() + '/benchmark/' + bench.name + '/'
            mkdir(benchfolder)
            bench.download(benchfolder)
            simulator_info = SimulatorInfo()
            simulator_info.crossbin = self.cross['prefix']
            simulator_info.arch     = self.model['name']
            simulator_info.endian   = self.model['endian']
            simulator_info.name     = self.name
            simulator_info.run      = self.get_run_fullpath()
            bench.run_tests(simulator_info)
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
            
