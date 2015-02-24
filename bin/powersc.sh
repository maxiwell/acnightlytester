#!/bin/bash

##########################################
# External function used: 
#   acsim_build_model:  in 'acsim.sh'
#   acsim_run        :  in 'acsim.sh'
##########################################

acsim_finalize(){
    MODEL=$1
    sed -i "s@__REPLACELINE_${MODEL}_powersc_@$(cat $HTMLLOG_TESTROOT)@g" $HTMLLOG
}

powersc_html_table() {
    echo -ne "<h3>Testing: ACSIM POWERSC </h3>\n" >> $HTMLLOG
    echo -ne "<p>Command used to build PowerSC models: <b> ./acsim model.ac ${ACSIM_PARAMS} -pw </b> </p>\n" >> $HTMLLOG
    echo -ne "<p> <b>Note: </b> ARM and PowerPC models don't have POWERSC table files.</p>\n" >> $HTMLLOG 
 
    echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">" >> $HTMLLOG
    echo -ne "<tr><th>Model</th><th>Link/Path</th><th>Version</th><th>Compilation</th><th>Benchmark</th><th>Tested in</th></tr>\n" >> $HTMLLOG

    cp ${SCRIPTROOT}/bin/acsim_validation.sh ${TESTROOT}/acsim/acsim_validation.sh
    chmod u+x ${TESTROOT}/acsim/acsim_validation.sh

    for ARG in "$@"; do
        echo -ne "__REPLACELINE_${ARG}_powersc__\n" >> $HTMLLOG
    done

    finalize_html $HTMLLOG "</table></p>"
}


# $1: model name
# $2: var declared in .conf that define if model will execute
# $3: revision git of the model
# $4: link source code
# $5: cross-compiler path of the model
# $6: endian
powersc_test() {
    MODEL=$1
    RUN_MODEL=$2
    REV_MODEL=$3
    LINK_MODEL=$4
    CROSS_MODEL=$5
    ENDIAN=$6

    if [ $RUN_MODEL == "no" ]; then
        return 0
    fi

    create_test_env ${MODEL}  ${RUN_MODEL}  ${CROSS_MODEL} ${HTMLLOG}

    # Get the cross-compiler tuple 
    TUPLE=`ls ${CROSS_MODEL} | cut -d- -f1-3 | uniq`
    if [ `echo $TUPLE | grep " " | wc -l` == "1" ]; then      
        # The TUPLE var contains a invalid string. Maybe the tuple have 2
        # words and the line above (cut -d- -f1-3) takes 3 (FIXME)
        echo -ne "\n ${MODEL} Failed in find a cross-compiler tuple string\n"
        return 1
    fi

    echo -ne "\n Testing ACSIM POWERSC..."
    echo -ne "<tr><td>${MODEL} </td><td>${LINK_MODEL}</td><td>${REV_MODEL}</td>" >> $HTMLLOG_TESTROOT
    acsim_build_model "${MODEL}" "${REV_MODEL}" "${RUN_MODEL}" "${ACSIM_PARAMS} -pw" "powersc" 
    echo -ne "\n Running ${MODEL}... \n"

    export TESTCOMPILER="${CROSS_MODEL}/${TUPLE}-gcc" 
    export TESTCOMPILERCXX="${CROSS_MODEL}/${TUPLE}-g++"
    export TESTAR="${CROSS_MODEL}/${TUPLE}-ar$"
    export TESTRANLIB="${CROSS_MODEL}/${TUPLE}-ranlib"
    export TESTFLAG="-specs=archc -static"
    export ENDIAN
    export HTML_TESTROOT
    export HTMLPREFIX
    acsim_run ${MODEL} "${TESTROOT}/acsim/${MODEL}_mibench" "${TESTROOT}/acsim/${MODEL}_spec" "${REV_MODEL}" "powersc" 

    CPUINFOFILE=${HTMLPREFIX}-${MODELNAME}-${DIRSIMULATOR}-cpuinfo.txt
    MEMINFOFILE=${HTMLPREFIX}-${MODELNAME}-${DIRSIMULATOR}-meminfo.txt
    cat /proc/cpuinfo > ${HTML_TESTROOT}/$CPUINFOFILE
    cat /proc/meminfo > ${HTML_TESTROOT}/$MEMINFOFILE
    echo -ne "<td> ${HOSTNAME} (<a href=\"${CPUINFOFILE}\">cpuinfo</a>, <a href=\"${MEMINFOFILE}\">meminfo</a>) </td></tr>\n" >> $HTMLLOG_TESTROO

    powersc_finalize ${MODEL}
}

