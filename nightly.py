#!/usr/bin/env python3

import os, re, argparse
from configparser import ConfigParser
from python.archc import ArchC
from python.env   import Env

def abort():
    print("To be development")


def command_line_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', dest='force', action='store_true', \
                        help='run the Nightly even without GIT modification')
    parser.add_argument('--condor', dest='condor', action='store_true', \
                        help='run over the condor')
    parser.add_argument('configfile', metavar='input.conf', \
                        help='configuration file')
    return parser.parse_args()
 
def config_parser_handler(configfile):
    env = Env()

    config = ConfigParser()
    config.read(configfile)

    modules_file   = config['nightly']['modules file']
    modules_config = ConfigParser()
    modules_config.read(modules_file)

    if (config.has_option('nightly', 'workspace')):
        workspace = config.get('nightly','workspace')
        env.set_workspace(workspace)

    if (config.has_option('nightly', 'htmlroot')):
        htmlroot  = config.get('nightly','htmlroot')
        env.set_htmlroot(htmlroot)

    env.printenv()

    if (config.has_section('archc')):
        if (config.has_option('archc','where')):
            archc = ArchC(env, config.get('archc','where'))
        else:
            abort()

        if (config.has_option('archc','systemc')):
            archc.set_systemc(config.get('archc','systemc'))

        if (config.has_option('archc','binutils')):
            archc.set_binutils(config.get('archc','binutils'))

        if (config.has_option('archc','gdb')):
            archc.set_gdb(config.get('archc','gdb'))
  
    return config


def main():
    args   = command_line_handler()
    config = config_parser_handler(args.configfile)

#    print(config.sections())
#
#    for key in config['mips']:
#        print(key)
#
#    mips = config['mips']
#    print (mips['acsim'])


if __name__ == '__main__':
    main()  





