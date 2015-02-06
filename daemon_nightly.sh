#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/notroot/nightly/acnightlytester/daemon_nightly.sh
#
###########################################################################

cd /home/notroot/nightly/acnightlytester &> /dev/null
./nightlytester.sh site.conf  $1
rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/
cd - &> /dev/null

