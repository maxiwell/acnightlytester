
import os
from .helper import DownloadHelper
from .nightly    import Env
import subprocess
from .utils import *
from .html import *

class ArchC (DownloadHelper):

    archc     = ""
    systemc   = ""
    binutils  = "" 
    gdb       = ""

    archchash_long  = ""
    archchash_short = ""

    archc_src    = "archc/src"
    archc_prefix = "archc/install"

    systemc_src    = "systemc/src"
    systemc_prefix = "systemc/install"

    binutils_src    = "binutils/src"
    binutils_prefix = "binutils/instsall"

    gdb_src         = "gdb/src"
    gdb_prefix      = "gdb/install"

    buildlog        = "log/archc.log"
    
    htmllog         = "-archc-build-log.html"

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
        self.buildlog        = self.env.workspace + "/" + self.buildlog
        mkdir(os.path.dirname(self.buildlog))
        #rm(self.buildlog)

    def set_linkpath(self, linkpath):
        self.archc = linkpath
        self.get_from(url_or_path = linkpath, \
                copy_to = self.archc_src, pkg = "ArchC")
        self.archchash_long, self.archchash_short = get_githash(self.archc_src)

    def set_systemc(self, linkpath):
        self.systemc = linkpath
        if  self.systemc  :
            self.get_from( url_or_path = linkpath, \
                    copy_to = self.systemc_prefix, pkg = "SystemC")

    def set_binutils(self, linkpath):
        self.binutils = linkpath
        if self.binutils :
            self.get_from( url_or_path = linkpath, \
                    copy_to = self.binutils_src, pkg = "Binutils")

    def set_gdb(self, linkpath):
        self.gdb = linkpath
        if self.gdb :
            self.get_from( url_or_path = linkpath, \
                    copy_to = self.gdb_src, pkg = "GDB")

    def build(self):

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

#       cmdret = exec_to_log(cmd, self.buildlog) 
        cmdret = 0
        if cmdret == 0:
            print("OK")
        else:
            print("FAILED")

        htmllog = self.env.htmlroot + "/" + self.env.index + self.htmllog
        html = HTML(htmllog)
        html.init_page("ArchC rev "+self.archchash_short+" build output")
        html.append_log_formatted(self.buildlog)
        html.close_page()

        strret = 'ArchC;' + self.archc + ';' \
               + HTML.href(self.archchash_short, self.archc.replace('.git','') \
               + '/commit/' + self.archchash_long) + ';'
        if cmdret == 0:
            strret += HTML.success()
        else:
            strret += HTML.fail()

        strret += '(' + HTML.href('log', htmllog) + ');'
        return strret


class Simulator (DownloadHelper):
    name        = ""

    generator   = ""
    options     = ""
    desc        = ""

    inputfile   = ""
    linkpath    = ""
    simsrc     = ""
    buildlog   = ""

    env         = None
    benchmarks  = []

    htmllog     = ""

    def __init__(self, name, inputfile, env):
        self.name = name
        self.linkpath = ""
        self.inputfile = inputfile
        self.env  = env
        self.benchmarks = []

        self.generator = ""
        self.options   = ""
        self.desc      = ""
        self.htmllog   = ""

        self.simsrc    = env.workspace + "/" + name
        self.buildlog = env.workspace + "/log/" + name + ".log"
        mkdir(os.path.dirname(self.buildlog))
        rm(self.buildlog)

    def set_linkpath(self, linkpath):
        self.linkpath = linkpath
        if (self.linkpath.startswith("./")) or (self.linkpath.startswith("/")):
            self.get_local(self.linkpath, self.simsrc, self.name)
        else:
            self.git_clone(self.linkpath, self.simsrc, self.name)

    def set_generator(self, generator):
        self.generator = generator

    def set_options(self, options):
        self.options = options

    def set_desc(self, desc):
        self.desc = desc

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

        if exec_to_log(cmd, self.buildlog) :
            print("OK")
        else:
            print("FAILED")

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
            







