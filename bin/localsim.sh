#!/bin/bash

##########################################
# External function used: 
#   acsim_run: in 'acsim.sh'
##########################################

localsim_build_model() {
    MODELNAME=$1
    MODELREV=$2
    USEACSIM=$3
    LOCAL_PARAMS=$4  # Each test have a specific set of params
    DIRSIMULATOR=$5     # Each test have a specific dir (e.g. arm/acsim, arm/accsim, arm/acstone)

    BUILD_RETCODE="false"
    if [ "$USEACSIM" != "no" ]; then    
        cd ${TESTROOT}/${MODELNAME}
        cp -r modelbase $DIRSIMULATOR
        cd $DIRSIMULATOR
        TEMPFL=${RANDOM}.out
        echo -ne "\n Building ${MODELNAME} ArchC model from a local source simulator..."
        if [ -e Makefile.archc ]; then
            make -f Makefile.archc clean &> /dev/null
            make -f Makefile.archc >> $TEMPFL 2>&1
        else
            echo -ne "<p><b><font color=\"crimson\">${MODELNAME} Makefile.archc not found, necessary when LOCALSIMULATOR=yes. Check script parameters.</font></b></p>\n" >> $HTMLLOG
            finalize_html $HTMLLOG ""
            echo -ne "Local simulator \e[31mfailed\e[m. Makefile.archc not found; necessary when LOCALSIMULATOR=yes. Check script parameters.\n"
            do_abort
        fi 
        BUILD_RETCODE=$?
        HTMLBUILDLOG=${LOGROOT}/${HTMLPREFIX}-${MODELNAME}-${DIRSIMULATOR}-build-log.htm
        initialize_html $HTMLBUILDLOG "${MODELNAME} rev $MODELREV build output"
        format_html_output $TEMPFL $HTMLBUILDLOG
        finalize_html $HTMLBUILDLOG ""
        rm $TEMPFL

        if [ $BUILD_RETCODE -ne 0 ]; then
            echo -ne "<td><b><font color="crimson"> Failed </font></b>(<a href=\"${HTMLPREFIX}-${MODELNAME}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td><td>-</td></th>" >> $HTMLLOG
            echo -ne "ACSIM \e[31mfailed\e[m to build $MODELNAME model.\n"
        else
            echo -ne "<td><b><font color="green"> OK </font></b>(<a href=\"${HTMLPREFIX}-${MODELNAME}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td>" >> $HTMLLOG
        fi
    fi
}

localsim_prologue(){
    echo -ne "<h3>Testing: ACSIM </h3>\n" >> $HTMLLOG
    echo -ne "<p>Testing a Local Simulator. The 'acsim' was not run</p>\n" >> $HTMLLOG

    echo -ne "\n****************************************\n"
    echo -ne "* Testing Local Simulator             **\n"
    echo -ne "****************************************\n"

    cp ${SCRIPTROOT}/bin/acsim_validation.sh ${TESTROOT}/acsim/acsim_validation.sh
    chmod u+x ${TESTROOT}/acsim/acsim_validation.sh

    echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">" >> $HTMLLOG
    echo -ne "<tr><th>Component</th><th>Version</th><th>Compilation</th><th>Benchmark</th></tr>\n" >> $HTMLLOG

}

localsim_epilogue(){
    finalize_html $HTMLLOG "</table></p>"
}

# $1: model name
# $2: var declared in .conf that define if model will execute
# $3: revision git of the model
# $4: cross-compiler path of the model
# $5: endian
localsim_test(){
    MODEL=$1
    RUN_MODEL=$2
    REV_MODEL=$3
    CROSS_MODEL=$4
    ENDIAN=$5

    if [ $RUN_MODEL == "no" ]; then
        return 0
    fi

    # Get the cross-compiler tuple 
    TUPLE=`ls ${CROSS_MODEL} | cut -d- -f1-3 | uniq`
    if [ `echo $TUPLE | grep " " | wc -l` == "1" ]; then      
        # The TUPLE var contains a invalid string. Maybe the tuple have 2
        # words and the line above (cut -d- -f1-3) takes 3 (FIXME)
        echo -ne "\n ${MODEL} Failed in find a cross-compiler tuple string\n"
        return 1
    fi

    echo -ne "<tr><td>${MODEL} </td><td>${REV_MODEL}</td>" >> $HTMLLOG
    localsim_build_model "${MODEL}" "${REV_MODEL}" "${RUN_MODEL}" "${ACSIM_PARAMS}" "acsim" 
    echo -ne "\n Running ${MODEL}... \n"

    export TESTCOMPILER="${CROSS_MODEL}/${TUPLE}-gcc" 
    export TESTCOMPILERCXX="${CROSS_MODEL}/${TUPLE}-g++"
    export TESTAR="${CROSS_MODEL}/${TUPLE}-ar$"
    export TESTRANLIB="${CROSS_MODEL}/${TUPLE}-ranlib"
    export TESTFLAG="-specs=archc -static"
    export ENDIAN
    export LOGROOT
    export HTMLPREFIX
    acsim_run ${MODEL} "${TESTROOT}/acsim/${MODEL}_mibench" "${TESTROOT}/acsim/${MODEL}_spec" "${REV_MODEL}" "acsim" 
    
}
