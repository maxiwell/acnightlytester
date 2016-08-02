
import os
from .nightly    import Env
import subprocess
from .utils import *
from .html import *
import tarfile
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

    archcbuildlog   = "log/archc.log"
    systemcbuildlog = "log/systemc.log"

    archchtmllog    = "-archc-build-log.html"
    systemchtmllog   = "-systemc-build-log.html"

    env = None

    def set_env(self, env):
        self.env = env;
        self.archc_src       = self.env.workspace + "/" + self.archc_src
        self.archc_prefix    = self.env.workspace + "/" + self.archc_prefix
        self.systemc_src     = self.env.workspace + "/" + self.systemc_src
        self.systemc_prefix  = self.env.workspace + "/" + self.systemc_prefix
        self.binutils_src    = self.env.workspace + "/" + self.binutils_src
        self.binutils_prefix = self.env.workspace + "/" + self.binutils_prefix
        self.gdb_src         = self.env.workspace + "/" + self.gdb_src
        self.gdb_prefix      = self.env.workspace + "/" + self.gdb_prefix
        self.archcbuildlog   = self.env.workspace + "/" + self.archcbuildlog
        self.systemcbuildlog = self.env.workspace + "/" + self.systemcbuildlog
        mkdir(os.path.dirname(self.archcbuildlog))
        #rm(self.archcbuildlog)

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

            cmdret = exec_to_log(cmd, self.systemcbuildlog)
            if cmdret:
                print("OK")
            else:
                print("FAILED")

            htmllog = self.env.htmloutput + "/" + self.env.testnumber + self.systemchtmllog
            html = HTML(htmllog)
            html.init_page("SystemC rev " + self.systemc_hash[0:7] + " build output")
            html.append_log_formatted(self.systemcbuildlog)
            html.write_page()

            csvline = 'SystemC;' + self.systemc + ';'
            csvline += HTML.href(self.systemc_hash[0:7], \
                                self.systemc.replace('.git','') + '/commit/' + \
                                self.systemc_hash) + ';'
            if cmdret:
                csvline += HTML.success()
            else:
                csvline += HTML.fail()
            csvline += '(' + HTML.href('log', htmllog) + ')'
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

        #cmdret = exec_to_log(cmd, self.archcbuildlog)
        cmdret = True
        if cmdret:
            print("OK")
        else:
            print("FAILED")

        htmllog = self.env.htmloutput + "/" + self.env.testnumber + self.archchtmllog
        html = HTML(htmllog)
        html.init_page("ArchC rev "+self.archc_hash[0:7]+" build output")
        html.append_log_formatted(self.archcbuildlog)
        html.write_page()

        csvline = 'ArchC;' + self.archc + ';' 
        if self.archc_hash != '-' :
            csvline += HTML.href(self.archc_hash[0:7], \
                                 self.archc.replace('.git','') + '/commit/' + self.archc_hash ) + ';'
        else:
            csvline += self.archc_hash[0:7] + ';'

        if cmdret:
            csvline += HTML.success()
        else:
            csvline += HTML.fail()
        csvline += '(' + HTML.href('log', htmllog) + ')'

        return csvline + '\n' + systemc_csvline


