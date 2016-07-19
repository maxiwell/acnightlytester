
import os
from .helper import DownloadHelper
from .nightly    import Env
import subprocess
from .utils import *

class ArchC (DownloadHelper):

    archc = None
    systemc   = None
    binutils  = None
    gdb       = None

    archc_src    = "archc/src"
    archc_prefix = "archc/install"

    systemc_src    = "systemc/src"
    systemc_prefix = "systemc/install"

    binutils_src    = "binutils/src"
    binutils_prefix = "binutils/instsall"

    gdb_src         = "gdb/src"
    gdb_prefix      = "gdb/install"

    build_log       = "log/archc.log"

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
        self.build_log       = self.env.workspace + "/" + self.build_log
        mkdir(os.path.dirname(self.build_log))
        rm(self.build_log)

    def set_where(self, where):
        self.archc = where
        self.get_from(url_or_path = where, \
                copy_to = self.archc_src, pkg = "ArchC")

    def set_systemc(self, where):
        self.systemc = where
        if  self.systemc  :
            self.get_from( url_or_path = where, \
                    copy_to = self.systemc_prefix, pkg = "SystemC")

    def set_binutils(self, where):
        self.binutils = where
        if self.binutils :
            self.get_from( url_or_path = where, \
                    copy_to = self.binutils_src, pkg = "Binutils")

    def set_gdb(self, where):
        self.gdb = where
        if self.gdb :
            self.get_from( url_or_path = where, \
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
        if exec_to_log(cmd, self.build_log) :
            print("OK")
        else:
            print("FAILED")


class Simulator (DownloadHelper):
    name        = ""

    generator   = ""
    options     = ""
    desc        = ""

    inputfile   = ""
    where       = ""
    sim_src     = ""
    build_log   = ""

    env         = None
    benchmarks  = []

    def __init__(self, name, inputfile, env):
        self.name = name
        self.where = ""
        self.inputfile = inputfile
        self.env  = env
        self.benchmarks = []

        self.generator = ""
        self.options   = ""
        self.desc      = ""

        self.sim_src =   self.env.workspace + "/" + name
        self.build_log = self.env.workspace + "/log/" + self.name + ".log"
        mkdir(os.path.dirname(self.build_log))
        rm(self.build_log)

    def set_where(self, where):
        self.where = where
        if (self.where.startswith("./")) or (self.where.startswith("/")):
            self.get_local(self.where, self.sim_src, self.name)
        else:
            self.git_clone(self.where, self.sim_src, self.name)

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
        cmd_cd     = "cd " + self.sim_src + " && "
        cmd_acsim  = self.generator + " " + self.inputfile + " " \
                    + self.options + " && "
        cmd_make   = "make "

        cmd = cmd_source + cmd_cd + cmd_acsim + cmd_make 
        print(self.name + ":")
        print("| "+cmd)
        print("| Generating and Building... ", end="", flush=True)

        if exec_to_log(cmd, self.build_log) :
            print("OK")
        else:
            print("FAILED")

    def printsim(self):
        print("Simulator: " + self.name)
        print("| from " + self.where)
        print("| generator: " + self.generator)
        print("| options: " + self.options )
        if (self.desc):
            print("| desc: " + self.desc )
        print("| benchmark: ", end="")
        for b in self.benchmarks:
            print("["+b.name+"] ", end="")
        print()
            







