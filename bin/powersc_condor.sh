#!/bin/bash

############################
### Condor script
############################

MODEL=$1
RUN_MODEL=$2
REV_MODEL=$3     
LINK_MODEL=$4       
CROSS_MODEL=$5 
ENDIAN=$6
TESTROOT_LINK=$7

#Get env: $SCRIPTROOT must be in NFS (like /home/lsc/...)
_PWD=${PWD}
cd ${SCRIPTROOT}
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. $CONFIGFILE
cd $_PWD

# Change the TESTROOT to use the default PATH in CONDOR machine (/var/lib/condor/hostname/execute/dir_$(pid))
export TESTROOT="${PWD}/$(basename $TESTROOT_LINK)"    
export HTML_TESTROOT="${TESTROOT}/public_html/"
export HTMLLOG_TESTROOT="${HTML_TESTROOT}/${HTMLPREFIX}-index.htm"

# ArchC must be moved to the PATH set in the PREFIX instalation in Startup Machine
# I assume that the Condor Nodes have the PATH used by Startup Machine (like /tmp/...)
# If the Folder exists, so the ArchC already been installed by other Job. 
if [ ! -d $TESTROOT_LINK ]; then
	mkdir -p $TESTROOT_LINK
    cp -r ${TESTROOT}/acinstall ${TESTROOT_LINK}
fi

# Enter in local TESTROOT
cd ${TESTROOT}/acsim

powersc_test  $MODEL  $RUN_MODEL  $REV_MODEL  $LINK_MODEL  $CROSS_MODEL   $ENDIAN

