
from .utils import *
from .html import *

class Dataset:
    name = ""
    execpage = ""
    diffpage = ""
    diffstatus = ""

    def __init__(self, name, app, sim):
        self.name = name
        self.execpage = env.htmloutput + '/' + env.testnumber + '-' + sim + '-' + \
                        app.replace('/','_') + '-' + name.replace('/','_') + '-run.html'
                        
        self.diffpage = env.htmloutput + '/' + env.testnumber + '-' + sim + '-' + \
                        app.replace('/','_') + '-' + name.replace('/','_') + '-diff.html'

        self.diffstatus = True

class App:
    name = ""
    dataset = []
    appfolder   = ""
    buildpage   = ""
    buildstatus = ""

    def __init__(self, name, sim):
        self.name = name
        self.dataset = []

        self.buildpage = env.htmloutput + '/' + env.testnumber + '-' + sim + \
                         '-' + name.replace('/','_') + '-build.html'

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
    name = ""
    apps = []

    def __init__(self):
        self.apps = []

    def append_app(self, app):
        self.apps.append(app)

    def printbench(self):
        print("Benchmark: "+self.name)
        for a in self.apps:
            print ( "| "+a.tostring())

    def download(self, benchmark_folder):
        raise NotImplementedError("Please Implement this method")

    def run_tests(self, cross_folder, simulator_endian, simulator_name, simulator_cmdline):
        raise NotImplementedError("Please Implement this method")

    def compile(self, cmd, app, sim):

        print('| [compiling] '+app.name+"... ",end="", flush=True)

        log = create_rand_file()
        if exec_to_log(cmd, log):
            print("OK")
            app.buildstatus = HTML.success()
        else:
            print("FAILED")
            app.buildstatus = HTML.fail()

        HTML.log_to_html(log, app.buildpage, \
                    sim + ' ' + app.name + ' build log')

    def run(self, cmd, app, dataset):
        print('| [ running ] ' + app.name + " (" + dataset.name + ")... ",end="", flush=True)
        log = create_rand_file()
        if exec_to_log(cmd, log):
            print("OK")
        else:
            print("FAILED")

        HTML.log_to_html(log, dataset.execpage, \
                         app.name + ' ' + dataset.name + ' Simulator Output')

    def diff(self, app, dataset, appfolder, goldenfolder, outputfiles):
        html = HTMLPage(dataset.diffpage)
        html.init_page(app.name + ' ' + dataset.name + ' output compared with Golden Model')
        for f in outputfiles:
            cmd  = 'diff -w '
            cmd +=    appfolder + '/' + f + ' '
            cmd += goldenfolder + '/' + f + ' '
            
            log = create_rand_file() 
            if not exec_to_log(cmd, log):
                dataset.diffstatus = False

            html.append_raw('<h2>File '+f+'</h2>\n') 
            html.append_log_formatted(log)
            html.write_page()




