#!/usr/bin/env python3

import urllib.request 
import os
import shutil 
from python import utils

class DownloadHelper:

    def get_http(self, url, dest):
        pkg = os.path.basename(url)
        print("Getting " + pkg + " over HTTP... ", end="", flush=True)
        utils.mkdir(dest)
        if ( urllib.request.urlretrieve(url, dest + "/" + pkg) ):
            print("OK");
        else:
            print("FAILED")

    def get_local(self, path, dest, pkg ):
        print("Getting " + pkg + " from " + path + "... ", end="", flush=True)
        utils.mkdir(dest)
        if ( utils.cp(path, dest) ):
            print("OK");
        else:
            print("FAILED")

    def git_clone(self, url, dest, pkg ):
        print("Cloning "+pkg + " from " + url + "... ", end="", flush=True)
        if (os.system("git clone "+url+" " \
                +dest+" > /dev/null 2>&1") == 0):
            print("OK")
        else:
            print("FAILED")

    def get_from(self, url_or_path, copy_to, pkg):
        if (url_or_path.startswith("./")) or (url_or_path.startswith("/")):
            self.get_local(url_or_path, copy_to, pkg)
        else:
            self.git_clone(url_or_path, copy_to, pkg)




class DownloadSource (DownloadHelper):

    url_base = "http://archc.lsc.ic.unicamp.br/downloads/Nightly/sources/"

    def get_acstone(self, dest):
        pkg = ['AllArchs-acstone.tar.bz2']
        for p in pkg:
            self.get_http(self.url_base+p, dest)

    def get_acasm(self, dest):
        pkg = ['acasm-validation.tar.bz2']
        for p in pkg:
            self.get_http(self.url_base+p, dest)

    def get_mibench(self, dest):
        pkg = ['GoldenMibench.tar.bz2', 'SourceMibench.tar.bz2'] 
        for p in pkg:
            self.get_http(self.url_base+p, dest)

    def get_spec(self, dest):
        pkg = ['SourceSPEC2006.tar.bz2', 'GoldenSPEC2006.tar.bz2']
        for p in pkg:
            print("Getting "+p+" ... FAILED")
            print("SPEC2006: sources are protected by copyright.")




#dh = DownloadSource()
#
#dh.get_acasm( dest = "/tmp/python");
#
#dc = DownloadCross()
#
#dc.get_mips( dest = "/tmp/python")

        



