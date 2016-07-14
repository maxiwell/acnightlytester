#!/usr/bin/env python3

import os, re, argparse
from configparser     import ConfigParser
from python.archc     import ArchC, Simulator, Module
from python.env       import Env
from python.benchmark import Benchmark, App
from python           import utils     

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
    env   = Env()
    archc = ArchC()
    simulators = []
    mibench  = Benchmark('MiBench')
    spec2006 = Benchmark('Spec2006')

    config = ConfigParser()
    config.read(configfile)

    modules = []
    if (config.has_section('nightly')):
        if (config.has_option('nightly', 'modules file')):
            modfile   = config['nightly']['modules file']
            modfile   = os.path.dirname(configfile)+"/"+modfile
            modconfig = ConfigParser()
            modconfig.read(modfile)
            for _module in modconfig.sections():
                module = Module(_module)
                if (modconfig.has_option (_module, 'generator')):
                    module.set_generator(modconfig.get(_module,'generator'))
                if (modconfig.has_option(_module, 'options')):
                    module.set_options (modconfig.get(_module,'options'))
                if (modconfig.has_option(_module, 'desc')):
                    module.set_desc (modconfig.get(_module,'desc'))
                modules.append(module)
        else:
            abort()

        if (config.has_option('nightly', 'workspace')):
            workspace = config.get('nightly','workspace')
            env.set_workspace(workspace)

        if (config.has_option('nightly', 'htmlroot')):
            htmlroot  = config.get('nightly','htmlroot')
            env.set_htmlroot(htmlroot)
    else:
        abort()

    env.printenv()

    for _app in config.options('mibench'):
        app = App(_app)
        for dataset in utils.parselist(config.get('mibench',_app)):
            app.append_dataset(dataset)
        mibench.append_app(app)
    mibench.printbench()

    for _app in config.options('spec2006'):
        app = App(_app)
        for dataset in utils.parselist(config.get('spec2006',_app)):
            app.append_dataset(dataset)
        spec2006.append_app(app)
    spec2006.printbench()

    if (config.has_section('archc')):
        if (config.has_option('archc','where')):
            archc.set_env(env)
            archc.set_where(config.get('archc','where'))
        else:
            abort()

        if (config.has_option('archc','systemc')):
            archc.set_systemc(config.get('archc','systemc'))

        if (config.has_option('archc','binutils')):
            archc.set_binutils(config.get('archc','binutils'))

        if (config.has_option('archc','gdb')):
            archc.set_gdb(config.get('archc','gdb'))
    else:
        abort()
   
    for _model in ['mips', 'arm', 'powerpc', 'sparc']:
        if (config.has_section(_model)):
            where = ""
            if (config.has_option(_model,'where')):
                where = config.get(_model,'where')
            else:
                abort()
          
            for module in utils.parselist(config.get(_model,'modules')):
                sim = Simulator(_model+"-"+module, env)
                sim.set_where(where)
                for _module in modules:
                    if _module.name == module:
                        sim.set_module(_module)
                simulators.append(sim)
 
    for s in simulators:
        s.printsim()
    return config


def main():
    args   = command_line_handler()
    nightly = config_parser_handler(args.configfile)



#    print(config.sections())
#
#    for key in config['mips']:
#        print(key)
#
#    mips = config['mips']
#    print (mips['acsim'])


if __name__ == '__main__':
    main()  





