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

echo "Oii"
exit

# Folder that I will copy the $TESTROOT to execute locally. 
CONDOR_FOLDER=/tmp/condor/
mkdir -p ${CONDOR_FOLDER}
if [ $? -ne 0 ]; then
    echo -ne "Create file ${CONDOR_FOLDER} failed\n"
    return 1
fi

### Copy the all files compiled and installed by startup machine (archc2.lsc.ic.unicamp.br) to local machine (nodeX)
# Line to test in a same machine, before send to condor
cp -r ${TESTFOLDER} ${CONDOR_FOLDER}
# Line to use in real condor machine
#cp -r $(basename $TESTFOLDER) ${CONDOR_FOLDER}

### Get ENV. $SCRIPTROOT must be in NFS (like /home/lsc/...)
SAVE_ENV=$PWD
cd ${SCRIPTROOT}
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. $CONFIGFILE
cd $SAVE_ENV  &> /dev/null

ORIG_HTMLLOG=${HTMLLOG}

### This lines override the variables defined by $CONFIGFILE to a local path in Condor Machine
export TESTROOT="${CONDOR_FOLDER}/$(basename $TESTFOLDER)"    
export LOGTMP="${TESTROOT}/public_html/"
export HTMLLOG="${LOGTMP}/${HTMLPREFIX}-index.htm"

# Enter in local TESTROOT
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
cp -r ${LOGTMP}/* ${LOGROOT}/ 

chmod 777 ${CONDOR_FOLDER} -R
rm -rf ${CONDOR_FOLDER} 
