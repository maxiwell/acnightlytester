
from .utils import *
from .html import *
import shutil

class Dataset:
    name = ""
    execpage = ""
    diffpage = ""
    diffstatus = ""
    custom_links = {}

    def __init__(self, name, app, sim):
        self.custom_links = {}
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
    custom_links = {}
    simulator_name = ""

    def __init__(self):
        self.name = ""
        self.apps = []
        self.custom_links = {}
        self.simulator_name = ""

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

    def compile(self, srcfolder, cmd, app):
        print('| [compiling] '+app.name+"... ",end="", flush=True)
        cmd_cd = "cd " + srcfolder + " && "

        log = create_rand_file()
        if exec_to_log(cmd_cd + cmd, log):
            print("OK")
            app.buildstatus = HTML.success()
        else:
            print("FAILED")
            app.buildstatus = HTML.fail()

        HTML.log_to_html(log, app.buildpage, \
                    self.simulator_name + ' ' + app.name + ' build log')

    def run(self, appfolder, cmd, app, dataset):
        print('| [ running ] ' + app.name + " (" + dataset.name + ")... ",end="", flush=True)
        cmd_cd = "cd " + appfolder + " && "

        log = create_rand_file()
        if exec_to_log(cmd_cd + cmd, log):
            print("OK")
        else:
            print("FAILED")

        HTML.log_to_html(log, dataset.execpage, \
                         app.name + ' ' + dataset.name + ' Simulator Output')

        try:
            for link, cmdline in self.custom_links.items():
                cmd = cmd_cd + cmdline.strip()
                f = exec_to_var(cmd).split('\n')[-1]
                ext = find_ext(f)

                dataset.custom_links[link] = env.htmloutput + '/' + env.testnumber + '-' + self.simulator_name + '-' + \
                                             app.name.replace('/','_') + '-' + dataset.name + '-' + link.replace(' ','_') + ext
    
                shutil.move(appfolder + '/' + f, dataset.custom_links[link])
        except:
            print('ERROR in Custom Link command line')

    def diff(self, appfolder, goldenfolder, outputfiles, app, dataset):
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




