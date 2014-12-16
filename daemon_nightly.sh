#!/bin/bash

. site.conf
export LD_LIBRARY_PATH="$SYSTEMCPATH/lib-linux64/"
cd /local/archc/acnightlytester &> /dev/null
./nightlytester.sh site.conf  $1
rsync -Rrazp -v public_html /home/lsc/projetos/archc/acnightlytester/
cd - &> /dev/null

