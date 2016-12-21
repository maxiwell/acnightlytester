
import os, glob
import subprocess
from .utils import *
from .html import *
import hashlib
from .benchbase import SimulatorInfo

class ArchC ():

    archc         = {}
    external_libs = []

    def __init__(self, _env):
        self.archc = {}
        self.archc['src']       = "/archc/src"
        self.archc['prefix']    = "/archc/install"
        self.archc['hash']      = '-'

        self.external_libs = []

    def get_archc_src(self):
        return env.workspace + self.archc['src']

    def get_archc_prefix(self):
        return env.workspace + self.archc['prefix']

    def get_archc_hashtohtml(self):
        return HTML.get_link_from_githash(self.archc['hash'], self.archc['link'])

    def get_external_lib_by_name(self, libname):
        for l in self.external_libs:
            if l['name'] == libname:
                return l
        return None

    def get_external_lib_src(self, lib):
        return env.workspace + lib['src'];

    def get_external_lib_prefix(self, lib):
        return env.workspace + lib['prefix'];

    def get_external_libs_PKG_CONFIG_PATH(self):
        pkg_config_path = '$PKG_CONFIG_PATH'
        for l in self.external_libs:
            for d in glob.glob(env.workspace + l['prefix'] + '/lib*/pkgconfig'):
                pkg_config_path = d + ":" + pkg_config_path
        return pkg_config_path

    def get_external_libs_LD_LIBRARY_PATH(self):
        ld_library_path = '$LD_LIBRARY_PATH'
        for l in self.external_libs:
            for d in glob.glob (env.workspace + l['prefix'] + '/lib*'): 
                ld_library_path = d + ":" + ld_library_path 
        return ld_library_path

    def get_external_libs_PATH(self):
        path = '$PATH'
        for l in self.external_libs:
            path += env.workspace + l['prefix'] + '/bin:' + path
        return path
    
    def set_linkpath(self, linkpath):
        self.archc['link'] = linkpath
        self.archc['src']  = get_relative_path ( 
                                get_tar_git_or_folder ( 
                                    linkpath, 
                                    self.get_archc_src()
                                )
                            )
        if is_linkpath_a_git (linkpath):
            self.archc['hash'] = get_githash(self.get_archc_src())

    def set_external_libs(self, name, link, branch, cmd):
        lib = {}
        lib['name'  ] = name
        lib['link'  ] = link
        lib['branch'] = branch
        lib['cmd'   ] = cmd
        lib['hash'  ] = '-'
        lib['src'   ] = '/external/src/' + name
        lib['prefix'] = '/external/install/' + name
        self.external_libs.append(lib)

    def build_external_lib(self, lib):
        src    = self.get_external_lib_src(lib)
        prefix = self.get_external_lib_prefix(lib) 
        cmd    = lib['cmd']
        branch = lib['branch']
        if is_linkpath_a_git (lib['link']): 
            git_clone(lib['link'], lib['branch'], src)
            lib['hash'] = get_githash(src)
        else:
            src = get_tar_git_or_folder(lib['link'], src)

        pre  = "cd " + src + " && "
        cmd  = re.sub(r"make", inflate("make"), cmd)
        cmd  = re.sub(r"\./configure", "./configure --prefix=" + prefix, cmd)

        allcmd = pre + cmd
        print(lib['name'] + ':')
        print("| " + cmd)
        print("| Building and Installing...", end="", flush=True)

        retcode, log = exec_to_log(allcmd)
        execstatus = ''
        if  retcode:
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()
            
        # Creating the Build Page
        htmllog = env.get_htmloutput_fullstring() + lib['name'] + "-build-log.html"
        HTML.log_to_html(log, htmllog,  lib['name'] + " build output")

        # Creating a csv line to add in the TestsPage (ArchC Table)
        csvline  = lib['name'] + ';' + lib['link'] + ';'
        csvline += HTML.get_link_from_githash(lib['hash'], lib['link']) + ';' + execstatus
        csvline += '(' + HTML.lhref('log', htmllog) + ')'
        return csvline

    def build_and_install_archc(self):

        extra_csvline = ""
        for l in self.external_libs:
            extra_csvline += self.build_external_lib(l) + '\n'

        cmd_1  = 'export PKG_CONFIG_PATH="' + self.get_external_libs_PKG_CONFIG_PATH() + '" && '
        cmd_1 += 'export LD_LIBRARY_PATH="' + self.get_external_libs_LD_LIBRARY_PATH() + '" && '
        cmd_1 += "cd " + self.get_archc_src() + " && "
        if os.path.isfile( self.get_archc_src() + '/Makefile' ):
            cmd_1 += "make distclean && "
        cmd_2  = "./autogen.sh && " 
        cmd_2 += "./configure --prefix=" + self.get_archc_prefix()
        for ext in ['systemc', 'binutils', 'gdb']:
            lib = self.get_external_lib_by_name(ext)
            if lib != None:
                cmd_2 += " --with-"+ext+"=" + self.get_external_lib_prefix(lib)
        cmd_2 += " && " + inflate("make") + " && " + inflate("make install")
        print("ArchC:")
        print("| "+cmd_2)
        print("| Building and Installing... ", end="", flush=True)
        cmd = cmd_1 + cmd_2

        retcode, log = exec_to_log(cmd)
        execstatus = ''
        if retcode: 
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()

        # Creating the Build Page
        htmllog = env.get_htmloutput_fullstring() + "archc-build-log.html"
        HTML.log_to_html(log, htmllog, "ArchC rev "+self.archc['hash'][0:7]+" build output")
        
        # Creating a csv line to add in the TestsPage (ArchC Table)
        csvline = 'ArchC;' + self.archc['link'] + ';' 
        csvline += HTML.get_link_from_githash(self.archc['hash'], self.archc['link']) + ';' 
        csvline += execstatus
        csvline += '(' + HTML.lhref('log', htmllog) + ');'
       
        return csvline + '\n' + extra_csvline + '\n'

    def reinstall_archc(self):
        for l in self.external_libs:
            pre  = "cd " + self.get_external_lib_src(l) + " && "
            cmd  = re.sub(r"make", inflate("make"), l['cmd'])
            cmd  = re.sub(r"\./configure", "./configure --prefix=" + self.get_external_lib_prefix(l), cmd)
            allcmd = pre + cmd
            exec_to_var ( allcmd )

        # Each model will change the GDB and BINUTILS folders
        cmd  = 'export PKG_CONFIG_PATH="' + self.get_external_libs_PKG_CONFIG_PATH() + '" && '
        cmd += 'export LD_LIBRARY_PATH="' + self.get_external_libs_LD_LIBRARY_PATH() + '" && '
        cmd += "cd " + self.get_archc_src() + " && "
        cmd += "./configure --prefix=" + self.get_archc_prefix()
        for ext in ['systemc', 'binutils', 'gdb']:
            lib = self.get_external_lib_by_name(ext)
            if lib != None:
                cmd += " --with-"+ext+"=" + self.get_external_lib_prefix(lib)
        cmd += " && " + inflate("make") + " && " + inflate("make install")
        exec_to_var ( cmd )


