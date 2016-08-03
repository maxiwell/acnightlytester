
from .benchmark import Benchmark
from .utils import *
import tarfile

class mibench (Benchmark):

    def __init__(self, env):
        super().__init__(env)
        self.name = "mibench"

        self.benchfolder = self.folderpath + "/SourceMibench/"
        self.goldenfolder = self.folderpath + "/GoldenMibench/"

    def download(self):
        base = "/home/max/ArchC/acnightly/sources/"
        #url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

        pkg = ['GoldenMibench.tar.bz2', 'SourceMibench.tar.bz2'] 
        for p in pkg:
            if (base.startswith("./")) or (base.startswith("/")):
                get_local(base+p, self.folderpath)
            else: 
                get_http(base+p, self.folderpath)

            tar = tarfile.open(self.folderpath+"/"+p)
            tar.extractall(self.folderpath)
            fullprefix = self.folderpath + tar.getnames()[0]
            tar.close()

    def exportenv (self, cross):
        export = ""
        for f in os.listdir(cross):
            if f.endswith("-gcc"):
                crosstuple = f.strip('-gcc')
        export += " TESTCOMPILER="+cross+crosstuple+'-gcc'
        export += " TESTAR="+cross+crosstuple+'-ar'
        export += " TESTCOMPILERCXX="+cross+crosstuple+'-g++'
        export += " TESTRANLIB="+cross+crosstuple+'-ranlib'
        export += " TESTFLAG='-specs=archc -static'"
        return export


    def run_tests(self, cross, sim):
        
        for app in self.apps:
            if   app.name == 'consumer/jpeg':
                srcfolder = self.benchfolder + app.name + '/jpeg-6a'
            elif app.name == 'consumer/lame':
                srcfolder = self.benchfolder + app.name + '/lame3.70'
            elif app.name == 'telecomm/adpcm':
                srcfolder = self.benchfolder + app.name + '/src'
            else:
                srcfolder = self.benchfolder + app.name 

            cmd  = "cd " + srcfolder + " && "
            cmd += "make clean && "
            cmd += self.exportenv(cross) + " make "

            self.compile(cmd, app, sim)






