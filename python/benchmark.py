
from .utils import *


class App:
    name = ""
    dataset = []

    def __init__(self, name):
        self.name = name
        self.dataset = []

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

    cflags = "'-specs=archc -static'"

    def __init__(self, env):
        self.folderpath = env.workspace + self.folder 
        self.env = env
        
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