class Simulator (SimulatorPage):
    name        = ""
    identifier  = ""

    model       = {}
    cross       = {}
    module      = {}

    benchmarks  = []

    custom_links = {}

    def __init__(self, model, module, run, inputfile):
        self.name = model + '-' + module
        super().__init__(self.name)
        
        self.identifier = get_random()
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

    def get_identifier(self):
        return self.identifier

    def get_simfolder(self):
        return env.workspace + self.simfolder

    def get_simsrc(self):
        return self.get_simfolder() + self.simsrc

    def get_run_fullpath(self):
        return self.get_simsrc() + self.model['run']

    def get_inputfile(self):
        return self.model['inputfile']

    def set_modellink(self, linkpath, branch):
        self.model['link'] = linkpath
        if is_linkpath_a_git(self.model['link']):
            self.model['hash']   = get_githash_online(linkpath, branch)
            self.model['branch'] = branch 
        else:
            self.model['hash']   = '-'
            self.model['branch'] = '-'

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

    def get_cross_csvline(self):
        # Find the cross version and write the page
        prefix, crossversion, crossdump = env.get_xtools_cache(self.cross['link'])
        if prefix == None:
            prefix = get_tar_git_or_folder(self.cross['link'], env.get_xtoolsfolder()) + '/bin/'
            crosscmd = 'cd ' + prefix + ' && `find . -iname "*-gcc"` '
            crossversion = exec_to_var( crosscmd + "--version | awk '/gcc/ {print $4;}'")
            retcode, crossdump = exec_to_log ( crosscmd + '-v' )
            env.add_xtools_cache(self.cross['link'], prefix, crossversion, crossdump)
            
        highlight_list = ['--with-float=soft', '--with-newlib']
        crosspage = env.get_htmloutput_fullstring() + self.model['name'] + '-cross-version.html'
        HTML.log_to_html( crossdump, crosspage, self.model['name'] + ' Cross Version', highlight_list)
        
        csvline  = 'GCC Cross ' + self.model['name'] + ';' + self.cross['link'] + ';' 
        csvline += crossversion + ';' + HTML.success() + ' (' + HTML.lhref('version', crosspage) + ')\n'
        rm (env.get_xtoolsfolder())

        return csvline

    def set_modelhash(self, githash):
        self.model['hash'] = githash

    def get_modelhash(self):
        return self.model['hash'] 

    def get_model_hashtohtml(self):
        return HTML.get_link_from_githash(self.model['hash'], self.model['link'])

    def get_model_inputtohtml(self):
        return HTML.get_link_from_file(self.model['hash'], self.model['inputfile'], self.model['link'])

    def set_custom_links(self, link, cmdline):
        self.custom_links[link] = cmdline

    def append_benchmark(self, benchmark):
        benchmark.custom_links   = self.custom_links
        benchmark.simulator_name = self.get_name()
        self.benchmarks.append(benchmark)

    def download_modellink(self):
        if (is_linkpath_a_git(self.model['link'])):
            git_clone(self.model['link'], self.model['branch'], self.get_simsrc(), self.get_name())
        else:
            get_local(self.model['link'], self.get_simsrc(), self.get_name())

        with open(self.get_simsrc() + self.model['inputfile'], 'r') as f:
            for l in f:
                s = re.search(r'set_endian\("(.*)"\)', l)
                if s:
                    self.model['endian'] = s.group(1)

    def gen_and_build(self):
        self.download_modellink()
        cmd_source = 'source '+env.get_archcenv()+' && '
        cmd_cd     = "cd " + self.get_simsrc() + " && "
        if os.path.isfile(self.get_simsrc() + '/Makefile'):
            cmd_cd += "make distclean && "
        cmd_acsim  = self.module['generator'] + " " + self.model['inputfile'] + " " \
                    + self.module['options'] + " && "
        cmd_make   = inflate("make")

        cmd = cmd_source + cmd_cd + cmd_acsim + cmd_make 
        print(self.get_name() + ":")
        print("| "+cmd)
        print("| Generating and Building... ", end="", flush=True)

        retcode, log = exec_to_log(cmd)
        execstatus = ''
        if retcode:
            print("OK")
            execstatus = HTML.success()
        else:
            print("FAILED")
            execstatus = HTML.fail()

        # Creating the Build Page
        buildpage = env.get_htmloutput_fullstring() + self.get_name() + "-build-log.html"
        HTML.log_to_html(log, buildpage, self.get_name() + " rev "+self.model['hash'][0:7]+" build output")

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
            simulator_info.name     = self.get_name()
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
        cpuinfofile = env.get_htmloutput_fullstring() + self.get_name() + "-cpuinfo.txt"
        meminfofile = env.get_htmloutput_fullstring() + self.get_name() + "-meminfo.txt"

        exec_to_log("cat /proc/cpuinfo", cpuinfofile)        
        exec_to_log("cat /proc/meminfo", meminfofile)        
        
        # Finishing the csv line with the tests results to add in the TestsPage (Tests Table)
        tableline = test_results + '(' + HTML.lhref('report', self.page) + ');' + hostname + \
                                   ' (' + HTML.lhref('cpuinfo', cpuinfofile) + ', ' + \
                                          HTML.lhref('meminfo', meminfofile) + ');'
        return tableline


    def printsim(self):
        print("Simulator: " + self.get_name())
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
            
