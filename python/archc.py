
import os
from .helper import DownloadHelper
from .env    import Env
import subprocess

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
        cmd = "cd " + self.archc_src + " && " + \
              "./autogen.sh && " + \
              "./configure --prefix=" + self.archc_prefix
        if self.systemc:
            cmd += " --with-systemc=" + self.systemc_prefix
        if self.binutils: 
            cmd += " --with-binutils=" + self.binutils_src
        if self.gdb:
            cmd += " --with-gdb=" + self.gdb_src
        cmd += " && make && make install"
        print("ArchC:")
        print("| "+cmd)
        print("| Building and Installing...", end="", flush=True)
        if os.system( " ( " + cmd + " ) > /dev/null 2>&1" ) == 0 :
            print("OK")
        else:
            print("FAILED")

class Module:
    name      = ""
    generator = ""
    options   = ""
    desc      = ""

    def __init__(self, name):
        self.name     = name

    def set_generator(self, gen):
        self.generator = gen

    def set_options(self, opt):
        self.options  = opt

    def set_desc(self, desc):
        self.desc = desc

    def tostring(self):
        string = "Module: " + self.name 
        if (self.generator != ""):
            string += "\n| generator: " + self.generator 
        if (self.options != ""):
            string += "\n| options: " + self.options 
        if (self.desc != ""):
            string += "\n| desc: " + self.desc 
        return string



    def print_module(self):
        print(string)


class Simulator (DownloadHelper):
    name    = ""
    module = None
    where   = ""

    sim_src = ""

    env = None

    def __init__(self, name, env):
        self.name = name
        self.module = None
        self.where = ""
        self.env  = env
        self.sim_src = name

    def set_where(self, where):
        self.where = where
        if (self.where.startswith("./")) or (self.where.startswith("/")):
            self.get_local(self.where, self.env.workspace + "/" + self.sim_src, self.name)
        else:
            self.git_clone(self.where, self.env.workspace + "/" + self.sim_src)




    def set_module(self, module):
        self.module = module

    def printsim(self):
        print("Simulator: " + self.name)
        print("| from " + self.where)
        print("| " + self.module.tostring())





