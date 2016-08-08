
from .benchmark import Benchmark
from .utils import *
from .html  import Table, HTML, HTMLPage
import tarfile

class mibench (Benchmark):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def download(self, benchmark_folder):
        self.benchfolder  = benchmark_folder + "/SourceMibench/"
        self.goldenfolder = benchmark_folder + "/GoldenMibench/"

        base = "/home/max/ArchC/acnightly/sources/"
        #url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

        pkg = ['GoldenMibench.tar.bz2', 'SourceMibench.tar.bz2'] 
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
        export += " TESTCOMPILER="+cross+crosstuple+'-gcc'
        export += " TESTAR="+cross+crosstuple+'-ar'
        export += " TESTCOMPILERCXX="+cross+crosstuple+'-g++'
        export += " TESTRANLIB="+cross+crosstuple+'-ranlib'
        export += " TESTFLAG='-specs=archc -static'"
        export += " ENDIAN="+endian
        return export

    def run_tests(self, cross_folder, simulator_endian, simulator_name, simulator_cmdline):
        for app in self.apps:
            
            appfolder    = self.benchfolder + app.name
            goldenfolder = self.goldenfolder + app.name

            outputfiles = {}
            outputfiles['small'] = ['output_small.txt']
            outputfiles['large'] = ['output_large.txt']
            srcfolder = appfolder

            if app.name == 'automotive/basicmath':
                outputfiles['small'] = ['output_small.txt']
                outputfiles['large'] = ['output_large_softfloat.txt']
            elif app.name == 'automotive/susan':
                outputfiles['small'] = ['output_small.smoothing.pgm','output_small.edges.pgm','output_small.corners.pgm']
                outputfiles['large'] = ['output_large.smoothing.pgm','output_large.edges.pgm','output_large.corners.pgm']
            elif app.name == 'telecomm/adpcm':
                if simulator_endian == 'big':
                    outputfiles['small'] = ['output_small.adpcm', 'BIG_ENDIAN_output_small.pcm']
                    outputfiles['large'] = ['output_large.adpcm', 'BIG_ENDIAN_output_large.pcm']
                else:
                    outputfiles['small'] = ['output_small.adpcm', 'output_small.pcm']
                    outputfiles['large'] = ['output_large.adpcm', 'output_large.pcm']
                srcfolder = appfolder + '/src'
            elif app.name == 'telecomm/FFT':
                outputfiles['small'] = ['output_small.txt', 'output_small.inv.txt']
                outputfiles['large'] = ['output_large.txt', 'output_large.inv.txt']
            elif app.name == 'telecomm/gsm':
                outputfiles['small'] = ['output_small.encode.gsm', 'output_small.decode.run']
                outputfiles['large'] = ['output_large.encode.gsm', 'output_large.decode.run']
            elif app.name == 'network/dijkstra':
                outputfiles['small'] = ['output_small.dat']
                outputfiles['large'] = ['output_large.dat']
            elif app.name == 'security/rijndael':
                if simulator_endian == 'big':
                    outputfiles['small'] = ['output_small.enc', 'output_small.dec']
                    outputfiles['large'] = ['output_large.enc', 'output_large.dec']
                else:
                    outputfiles['small'] = ['LITTLE_ENDIAN_output_small.enc', 'output_small.dec']
                    outputfiles['large'] = ['LITTLE_ENDIAN_output_large.enc', 'output_large.dec']
            elif app.name == 'consumer/jpeg':
                outputfiles['small'] = ['output_small_encode.jpeg', 'output_small_decode.ppm']
                outputfiles['large'] = ['output_large_encode.jpeg', 'output_large_decode.ppm']
                srcfolder = appfolder + '/jpeg-6a'
            elif app.name == 'consumer/lame':
                outputfiles['small'] = ['output_small.mp3']
                outputfiles['large'] = ['output_large.mp3']
                srcfolder = appfolder + '/lame3.70'
                
            cmd  = "make clean && "
            cmd += self.exportenv(cross_folder, simulator_endian) + " make "
    
            self.compile(srcfolder, cmd, app)
    
            cmd_env  = "source "+env.archc_envfile+" && "
            cmd_env += "export ENDIAN='"+simulator_endian+"' && "
            cmd_env += "export SIMULATOR='"+simulator_cmdline+"' && "
           
            for dataset in app.dataset:
                if dataset.name == 'small':
                    cmd_run = " ./runme_small.sh"
                if dataset.name == 'large':
                    cmd_run = " ./runme_large.sh"

                self.run  (appfolder, cmd_env + cmd_run, app, dataset)
                self.diff (appfolder, goldenfolder, outputfiles[dataset.name], app, dataset)
                

class mibenchtest(mibench):

    def __init__(self, name):
        super().__init__(name)


