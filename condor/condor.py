#!/usr/bin/env python3

import os, re, argparse, signal, sys
from configparser     import ConfigParser
import pickle

from modules.archc      import ArchC, Simulator
from modules.nightly    import Nightly, Condor
from modules.benchbase  import Benchmark, App, Dataset
from modules            import utils
from modules.html       import HTML
from modules.benchmarks import *

def command_line_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbg', '--debug', dest='debug', action='store_true', \
                        help="don't remove the 'workspace' folder")
    parser.add_argument('envobj', metavar='env.p')
    parser.add_argument('archcobj', metavar='archc.p')
    parser.add_argument('simulatorobj', metavar='mips-acsim.p')

    return parser.parse_args()

def main():
    args        = command_line_handler()
    utils.debug = args.debug
   
    utils.env.copy(pickle.load (open (args.envobj, "rb")))
    archc     = pickle.load    (open (args.archcobj, "rb"))
    simulator = pickle.load    (open (args.simulatorobj, "rb"))

    env.set_workspace ( os.getcwd() )
    
    condor = Condor(archc, simulator)

    condor.running_simulator(simulator)
    
    condor.finalize(simulator)
     
if __name__ == '__main__':
    main()  


