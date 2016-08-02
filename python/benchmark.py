
from python import helper


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


class Benchmark(helper.DownloadSource):
    name = ""
    apps = []
    env = None

    prefix = "/benchmark/"

    def __init__(self, name, env):
        self.name = name
        self.apps = []
        self.env = env

        fullprefix = env.workspace + self.prefix + "/"
        
        if   name == "mibench":
            self.get_mibench(fullprefix)
        elif name == "spec2006":
            self.get_spec(fullprefix)

    def append_app(self, app):
        self.apps.append(app)

    def printbench(self):
        print("Benchmark: "+self.name)
        for a in self.apps:
            print ( "| "+a.tostring())


