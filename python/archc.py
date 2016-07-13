
import os
from .helper import DownloadHelper
from .env    import Env

class ArchC (DownloadHelper):

    pick_from = None

    systemc   = None
    binutils  = None
    gdb       = None

    src_folder    = "archc"
    prefix_folder = "acinstall"
    workspace      = None


    def __init__(self, env, pick_from):
        self.pick_from = pick_from
        self.workspace  = env.workspace

        if (self.pick_from.startswith("./")) or \
                (self.pick_from.startswith("/")):
                    self.get_local(pick_from, \
                       self.workspace + self.src_folder, "ArchC")
        else:
            self.git_clone(self.pick_from, \
                    self.workspace + self.src_folder)



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




