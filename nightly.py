#!/usr/bin/env python3

import argparse

def command_line_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', dest='force', action='store_true', \
                        help='run the Nightly even without GIT modification')
    parser.add_argument('--condor', dest='condor', action='store_true', \
                        help='run over the condor')
    parser.add_argument('config_file', metavar='input.conf', \
                        help='configuration file')
    return parser.parse_args()
 


if __name__ == '__main__':
  
    args = command_line_setup()

    print(args.config_file)



