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
        utils.env.set_htmloutput(yamls['nightly']['html output'])
        if 'tarball pool' in yamls['nightly'] and yamls['nightly']['tarball pool'] != None:
            utils.env.set_tarballpool(yamls['nightly']['tarball pool'])
        utils.env.printenv()

        archc = ArchC(utils.env)
        archc.set_systemc(yamls['archc']['systemc'])
        archc.set_linkpath(yamls['archc']['link/path'])
        if 'gdb' in yamls['archc'] and yamls['archc']['gdb'] != None:
            archc.set_gdb(yamls['archc']['gdb'])
        if 'binutils' in yamls['archc'] and yamls['archc']['binutils'] != None:
            archc.set_binutils(yamls['archc']['binutils'])
        if 'extlibs' in yamls['archc'] and yamls['archc']['extlibs'] != None:
            for _lib in yamls['archc'] and yamls['archc']['extlibs']:
                archc.set_external_libs(_lib, yamls['archc']['extlibs'][_lib])

        simlist = []
        if yamls['nightly']['simulators'] == 'all':
            simlist = yamls['simulators']
        else:
            simlist = yamls['nightly']['simulators']

        for _sim in simlist:
            if yamls['simulators'][_sim]['models'] == 'all':
                modellist = yamls['models']
            else:
                modellist = yamls['simulators'][_sim]['models']

            for _model in modellist:
                inputfile = yamls['models'][_model]['inputfile']
                run       = yamls['models'][_model]['run']
                linkpath  = yamls['models'][_model]['link/path']
                branch    = 'master'
                if 'branch' in yamls['models'][_model] and yamls['models'][_model]['branch'] != None:
                    branch = yamls['models'][_model]['branch']
                crosslink = yamls['models'][_model]['cross']
                
                sim = Simulator(_model, _sim, run, inputfile)
                sim.set_modellink(linkpath, branch)
                sim.set_generator(yamls['simulators'][_sim]['generator'])
                sim.set_options  (yamls['simulators'][_sim]['options'])
                if 'desc' in yamls['simulators'][_sim]:
                    sim.set_desc(yamls['simulators'][_sim]['desc'])
                if 'custom links' in yamls['simulators'][_sim]:
                    for cl in yamls['simulators'][_sim]['custom links']:
                        sim.set_custom_links(cl, yamls['simulators'][_sim]['custom links'][cl])
        
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
    args    = command_line_handler()
    
    nightly = config_parser_yaml(args.configfile)
    if args.debug:
        env.enable_dbg()
    if args.condor:
        env.enable_condor()

    if not nightly.git_hashes_changed() and not args.force:
        utils.abort("All repositories have tested in the last Nightly execution")

    nightly.init_pages()
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

