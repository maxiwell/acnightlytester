

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

    def print_module(self):
        print("Module: "+self.name)
        if (self.generator != ""):
            print("| generator: " + self.generator)
        if (self.options != ""):
            print("| options: " + self.options)
        if (self.desc != ""):
            print("| desc: " + self.desc)


