
from .benchbase import Benchmark
from .utils import *
from .html  import Table, HTML, HTMLPage
import tarfile, shutil, socket
from random import randint

class mibench (Benchmark):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def download(self, benchmark_folder):
        base = env.scriptroot + '/sources/'
        #url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

        self.benchfolder  = get_tar_git_or_folder(base + 'SourceMibench.tar.bz2', benchmark_folder) 
        self.goldenfolder = get_tar_git_or_folder(base + 'GoldenMibench.tar.bz2', benchmark_folder) 

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

    def run_tests(self, simulator_info):
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
                outputfiles['small'] = ['output_small.smoothing.pgm','output_small.edges.pgm', \
					'output_small.corners.pgm']
                outputfiles['large'] = ['output_large.smoothing.pgm','output_large.edges.pgm', \
					'output_large.corners.pgm']
            elif app.name == 'telecomm/adpcm':
                if simulator_info.endian == 'big':
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
                if simulator_info.endian == 'big':
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
            cmd += self.exportenv(simulator_info.crossbin, simulator_info.endian) + " make "
    
            self.compile(srcfolder, cmd, app)
    
            cmd_env  = "source "+env.get_archcenv()+" && "
            cmd_env += "export ENDIAN='"+simulator_info.endian+"' && "
            cmd_env += "export SIMULATOR='"+simulator_info.run+"' && "
           
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

class mibenchsmall(mibench):

    def __init__(self, name):
        super().__init__(name)


class spec2006 (Benchmark):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def download(self, benchmark_folder):
        base = env.scriptroot + "/sources/"
        #url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

        self.benchfolder  = get_tar_git_or_folder(base + 'SourceSPEC2006.tar.bz2', benchmark_folder) + 'CPU2006/'
        self.goldenfolder = get_tar_git_or_folder(base + 'GoldenSPEC2006.tar.bz2', benchmark_folder) 

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

    def run_tests(self, simulator_info):
        for app in self.apps:
            
            appfolder    = self.benchfolder + app.name

            outputfiles = {}
            srcfolder = appfolder + '/src'

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
               
            exportenv = self.exportenv(simulator_info.crossbin, simulator_info.endian)
            cmd  = "make clean " + exportenv + " && "
            cmd += "make "       + exportenv

            self.compile(srcfolder, cmd, app)
    
            cmd_env  = "source "+env.get_archcenv()+" && "
            cmd_env += "export SIMULATOR='"+simulator_info.run+"' && "
           
            for dataset in app.dataset:
                if dataset.name == 'test':
                    cmd_run = " ./runme_test.sh"
                    goldenfolder = self.goldenfolder + app.name + '/data/test/output/'

                self.run  (appfolder, cmd_env + cmd_run, app, dataset)
                self.diff (appfolder, goldenfolder, outputfiles[dataset.name], app, dataset)
                
class acstone(Benchmark):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def download(self, benchmark_folder):

        self.benchfolder = benchmark_folder + '/acstone/'
        self.gdbfolder   = benchmark_folder + '/gdb/'
        
        rm (self.benchfolder)
        git_clone('http://github.com/archc/acstone.git', self.benchfolder)         


    def get_free_port(self):
        result = 0
        port   = 0
        while result == 0:
            port = randint(5000,6000)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1',port))
        return port

    def exportev(self, cross, arch):
        cc  = ''
        for f in os.listdir(cross):
            if f.endswith("-gcc"):
                cc = f

        export  = ' ARCH="' + arch + '"'
        export += ' CROSS_COMPILER="' + cross + cc + '"'
        return export 

    def run_tests(self, simulator_info):

        gdbcmd = ' GDB="gdb-multiarch"'
        
        # Compiling GDB if 'gdb' it an 'app' in 'acstone' benchmark
        gdbappfilter = filter(lambda x: x.name == 'gdb', self.apps)
        for app in list(gdbappfilter):
            # You can use the 'gdb-multiarch', if you prefer
            #gdbsrc    = get_tar_git_or_folder ( '/home/max/ArchC/tools/gdb-7.8.tar.gz', self.gdbfolder )
            gdbsrc    = get_tar_git_or_folder ( 'https://ftp.gnu.org/gnu/gdb/gdb-7.11.tar.xz', self.gdbfolder )
            gdbprefix = self.gdbfolder + '/install/' 
 

            # Compile GDB to connect to simulator
            cmd  = './configure --target=' + simulator_info.arch + '-elf --prefix=' + gdbprefix + ' && '
            cmd += 'make && make install '
            self.compile ( gdbsrc, cmd, app )
            for f in os.listdir(gdbprefix + '/bin/'):
                if f.endswith("-gdb"):
                    gdbcmd = ' GDB="' + gdbprefix + '/bin/' + f + '"'
                    break
            
            for dataset in app.dataset:
                self.resolve_custom_links( gdbprefix, app, dataset )

                # Removing the execute page from HTML Log
                dataset.execpage = None

        for app in self.apps:

            if app.name == 'gdb':
                continue

            appfolder = self.benchfolder + app.name + '/'
            mkdir(appfolder)

            begin = int(app.name.split('-')[0])
            end   = int(app.name.split('-')[1])

            # split the app name to find the range
            for f in os.listdir(self.benchfolder):
                if re.match(r'.*\.c', f):
                    if int(f.split('.')[0]) >= begin and \
                        int(f.split('.')[0]) <= end:
                            shutil.copy( self.benchfolder + f, appfolder)
            shutil.copy( self.benchfolder + 'Makefile', appfolder)
            for d in ['bin', 'gdb']:
                shutil.copytree( self.benchfolder + d, appfolder + d)

            exportenv  = self.exportev(simulator_info.crossbin, simulator_info.name) + gdbcmd
            exportenv += " SIMULATOR='" + simulator_info.run + "'" 
            
            cmd = "make " + exportenv + " build"
            self.compile( appfolder, cmd, app )
   
            cmd_env  = "source " + env.get_archcenv() + " && "
            for dataset in app.dataset:

                cmd = 'make ' + exportenv + ' GDBPORT="' + str(self.get_free_port()) + '" run'
                self.run  ( appfolder, cmd_env + cmd, app, dataset )
               
                goldenfolder = appfolder + 'golden/'
                mkdir (goldenfolder)
                exec_to_var( 'cd ' + appfolder + ' && mv *.x86.out ' + goldenfolder)
                outls = exec_to_var ('cd ' + goldenfolder + " && rename 's/\.x86//g' * && ls *.out"  )
                outputfiles = outls.split()

                exec_to_var ("cd " + appfolder + " && rename 's/\." + simulator_info.name + "//g' *" )

                self.diff ( appfolder, goldenfolder, outputfiles, app, dataset)

class acstonesmall(acstone):

    def __init__(self, name):
        super().__init__(name)



