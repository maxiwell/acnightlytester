#!/usr/bin/env python3

import os, re, argparse, yaml, signal, sys
from configparser     import ConfigParser
import pickle

sys.path.append('../')
from python.archc     import ArchC, Simulator, CrossCompilers
from python.nightly   import Nightly, Condor
from python.benchmark import Benchmark, App, Dataset
from python           import utils
from python.html      import HTML
from python.mibench   import *
from python.spec2006  import *

def command_line_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbg', '--debug', dest='debug', action='store_true', \
                        help="don't remove the 'workspace' folder")
    parser.add_argument('simulatorobj', metavar='mips-acsin.p')
    parser.add_argument('envobj', metavar='env.p')
    parser.add_argument('archcobj', metavar='archc.p')
    parser.add_argument('crossobj', metavar='cross.p')

    return parser.parse_args()

def config_parser_yaml(configfile, workspace, htmloutput):
    archc   = ArchC()
    simulators = []
    cross = CrossCompilers()

    with open(configfile, 'r') as config:
        try: 
            yamls = yaml.load(config)

            utils.env.setworkspace(workspace)
            utils.env.sethtmloutput(htmloutput)
            utils.env.printenv()

            archc.update_paths()
            archc.set_systemc(yamls['archc']['systemc'])
            archc.set_gdb(yamls['archc']['gdb'])
            archc.set_binutils(yamls['archc']['binutils'])
            archc.set_linkpath(yamls['archc']['link/path'])

            simlist = []
            if yamls['nightly']['simulators'] == 'all':
                simlist = yamls['simulators']
            else:
                simlist = yamls['nightly']['simulators']

            for _sim in simlist:
                model     = yamls['simulators'][_sim]['model']
                inputfile = yamls['models'][model]['inputfile']
                run       = yamls['models'][model]['run']
                linkpath  = yamls['models'][model]['link/path']
                crosslink = yamls['models'][model]['cross']
                for _module in yamls['simulators'][_sim]['modules']:
                    sim = Simulator(model+'-'+_module, model, _module, run, inputfile)
                    sim.set_linkpath(linkpath)
                    sim.set_generator(yamls['modules'][_module]['generator'])
                    sim.set_options(yamls['modules'][_module]['options'])
                    sim.set_desc(yamls['modules'][_module]['desc'])
                    if 'custom links' in yamls['modules'][_module]:
                        for cl in yamls['modules'][_module]['custom links']:
                            sim.set_custom_links(cl, yamls['modules'][_module]['custom links'][cl])
        
                    for _bench in yamls['simulators'][_sim]['benchmarks']:
                        bench = eval(_bench)(_bench)
                        for _app in yamls['benchmarks'][_bench] :
                            app = App(_app, sim.name)
                            for _dataset in yamls['benchmarks'][_bench][_app]:
                                dataset = Dataset(_dataset, app.name, sim.name)
                                app.append_dataset(dataset)
                            bench.append_app(app)
                        sim.append_benchmark(bench)
                    cross.add_cross(crosslink, model)
                    sim.set_cross( cross.get_cross_bin(model) ) 
                    simulators.append(sim)
           
            simulators.sort(key=lambda x: x.name)
            for s in simulators:
                s.printsim()

            nightly = Nightly(archc, simulators, cross)
            return nightly

        except Exception as e:
            utils.abort("[config.yaml] "+str(e))
                
def main():
    args        = command_line_handler()
    utils.debug = args.debug
    
    simulator = pickle.load (open (args.simulatorobj, "rb"))
    utils.env.copy(pickle.load (open (args.envobj, "rb")))
    archc     = pickle.load (open (args.archcobj, "rb"))
    cross     = pickle.load (open (args.crossobj, "rb"))
    condor = Condor( archc, simulator, cross)

    condor.running_simulator(simulator)
    
#    nightly.finalize()
     
if __name__ == '__main__':
    main()  





