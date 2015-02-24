#!/bin/bash

############################################################################
#
# This script will be called by cron:
# 0 0 * * * /home/lsc/projetos/archc/nightly/acnightlytester/daemon_nightly.sh
#
###########################################################################

./nightlytester.sh site.conf  $1 $2
#rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/

