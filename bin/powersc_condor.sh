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

### Get env
cd ${SCRIPTROOT}
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. $CONFIGFILE
cd -  &> /dev/null

ORIG_LOGROOT=${LOGROOT}
ORIG_HTMLLOG=${HTMLLOG}

### This lines override the variables defined by $CONFIGFILE to a local path in Condor Machine
TESTROOT="/tmp/$(basename $TESTFOLDER)"    
LOGROOT="/tmp/$(basename $TESTFOLDER)_public_html/"
HTMLINDEX="${LOGROOT}/$(basename $HTMLINDEX)"
HTMLLOG="${LOGROOT}/${HTMLPREFIX}-index.htm"

### Copy the Archc compiled and installed to local machine
cp -r $TESTFOLDER /tmp/

### change the env from original TESTROOT to local TESTROOT
mkdir ${LOGROOT} &> /dev/null
cd ${TESTROOT}/acsim

###########################################
echo -ne "\n*** Job Started ***\n\n"
create_test_env     $MODEL     $RUN_MODEL

powersc_test  $MODEL     $RUN_MODEL     $REV_MODEL     $LINK_MODEL        $CROSS_MODEL   $ENDIAN
sed -i "s@__${MODEL}_powersc_replace__@$(cat $HTMLLOG)@g" $ORIG_HTMLLOG && rm ${HTMLLOG}

echo -ne "\n*** Job Concluded ***\n"
###########################################

### Get generates files
cp $LOGROOT/* $ORIG_LOGROOT 

rm -rf $LOGROOT
rm -rf $TESTROOT

### Restoring the modified variables
. ${SCRIPTROOT}/${CONFIGFILE}
TESTROOT="$TESTFOLDER"

