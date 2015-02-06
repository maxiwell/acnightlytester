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

CONDOR_FOLDER=/tmp/condor

mkdir -p ${CONDOR_FOLDER}
if [ $? -ne 0 ]; then
    echo -ne "Create file ${CONDOR_FOLDER} failed\n"
    return 1
fi

### Get env
### SCRIPTROOT must be in NFS (like /home/lsc/...)
cd ${SCRIPTROOT}
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. $CONFIGFILE
cd -  &> /dev/null

ORIG_LOGROOT=${LOGROOT}
ORIG_HTMLLOG=${HTMLLOG}

### This lines override the variables defined by $CONFIGFILE to a local path in Condor Machine
export TESTROOT="${CONDOR_FOLDER}/$(basename $TESTFOLDER)"    
export LOGROOT="${CONDOR_FOLDER}/$(basename $TESTFOLDER)_public_html/"
export HTMLINDEX="${LOGROOT}/$(basename $HTMLINDEX)"
export HTMLLOG="${LOGROOT}/${HTMLPREFIX}-index.htm"

### Copy the Archc compiled and installed to local machine
cp -r ${TESTFOLDER} ${CONDOR_FOLDER}

### change the env from original TESTROOT to local TESTROOT
mkdir ${LOGROOT} &> /dev/null
cd ${TESTROOT}/acsim

###########################################
echo -ne "\n*** Job Started ***\n"
create_test_env $MODEL $RUN_MODEL $CROSS_MODEL $ORIG_HTMLLOG
acsim_test  $MODEL  $RUN_MODEL  $REV_MODEL  $LINK_MODEL  $CROSS_MODEL   $ENDIAN
sed -i "s@__${MODEL}_acsim_replace__@$(cat $HTMLLOG)@g" $ORIG_HTMLLOG 
rm ${HTMLLOG}

echo -ne "\n*** Job Concluded ***\n"
###########################################

### Get generates files
cp $LOGROOT/* $ORIG_LOGROOT 

rm -rf $LOGROOT &> /dev/null
rm -rf $TESTROOT &> /dev/null

### Restoring the modified variables
. ${SCRIPTROOT}/${CONFIGFILE}
TESTROOT="$TESTFOLDER"

chmod 777 ${CONDOR_FOLDER} -R
rm -rf ${CONDOR_FOLDER} 

