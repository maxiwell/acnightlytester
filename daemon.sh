#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/lsc/projetos/archc/nightly/acnightlytester/daemon.sh 
#
###########################################################################

cd /home/lsc/projetos/archc/nightly/acnightlytester/
./acnightly.py conf/config.yaml $1 --condor
#rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/

