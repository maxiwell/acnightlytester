
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



class Models:
    modules = []
    where   = ""

    def set_where(self, path):
        self.where = path

    def add_modules(self, module):
        self.modules.append(module)




