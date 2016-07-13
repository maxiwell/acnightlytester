#!/usr/bin/env python3

import argparse
import configparser


def command_line_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', dest='force', action='store_true', \
                        help='run the Nightly even without GIT modification')
    parser.add_argument('--condor', dest='condor', action='store_true', \
                        help='run over the condor')
    parser.add_argument('configfile', metavar='input.conf', \
                        help='configuration file')
    return parser.parse_args()
 
def config_parser_setup(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


def main():
    args = command_line_setup()

    config = config_parser_setup(args.configfile)

    print(config.sections())

    for key in config['mips']:
        print(key)

    mips = config['mips']
    print (mips['acsim'])


if __name__ == '__main__':
    main()  





