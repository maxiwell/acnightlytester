

class App:
    name = ""
    dataset = []

    def __init__(self, name):
        self.name = name
        self.dataset = []

    def append_dataset(self, dataset):
        self.dataset.append(dataset)

    def printapp(self):
        string = self.name + " : "
        for d in self.dataset:
            string = string + d + " "
        print(string)

    def tostring(self):
        string = self.name + " : "
        for d in self.dataset:
            string += d+" "
        return string


class Benchmark:
    name = ""
    apps = []

    def __init__(self, name):
        self.name = name
        self.apps = []

    def append_app(self, app):
        self.apps.append(app)


    def printbench(self):
        print("Benchmark: "+self.name)
        for a in self.apps:
            print ( "| "+a.tostring())

    



