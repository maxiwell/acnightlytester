
import os
from .helper import DownloadHelper
from .env    import Env

class ArchC (DownloadHelper):

    where = None

    systemc   = None
    binutils  = None
    gdb       = None

    src_folder    = "archc"
    prefix_folder = "acinstall"

    env = None

    def set_env(self, env):
        self.env = env;

    def set_where(self, where):
        self.where = where

        if (self.where.startswith("./")) or         \
                (self.where.startswith("/")):
                    self.get_local(where, self.env.workspace + "/" \
                                   + self.src_folder, "ArchC")
        else:
            self.git_clone(self.where, \
                    self.env.workspace + "/" + self.src_folder)

    def set_systemc(self, path):
        self.systemc = path

    def set_binutils(self, path):
        self.binutils = path

    def set_gdb(self, path):
        self.gdb = path


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

    src_folder = ""

    env = None

    def __init__(self, name, env):
        self.name = name
        self.module = None
        self.where = ""
        self.env  = env
        self.src_folder = name

    def set_where(self, path):
        self.where = path

        if (self.where.startswith("./")) or         \
                (self.where.startswith("/")):
                    self.get_local(self.where, self.env.workspace + "/" \
                                   + self.src_folder, self.name)
        else:
            self.git_clone(self.where, \
                    self.env.workspace + "/" + self.src_folder)
    
    def set_module(self, module):
        self.module = module

    def printsim(self):
        print("Simulator: " + self.name)
        print("| from " + self.where)
        print("| " + self.module.tostring())





