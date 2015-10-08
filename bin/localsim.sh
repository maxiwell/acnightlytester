#!/bin/bash

##########################################
# External function used: 
#   acsim_run: in 'acsim.sh'
##########################################

localsim_build_model() {
    MODEL=$1
    MODELREV=$2
    USEACSIM=$3
    LOCAL_PARAMS=$4  # Each test have a specific set of params
    DIRSIMULATOR=$5     # Each test have a specific dir (e.g. arm/acsim, arm/accsim, arm/acstone)

    BUILD_RETCODE="false"
    if [ "$USEACSIM" != "no" ]; then    
        cd ${TESTROOT}/${MODEL}
        cp -r base $DIRSIMULATOR
        cd $DIRSIMULATOR
        TEMPFL=${RANDOM}.out
        echo -ne "\n Building ${MODEL} ArchC model from a local source simulator..."
        if [ -e Makefile ]; then
            make clean &> /dev/null
            make  >> $TEMPFL 2>&1
        else
            echo -ne "<p><b><font color=\"crimson\">${MODEL} Makefile not found, necessary when LOCALSIMULATOR=yes. Check script parameters.</font></b></p>\n" >> $HTMLLOG_TESTROOT
            finalize_html $HTMLLOG_TESTROOT ""
            echo -ne "Local simulator \e[31mfailed\e[m. Makefile not found; necessary when LOCALSIMULATOR=yes. Check script parameters.\n"
            do_abort
        fi 
        BUILD_RETCODE=$?
        HTMLBUILDLOG=${HTML_TESTROOT}/${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm
        initialize_html $HTMLBUILDLOG "${MODEL} rev $MODELREV build output"
        format_html_output $TEMPFL $HTMLBUILDLOG
        finalize_html $HTMLBUILDLOG ""
        rm $TEMPFL

        if [ $BUILD_RETCODE -ne 0 ]; then
            echo -ne "<td><b><font color="crimson"> Failed </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td><td>-</td><td>$HOSTNAME</td></th>" >> $HTMLLOG_TESTROOT
            echo -ne "ACSIM \e[31mfailed\e[m to build $MODEL model.\n"
            do_abort
        else
            echo -ne "<td><b><font color="green"> OK </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td>" >> $HTMLLOG_TESTROOT
        fi
    fi
}

# $1: model name
# $2: var declared in .conf that define if model will execute
# $3: revision git of the model
# $4: Link source code
# $5: cross-compiler path of the model
# $6: endian
localsim_test(){
    MODEL=$1
    RUN_MODEL=$2
    REV_MODEL=$3
    LINK_MODEL=$4
    CROSS_MODEL=$5
    ENDIAN=$6

    DIRSIMULATOR="acsim"

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

    echo -ne "\n Testing local simulator..."
    echo -ne "<tr><td>${MODEL} </td><td>${LINK_MODEL}</td><td>${REV_MODEL}</td>" >> $HTMLLOG_TESTROOT

    localsim_build_model "${MODEL}" "${REV_MODEL}" "${RUN_MODEL}" "${ACSIM_PARAMS}" "acsim" 
    echo -ne "\n Running ${MODEL}... \n"

    export TESTCOMPILER="${CROSS_MODEL}/${TUPLE}-gcc" 
    export TESTCOMPILERCXX="${CROSS_MODEL}/${TUPLE}-g++"
    export TESTAR="${CROSS_MODEL}/${TUPLE}-ar$"
    export TESTRANLIB="${CROSS_MODEL}/${TUPLE}-ranlib"
    export TESTFLAG="-specs=archc -static"
    export ENDIAN
    export HTML_TESTROOT
    export HTMLPREFIX
    acsim_run ${MODEL} "${TESTROOT}/acsim/${MODEL}_mibench" "${TESTROOT}/acsim/${MODEL}_spec" "${REV_MODEL}" "acsim" 
    
    CPUINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-cpuinfo.txt
    MEMINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-meminfo.txt
    cat /proc/cpuinfo > ${HTML_TESTROOT}/$CPUINFOFILE
    cat /proc/meminfo > ${HTML_TESTROOT}/$MEMINFOFILE
    echo -ne "<td> ${HOSTNAME} (<a href=\"${CPUINFOFILE}\">cpuinfo</a>, <a href=\"${MEMINFOFILE}\">meminfo</a>) </td></tr>\n" >> $HTMLLOG_TESTROOT

    finalize_test


}





