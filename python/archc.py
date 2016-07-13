
class ArchC:
    systemc  = None
    binutils = None
    gdb      = None

    def set_systemc(path):
        self.systemc = path

    def set_binutils(path):
        self.binutils = path

    def set_gdb(path):
        self.gdb = path



class Models:
    modules = []
    where   = ""

    def set_where(self, path):
        self.where = path

    def add_modules(self, module):
        self.modules.append(module)




