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
TESTFOLDER=$7
STARTUP_MACHINE=$8

#Get env: $SCRIPTROOT must be in NFS (like /home/lsc/...)
_PWD=${PWD}
cd ${SCRIPTROOT}
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. $CONFIGFILE
cd $_PWD

initialize_condor

# Used in 'finalize_condor' 
export DIRSIMULATOR="powersc"
export ORIG_HTMLLOG=${HTMLLOG}

# Used in 'create_test_env' and '*_test'
export TESTROOT="${PWD}/$(basename $TESTFOLDER)"    
export LOGTMP="${TESTROOT}/public_html/"
export HTMLLOG="${LOGTMP}/${HTMLPREFIX}-index.htm"

# ArchC must be moved to the PATH set in the PREFIX instalation in Startup Machine
# I assume that the Condor Nodes have the PATH used by Startup Machine (like /tmp/...)
# If the Folder exists, so the ArchC already been installed by other Job. 
if [ ! -d $TESTFOLDER ]; then
	mkdir -p $TESTFOLDER
	cp -r ${TESTROOT}/acinstall ${TESTFOLDER}
fi

# Enter in local TESTROOT
cd ${TESTROOT}/acsim

create_test_env $MODEL $RUN_MODEL $CROSS_MODEL $ORIG_HTMLLOG
powersc_test  $MODEL  $RUN_MODEL  $REV_MODEL  $LINK_MODEL  $CROSS_MODEL   $ENDIAN

finalize_condor

