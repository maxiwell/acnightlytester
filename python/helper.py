#!/usr/bin/env python3

import urllib.request 
import os
import shutil 
from python import utils
import tarfile

#
#class DownloadSource (DownloadHelper):
#
#    url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"
#
#    def get_acstone(self, dest):
#        pkg = ['AllArchs-acstone.tar.bz2']
#        for p in pkg:
#            self.get_http(self.url_base+p, dest)
#
#    def get_acasm(self, dest):
#        pkg = ['acasm-validation.tar.bz2']
#        for p in pkg:
#            self.get_http(self.url_base+p, dest)
#
#    def get_mibench(self, dest):
#        pkg = ['GoldenMibench.tar.bz2', 'SourceMibench.tar.bz2'] 
#        for p in pkg:
#            self.get_http(self.url_base+p, dest)
#            tar = tarfile.open(dest+"/"+p)
#            tar.extractall(dest)
#            fullprefix = dest + tar.getnames()[0]
#            tar.close()
#
#    def get_spec(self, dest):
#        pkg = ['SourceSPEC2006.tar.bz2', 'GoldenSPEC2006.tar.bz2']
#        for p in pkg:
#            print("Getting "+p+" ... FAILED")
#            print("SPEC2006: sources are protected by copyright.")
#

