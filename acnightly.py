#!/usr/bin/env python3

import os, re, argparse, yaml, signal, sys
from configparser     import ConfigParser

sys.path.append(os.path.dirname(__file__))

from modules.archc     import ArchC, Simulator 
from modules.nightly   import Nightly, Env
from modules.benchbase import App, Dataset
from modules           import utils

from modules.benchmarks import *

def command_line_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', dest='force', action='store_true', \
                        help='run the Nightly even without GIT modification')
    parser.add_argument('--condor', dest='condor', action='store_true', \
                        help='run over the condor')
    parser.add_argument('-dbg', '--debug', dest='debug', action='store_true', \
                        help="don't remove the 'workspace' folder")
    parser.add_argument('configfile', metavar='config.yaml', \
                        help='configuration file')
    return parser.parse_args()

def config_parser_yaml(configfile):
    archc   = None
    simulators = []

    with open(configfile, 'r') as config:
        yamls = yaml.load(config)
        utils.env.set_workspace(yamls['nightly']['workspace'])
        utils.env.set_htmloutput(yamls['nightly']['htmloutput'])
        utils.env.printenv()

        archc = ArchC(utils.env)
        archc.set_systemc(yamls['archc']['systemc'])
        archc.set_linkpath(yamls['archc']['link/path'])
        if 'gdb' in yamls['archc'] and yamls['archc']['gdb'] != None:
            archc.set_gdb(yamls['archc']['gdb'])
        if 'binutils' in yamls['archc'] and yamls['archc']['binutils'] != None:
            archc.set_binutils(yamls['archc']['binutils'])

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
                sim = Simulator(model, _module, run, inputfile)
                sim.set_modellink(linkpath)
                sim.set_generator(yamls['modules'][_module]['generator'])
                sim.set_options(yamls['modules'][_module]['options'])
                if 'desc' in yamls['modules'][_module]:
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
                sim.set_crosslink( crosslink )
                simulators.append(sim)
        
        simulators.sort(key=lambda x: x.name)
        for s in simulators:
            s.printsim()

        nightly = Nightly(archc, simulators)
        return nightly
                
def main():
    args        = command_line_handler()
    
    nightly = config_parser_yaml(args.configfile)
    utils.env.debug_mode  = args.debug
    utils.env.condor_mode = args.condor

    if not nightly.git_hashes_changed() and not args.force:
        utils.abort("All repositories have tested in the last Nightly execution")

    nightly.building_archc()

    for simulator in nightly.simulators:
        if args.condor:
            nightly.condor_runnning_simulator(simulator)
            # nightly.finalize() is called by condor.py in each node machine
        else:
            nightly.running_simulator(simulator)
            nightly.finalize(simulator)
     
if __name__ == '__main__':
    main()  

