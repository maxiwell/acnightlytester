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
SCRIPTFOLDER=$8
CONFIGFILE=$9

. ${SCRIPTFOLDER}/bin/helper_functions.sh
. ${SCRIPTFOLDER}/bin/acsim.sh
. ${SCRIPTFOLDER}/bin/powersc.sh
. ${SCRIPTFOLDER}/$CONFIGFILE

cp -r $TESTFOLDER /tmp/

# This lines override the variables defined by $CONFIGFILE
TESTROOT="/tmp/$(basename $TESTFOLDER)"    
SCRIPTROOT="${SCRIPTFOLDER}"        
LOGROOT="/tmp/$(basename $TESTFOLDER)_public_html/"
HTMLINDEX="${LOGROOT}/$(basename $HTMLINDEX)"
HTMLLOG=${LOGROOT}/${HTMLPREFIX}-index.htm

mkdir ${LOGROOT}

cd ${TESTROOT}/acsim

create_test_env     $MODEL     $RUN_MODEL 
acsim_test          $MODEL     $RUN_MODEL     $REV_MODEL     $LINK_MODEL        $CROSS_MODEL   $ENDIAN



