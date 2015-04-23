#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/lsc/projetos/archc/nightly/acnightlytester/daemon_nightly.sh 
#
###########################################################################

cd /home/lsc/projetos/archc/nightly/acnightlytester/
./nightlytester.sh site.conf  site.conf --condor
#rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/

