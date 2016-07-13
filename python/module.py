

class Module:
    name      = ""
    generator = ""
    options   = ""

    def __init__(self, name):
        self.name     = name

    def set_generator(self, gen):
        self.generator = gen

    def set_options(self, opt):
        self.options  = opt

    def print_module(self):
        print("Module: "+self.name)
        print("| generator: " + self.generator)
        print("| options: " + self.options)


