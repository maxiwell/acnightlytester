#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/lsc/projetos/archc/nightly/acnightlytester/daemon.sh 
#
###########################################################################

cd /home/lsc/projetos/archc/nightly/acnightlytester/
./acnightly.py config/site.yaml --condor
#rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/

