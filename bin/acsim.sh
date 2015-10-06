#!/bin/bash

acsim_build_model() {
    MODEL=$1
    MODELREV=$2
    USEACSIM=$3
    LOCAL_PARAMS=$4  # Each test have a specific set of params
    DIRSIMULATOR=$5     # Each test have a specific dir (e.g. arm/acsim, arm/accsim, arm/acstone)
    
    BUILD_FAULT="no"  # funcion return

    BUILD_RETCODE="false"
    if [ "$USEACSIM" != "no" ]; then    
        cd ${TESTROOT}/${MODEL}
        cp -r base $DIRSIMULATOR
        cd $DIRSIMULATOR
        TEMPFL=${RANDOM}.out
        echo -ne "\n Building ${MODEL} ArchC Model with [ ${LOCAL_PARAMS} ] params..."
        if [ -e Makefile.archc ]; then
            make -f Makefile.archc distclean &> /dev/null
        fi
        ${TESTROOT}/acinstall/bin/acsim ${MODEL}.ac ${LOCAL_PARAMS} > $TEMPFL 2>&1 && make -f Makefile.archc >> $TEMPFL 2>&1  
        BUILD_RETCODE=$?
        HTMLBUILDLOG=${HTML_TESTROOT}/${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm
        initialize_html $HTMLBUILDLOG "${MODEL} rev $MODELREV build output"
        format_html_output $TEMPFL $HTMLBUILDLOG
        finalize_html $HTMLBUILDLOG ""
        rm $TEMPFL

        if [ $BUILD_RETCODE -ne 0 ]; then
            echo -ne "<td><b><font color="crimson"> Failed </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td><td>-</td><td>$HOSTNAME</td></th>" >> $HTMLLOG_TESTROOT
            echo -ne "ACSIM \e[31mfailed\e[m to build $MODEL model.\n"
            BUILD_FAULT="yes"
            do_abort
        else
            echo -ne "<td><b><font color="green"> OK </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-build-log.htm\">log</a>)</td>" >> $HTMLLOG_TESTROOT
        fi
    fi
}

acsim_run() {
  MODEL=$1
  MODELBENCHROOT=$2
  MODELSPECROOT=$3
  MODELREV=$4
  DIRSIMULATOR=$5  # Each test have simulators with a specific set of params (e.g. arm/acsim, arm/acstone, arm/powersc)

  # Preparing test script
  ARCH="${MODEL}"
  SIMULATOR="${TESTROOT}/${MODEL}/$DIRSIMULATOR/${MODEL}.x --load="
  GOLDENROOT=${TESTROOT}/acsim/GoldenMibench
  GOLDENSPECROOT=${TESTROOT}/acsim/GoldenSpec
  MIBENCHROOT=${MODELBENCHROOT} 
  SPECROOT=${MODELSPECROOT} 
  STATSROOT=${BENCHROOT}/stats
  # Collect statistical information 
  if [ "$COLLECT_STATS" != "no" ]; then
    mkdir -p ${STATSROOT}
    cp ${SCRIPTROOT}/collect_stats.py ${STATSROOT}
  fi
  export ARCH
  export DIRSIMULATOR
  export SIMULATOR 
  export RUNSMALL   # ==================================
  export RUNLARGE   # 
  export RUNTEST    #
  export RUNTRAIN   # ================================== 
  export GOLDENROOT
  export GOLDENSPECROOT
  export MIBENCHROOT
  export SPECROOT
  export STATSROOT
  export COLLECT_STATS
  export RUN_POWERSC

  # Define which programs to test (definition in nightlytester.conf)  
  export BASICMATH
  export BITCOUNT
  export QUICKSORT
  export SUSAN
  export ADPCM
  export CRC
  export FFT
  export GSM
  
  export PATRICIA
  export RIJNDAEL
  export SHA
  export JPEG
  export LAME

  export BZIP_2
  export GCC  
  export MCF 
  export GOBMK    
  export HMMER      
  export SJENG 	    
  export LIBQUANTUM
  export H264        
  export OMNETPP    
  export ASTAR      

  export ENDIAN

  export TESTROOT
  export TESTCOMPILER
  export TESTCOMPILERCXX
  export TESTAR
  export TESTRANLIB
  export TESTFLAG

  export -f is_spec2006_enabled

  cd ${TESTROOT}/acsim
  ./acsim_validation.sh
  
  FAILED=`grep -ne "Failed" ${HTML_TESTROOT}/${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}.htm`

  if [ -z "$FAILED" ]; then
      echo -ne "<td><b><font color="green"> OK </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}.htm\">Report</a>) </td>" >> $HTMLLOG_TESTROOT
  else
      echo -ne "<td><b><font color="crimson"> Failed </font></b>(<a href=\"${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}.htm\">Report</a>)</td>" >> $HTMLLOG_TESTROOT
  fi
}


acsim_html_table() {
    echo -ne "<h3>Testing: ACSIM </h3>\n" >> $HTMLLOG
    echo -ne "<p>Command used to build ACSIM models: <b> ./acsim model.ac ${ACSIM_PARAMS} </b> </p>\n" >> $HTMLLOG

    echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">\n" >> $HTMLLOG
    echo -ne "<tr><th>Model</th><th>Link/Path</th><th>Version</th><th>Compilation</th><th>Benchmark</th><th>Tested in</th></tr>\n" >> $HTMLLOG

    cp ${SCRIPTROOT}/bin/acsim_validation.sh ${TESTROOT}/acsim/acsim_validation.sh
    chmod u+x ${TESTROOT}/acsim/acsim_validation.sh

    for ARG in "$@"; do
        echo -ne "__REPLACELINE_${ARG}_acsim__\n" >> $HTMLLOG
    done

    finalize_html $HTMLLOG "</table></p>"
}



# $1: model name
# $2: var declared in .conf that define if model will execute
# $3: revision git of the model
# $4: Link source code
# $5: cross-compiler path of the model
# $6: endian
acsim_test(){
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

    echo -ne "\n Testing ACSIM..."
    echo -ne "<tr><td>${MODEL} </td><td>${LINK_MODEL}</td><td>${REV_MODEL}</td>" >> $HTMLLOG_TESTROOT

    acsim_build_model "${MODEL}" "${REV_MODEL}" "${RUN_MODEL}" "${ACSIM_PARAMS}" "acsim" 
    echo -ne "\n Running ${MODEL}... \n"

    export TESTCOMPILER="${CROSS_MODEL}/${TUPLE}-gcc" 
    export TESTCOMPILERCXX="${CROSS_MODEL}/${TUPLE}-g++"
    export TESTAR="${CROSS_MODEL}/${TUPLE}-ar$"
    export TESTRANLIB="${CROSS_MODEL}/${TUPLE}-ranlib"
    export TESTFLAG="-specs=archc -static"
    export ENDIAN
    export HTML_TESTROOT
    export HTMLPREFIX
    acsim_run ${MODEL} "${TESTROOT}/acsim/${MODEL}_mibench" "${TESTROOT}/acsim/${MODEL}_spec" "${REV_MODEL}" ${DIRSIMULATOR}

    CPUINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-cpuinfo.txt
    MEMINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-meminfo.txt
    cat /proc/cpuinfo > ${HTML_TESTROOT}/$CPUINFOFILE
    cat /proc/meminfo > ${HTML_TESTROOT}/$MEMINFOFILE
    echo -ne "<td> ${HOSTNAME} (<a href=\"${CPUINFOFILE}\">cpuinfo</a>, <a href=\"${MEMINFOFILE}\">meminfo</a>) </td></tr>\n" >> $HTMLLOG_TESTROOT

    finalize_test
}

