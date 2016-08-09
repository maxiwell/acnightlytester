#!/usr/bin/env python3

import os, re, argparse, signal, sys
from configparser     import ConfigParser
import pickle

from python.archc     import ArchC, Simulator
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
    parser.add_argument('workspace', metavar='/path/to/workspace')
    parser.add_argument('envobj', metavar='env.p')
    parser.add_argument('archcobj', metavar='archc.p')
    parser.add_argument('simulatorobj', metavar='mips-acsin.p')

    return parser.parse_args()

def main():
    args        = command_line_handler()
    utils.debug = args.debug

    args.workspace = os.path.normpath(args.workspace)
    utils.rm(args.workspace)
    os.symlink(os.getcwd(), args.workspace)
    
    utils.env.copy(pickle.load (open (args.envobj, "rb")))
    archc     = pickle.load (open (args.archcobj, "rb"))
    simulator = pickle.load (open (args.simulatorobj, "rb"))
    
    condor = Condor(archc, simulator)

    condor.running_simulator(simulator)
    
    condor.finalize(simulator)
     
if __name__ == '__main__':
    main()  


