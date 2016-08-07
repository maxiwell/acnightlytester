#!/usr/bin/env python3

import os, re, argparse, yaml, signal, sys
from configparser     import ConfigParser
from python.archc     import ArchC, Simulator, CrossCompilers
from python.nightly   import Nightly, Env
from python.benchmark import Benchmark, App, Dataset
from python           import utils
from python.html      import HTML

from python.mibench   import mibench
from python.spec2006  import spec2006

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
    archc   = ArchC()
    simulators = []
    cross = CrossCompilers()

    with open(configfile, 'r') as config:
#        try: 
            yamls = yaml.load(config)
            utils.env.setworkspace(yamls['nightly']['workspace'])
            utils.env.sethtmloutput(yamls['nightly']['htmloutput'])
            utils.env.printenv()

            archc.update_paths()
            archc.set_systemc(yamls['archc']['systemc'])
            archc.set_gdb(yamls['archc']['gdb'])
            archc.set_binutils(yamls['archc']['binutils'])
            archc.set_linkpath(yamls['archc']['link/path'])

            for _sim in yamls['nightly']['simulators']:
                inputfile = yamls['simulators'][_sim]['inputfile']
                run       = yamls['simulators'][_sim]['run']
                linkpath  = yamls['simulators'][_sim]['link/path']
                crosslink = yamls['simulators'][_sim]['cross']
                for _module in yamls['simulators'][_sim]['modules']:
                    sim = Simulator(_sim+"-"+_module, run, inputfile)
                    sim.set_linkpath(linkpath)
                    sim.set_generator(yamls['modules'][_module]['generator'])
                    sim.set_options(yamls['modules'][_module]['options'])
                    sim.set_desc(yamls['modules'][_module]['desc'])
        
                    for _bench in yamls['simulators'][_sim]['benchmarks']:
                        bench = eval(_bench)()
                        for _app in yamls['benchmarks'][_bench] :
                            app = App(_app, sim.name)
                            for _dataset in yamls['benchmarks'][_bench][_app]:
                                dataset = Dataset(_dataset, app.name, sim.name)
                                app.append_dataset(dataset)
                            bench.append_app(app)
                        sim.append_benchmark(bench)
                    cross.add_cross(crosslink, _sim)
                    sim.set_cross( cross.get_cross_bin(_sim) ) 
                    simulators.append(sim)
            
            for s in simulators:
                s.printsim()

            nightly = Nightly(archc, simulators, cross)
            return nightly

#        except Exception as e:
#            utils.abort("[config.yaml] "+str(e))
                
def main():
    args        = command_line_handler()
    utils.debug = args.debug
    
    nightly = config_parser_yaml(args.configfile)

    if not nightly.git_hashes_changed() and not args.force:
        utils.abort("All repositories have tested in the last Nightly execution")

#    nightly.building_archc()

    nightly.running_simulators()
    
    nightly.finalize()
     
if __name__ == '__main__':
    main()  