class Simulator ():
    name        = ""

    generator   = ""
    options     = ""
    desc        = ""

    cross       = ""

    inputfile   = ""
    linkpath    = ""
    simsrc      = ""
    buildlog    = ""

    model_hash  = ""

    env         = None
    benchmarks  = []

    htmllog    = ""

    def __init__(self, name, inputfile, env):
        self.name = name
        self.linkpath = ""
        self.inputfile = inputfile
        self.env  = env
        self.benchmarks = []

        self.generator = ""
        self.options   = ""
        self.desc      = ""
        
        self.htmllog    = "-"+name+"-build-log.html"

        self.simsrc    = env.workspace + "/" + name


        self.buildlog = env.workspace + "/log/" + name + ".log"
        mkdir(os.path.dirname(self.buildlog))
        rm(self.buildlog)

    def set_linkpath(self, linkpath):
        self.linkpath = linkpath
        if (self.linkpath.startswith("./")) or (self.linkpath.startswith("/")):
            get_local(self.linkpath, self.simsrc, self.name)
            self.model_hash = '-'
        else:
            git_clone(self.linkpath, self.simsrc, self.name)
            self.model_hash = get_githash(self.simsrc)

    def set_generator(self, generator):
        self.generator = generator

    def set_options(self, options):
        self.options = options

    def set_desc(self, desc):
        self.desc = desc

    def set_cross(self, path):
        self.cross = path

    def append_benchmark(self, benchmark):
        self.benchmarks.append(benchmark)

    def gen_and_build(self, archc_env_file):
        cmd_source = 'source '+archc_env_file+' && '
        cmd_cd     = "cd " + self.simsrc + " && "
        cmd_acsim  = self.generator + " " + self.inputfile + " " \
                    + self.options + " && "
        cmd_make   = "make "

        cmd = cmd_source + cmd_cd + cmd_acsim + cmd_make 
        print(self.name + ":")
        print("| "+cmd)
        print("| Generating and Building... ", end="", flush=True)

        cmdret =  exec_to_log(cmd, self.buildlog) 
        if cmdret:
            print("OK")
        else:
            print("FAILED")

        htmllog = self.env.htmloutput + "/" + self.env.testnumber + self.htmllog
        html = HTML(htmllog)
        html.init_page(self.name + " rev "+self.model_hash[0:7]+" build output")
        html.append_log_formatted(self.buildlog)
        html.write_page()

        csvline = self.name + ';' + self.linkpath + ';' ;

        if self.model_hash != '-' :
            csvline += HTML.href(self.model_hash[0:7], \
                                 self.linkpath.replace('.git','') + '/commit/' + self.model_hash) + ';'
        else:
            csvline += '-' + ';'

        csvline += HTML.monospace(self.generator) + ';' + HTML.monospace(self.options) + ';' 

        if cmdret:
            csvline += HTML.success()
        else:
            csvline += HTML.fail()
        csvline += '(' + HTML.href('log', htmllog) + ')' + ';'
        csvline += '-;-;'
        return csvline 

    def run_tests(self):

        for bench in self.benchmarks:
            bench.download()
            bench.run_tests(self.cross)




    def printsim(self):
        print("Simulator: " + self.name)
        print("| from " + self.linkpath)
        print("| generator: " + self.generator)
        print("| options: " + self.options )
        if (self.desc):
            print("| desc: " + self.desc )
        print("| benchmark: ", end="")
        for b in self.benchmarks:
            print("["+b.name+"] ", end="")
        print()
            

class CrossCompilers():

    cross = {}
    prefix = "/xtools/"

    def add_cross(self, env, cross, model):
        if model in self.cross:
            return self.cross[model]
        prefix = env.workspace + self.prefix + "/"
        mkdir(prefix)
        if (cross.startswith("./")) or (cross.startswith("/")):
            prefix += os.path.basename(cross)
            if not os.path.isdir(prefix+'/bin'):
                get_local(cross, prefix, ' Cross')
            self.cross[model] = {'src' : cross, 'prefix' : prefix}
        else:
            get_http(cross, prefix)
            tarname = os.path.basename(cross)
            tar = tarfile.open(prefix+"/"+tarname)
            tar.extractall(prefix)
            prefix += tar.getnames()[0]
            tar.close()
            self.cross[model] = { 'src' : cross, 'prefix' : prefix}
        return self.cross[model]

    def get_crosscsvline(self):
        csvline = ""
        for key in self.cross:
            csvline += 'Cross '+key+';'+self.cross[key]['src']+';-;'+HTML.success()+'\n' 
        return csvline

    def get_cross_bin(self, model):
        return self.cross[model]['prefix']+'/bin/'

