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

### Copy the all files compiled and installed by startup machine 
###n(archc2.lsc.ic.unicamp.br) to local machine (nodeX)

# If the startup machine is the same that execute the jobs (local testing, without CONDOR)
if [ ${STARTUP_MACHINE} == ${HOSTNAME} ]; then
    # Folder that I will copy the $TESTROOT to execute locally. 
    CONDOR_FOLDER=/tmp/condor/
    mkdir -p ${CONDOR_FOLDER}
    if [ $? -ne 0 ]; then
        echo -ne "Create file ${CONDOR_FOLDER} failed\n"
        return 1
    fi
    cp -r ${TESTFOLDER} ${CONDOR_FOLDER}
else
    # Folder that I will copy the $TESTROOT to execute locally. 
    CONDOR_FOLDER=/tmp/
    mkdir -p ${CONDOR_FOLDER}
    if [ $? -ne 0 ]; then
        echo -ne "Create file ${CONDOR_FOLDER} failed\n"
        return 1
    fi
    cp -r $(basename $TESTFOLDER) ${CONDOR_FOLDER}
fi

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
