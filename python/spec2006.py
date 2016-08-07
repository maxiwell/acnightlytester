
from .benchmark import Benchmark
from .utils import *
from .html  import Table, HTML, HTMLPage
import tarfile

class spec2006 (Benchmark):

    def __init__(self):
        super().__init__()
        self.name = "spec2006"

    def download(self, benchmark_folder):
        self.benchfolder  = benchmark_folder + "/SourceSPEC2006/CPU2006/"
        self.goldenfolder = benchmark_folder + "/GoldenSpec/"

        base = "/home/max/ArchC/acnightly/sources/"
        #url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

        pkg = ['GoldenSPEC2006.tar.bz2', 'SourceSPEC2006.tar.bz2'] 
        for p in pkg:
            if (base.startswith("./")) or (base.startswith("/")):
                get_local(base+p, benchmark_folder)
            else: 
                get_http(base+p, benchmark_folder)

            tar = tarfile.open(benchmark_folder+"/"+p)
            tar.extractall(benchmark_folder)
            fullprefix = benchmark_folder + tar.getnames()[0]
            tar.close()

    def exportenv (self, cross, endian):
        export = ""
        for f in os.listdir(cross):
            if f.endswith("-gcc"):
                crosstuple = f.strip('-gcc')
        export += " CC="+cross+crosstuple+'-gcc'
        export += " CXX="+cross+crosstuple+'-g++'
        export += " ENDIAN="+endian
        export += " SPEC='"+self.benchfolder+"../'"
        return export

    def run_tests(self, cross_folder, simulator_endian, simulator_name, simulator_cmdline):
        for app in self.apps:
            
            appfolder    = self.benchfolder + app.name

            outputfiles = {}
            srcfolder = appfolder + '/src'
            cmd_env   = ''

            if app.name == '401.bzip2':
                outputfiles['test'] = ['input.program.out']
            elif app.name == '403.gcc':
                outputfiles['test'] = ['cccp.s']
            elif app.name == '429.mcf':
                outputfiles['test'] = ['inp.out']
            elif app.name == '445.gobmk':
                outputfiles['test'] = ['capture.out']
            elif app.name == '456.hmmer':
                outputfiles['test'] = ['bombesin.out']
            elif app.name == '458.sjeng':
                outputfiles['test'] = ['test.out']
            elif app.name == '462.libquantum':
                outputfiles['test'] = ['test.out']
            elif app.name == '464.h264ref':
                outputfiles['test'] = ['foreman_test_baseline_encodelog.out']
               
            exportenv = self.exportenv(cross_folder, simulator_endian)
            cmd  = "cd " + srcfolder + " && "
            cmd += "make clean " + exportenv + " && "
            cmd += "make "       + exportenv

            self.compile(cmd, app, simulator_name)
    
            cmd_env += "source "+env.archc_envfile+" && "
            cmd_env += "export SIMULATOR='"+simulator_cmdline+"' && "
            cmd_env += "cd " + self.benchfolder + app.name  + " && " 
           
            for ds in app.dataset:
                if ds.name == 'test':
                    cmd_run = " ./runme_test.sh"
                    goldenfolder = self.goldenfolder + app.name + '/data/test/output/'

                self.run (cmd_env + cmd_run, app, ds)
                self.diff (app, ds, appfolder, goldenfolder, outputfiles[ds.name])
                

