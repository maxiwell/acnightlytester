#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/lsc/projetos/archc/nightly/acnightlytester/daemon.sh 
#
###########################################################################

cd /home/lsc/projetos/archc/nightly/acnightlytester/
ts=`date +"%Y%m%d"`
./acnightly.py conf/site.yaml --condor &> log_${ts}.txt

