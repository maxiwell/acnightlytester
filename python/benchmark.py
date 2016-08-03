
from .utils import *
from .html import *


class App:
    name = ""
    dataset = []
    htmlsuffix = ""

    def __init__(self, name):
        self.name = name
        self.dataset = []
        self.htmlsuffix = "-"+name.replace('/','_')+"-build.html"

    def append_dataset(self, dataset):
        self.dataset.append(dataset)

    def printapp(self):
        print(self.tostring())

    def tostring(self):
        string = self.name + " : "
        for d in self.dataset:
            string += d+" "
        return string


class Benchmark():

    folder     = "/benchmark/"
    folderpath = "" 

    name = ""
    env  = None
    apps = []

    htmllog = ""

    def __init__(self, env):
        self.folderpath = env.workspace + self.folder 
        self.env = env
        self.buildlog = env.workspace + "/log/"
        
    def append_app(self, app):
        self.apps.append(app)

    def printbench(self):
        print("Benchmark: "+self.name)
        for a in self.apps:
            print ( "| "+a.tostring())

    def download(self, cross):
        raise NotImplementedError("Please Implement this method")

    def run_tests(self):
        raise NotImplementedError("Please Implement this method")

    def compile(self, cmd, app, sim):

        print(app.name+"...",end="")

        buildlog = self.buildlog + sim + "-" + app.name.replace('/','_')+'.log'
        cmdret = exec_to_log(cmd, buildlog)
        if cmdret:
            print("OK")
        else:
            print("FAILED")

        htmllog = self.env.htmloutput + "/" + self.env.testnumber + "-" + sim + app.htmlsuffix
        html    = HTMLPage(htmllog)
        html.init_page(sim + ' ' + app.name + ' build log')
        html.append_log_formatted(buildlog)
        html.write_page()
    





