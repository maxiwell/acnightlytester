#!/usr/bin/env python3

import os, re, argparse, yaml, signal, sys
from configparser     import ConfigParser
from python.archc     import ArchC, Simulator
from python.nightly   import Nightly, Env
from python.benchmark import Benchmark, App
from python           import utils
from python.html      import HTML

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
    nightly = Nightly()
    env     = Env()
    archc   = ArchC()
    simulators = []

    with open(configfile, 'r') as config:
        try: 
            yamls = yaml.load(config)
            env.set_workspace(yamls['nightlysetup']['workspace'])
            env.set_htmlroot (yamls['nightlysetup']['htmlroot'])
            utils.workspace = env.workspace
            env.printenv()

            archc.set_env(env)
            archc.set_systemc(yamls['archc']['systemc'])
            archc.set_gdb(yamls['archc']['gdb'])
            archc.set_binutils(yamls['archc']['binutils'])
            archc.set_linkpath(yamls['archc']['link/path'])

            for _sim in yamls['nightlysetup']['simulators']:
                inputfile = yamls['simulators'][_sim]['inputfile']
                linkpath  = yamls['simulators'][_sim]['link/path']
                for _module in yamls['simulators'][_sim]['modules']:
                    sim = Simulator(_sim+"-"+_module, inputfile, env)
                    sim.set_linkpath(linkpath)
                    sim.set_generator(yamls['modules'][_module]['generator'])
                    sim.set_options(yamls['modules'][_module]['options'])
                    sim.set_desc(yamls['modules'][_module]['desc'])
        
                    for _bench in yamls['simulators'][_sim]['benchmarks']:
                        bench = Benchmark(_bench)
                        for _app in yamls['benchmarks'][_bench] :
                            app = App(_app)
                            for _dataset in yamls['benchmarks'][_bench][_app]:
                                app.append_dataset(_dataset)
                            bench.append_app(app)
                        sim.append_benchmark(bench)
                    simulators.append(sim)

            for s in simulators:
                s.printsim()

            nightly.env = env
            nightly.archc = archc
            nightly.simulators = simulators
            return nightly

        except Exception as e:
            utils.abort("[config.yaml] "+str(e))
                
def main():
    args   = command_line_handler()
    utils.debug = args.debug
    nightly = config_parser_yaml(args.configfile)

    nightly.init_htmlindex()
    nightly.init_htmllog()

    nightly.build_and_install_archc()
#    nightly.gen_and_build_simulator(nightly.simulators[0])
     
if __name__ == '__main__':
    main()  





