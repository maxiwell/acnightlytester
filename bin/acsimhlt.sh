#!/bin/bash

##########################################
# External function used: 
#   acsim_build_model:  in 'acsim.sh'
#   acsim_run        :  in 'acsim.sh'
##########################################

acsimhlt_html_table() {
    echo -ne "<h3>Testing: ACSIM High Level Trace </h3>\n" >> $HTMLLOG
    echo -ne "<p>Command used to build High Level Trace models: <b> ./acsim model.ac ${ACSIM_PARAMS} -hlt </b> </p>\n" >> $HTMLLOG
 
    echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">" >> $HTMLLOG
    echo -ne "<tr><th>Model</th><th>Link/Path</th><th>Version</th><th>Compilation</th><th>Benchmark</th><th>Tested in</th></tr>\n" >> $HTMLLOG

    cp ${SCRIPTROOT}/bin/acsim_validation.sh ${TESTROOT}/acsim/acsim_validation.sh
    chmod u+x ${TESTROOT}/acsim/acsim_validation.sh

    for ARG in "$@"; do
        echo -ne "__REPLACELINE_${ARG}_acsimhlt__\n" >> $HTMLLOG
    done

    finalize_html $HTMLLOG "</table></p>"
}


# ACSIM HLTRACE does not execute large tests (very slow). a.k.a SPEC2006 and MiBench LARGE
acsimhlt_run() {
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
  export COMPILE    # Definition in nightlytester.conf
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

  # Salve original values
  _BZIP_2=$BZIP_2
  _GCC=$GCC
  _MCF=$MCF
  _GOBMK=$GOBMK
  _HMMER=$HMMER    
  _SJENG=$SJENG    
  _LIBQUANTUM=$LIBQUANTUM
  _H264=$H264 
  _OMNETPP=$OMNETPP
  _ASTAR=$ASTAR
  _RUNLARGE=$RUNLARGE  
  _RUNTEST=$RUNTEST

  # Remove slowly tests
  export BZIP_2="no"
  export GCC="no"
  export MCF="no"
  export GOBMK="no" 
  export HMMER="no"      
  export SJENG="no" 	    
  export LIBQUANTUM="no"
  export H264="no"        
  export OMNETPP="no"    
  export ASTAR="no"
  export RUNLARGE="no"  
  export RUNTEST="no"

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

  # restore original Values
  BZIP_2=$_BZIP_2
  GCC=$_GCC
  MCF=$_MCF
  GOBMK=$_GOBMK
  HMMER=$_HMMER    
  SJENG=$_SJENG    
  LIBQUANTUM=$_LIBQUANTUM
  H264=$_H264 
  OMNETPP=$_OMNETPP
  ASTAR=$_ASTAR
  RUNLARGE=$_RUNLARGE  
  RUNTEST=$_RUNTEST
}


# $1: model name
# $2: var declared in .conf that define if model will execute
# $3: revision git of the model
# $4: link source code
# $5: cross-compiler path of the model
# $6: endian
acsimhlt_test() {
    MODEL=$1
    RUN_MODEL=$2
    REV_MODEL=$3
    LINK_MODEL=$4
    CROSS_MODEL=$5
    ENDIAN=$6
    
    DIRSIMULATOR="acsimhlt"

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

    echo -ne "\n Testing ACSIM HLTRACE..."
    echo -ne "<tr><td>${MODEL} </td><td>${LINK_MODEL}</td><td>${REV_MODEL}</td>" >> $HTMLLOG_TESTROOT

    acsim_build_model "${MODEL}" "${REV_MODEL}" "${RUN_MODEL}" "${ACSIM_PARAMS} -hlt" "acsimhlt" 
    echo -ne "\n Running ${MODEL}... \n"

    export TESTCOMPILER="${CROSS_MODEL}/${TUPLE}-gcc" 
    export TESTCOMPILERCXX="${CROSS_MODEL}/${TUPLE}-g++"
    export TESTAR="${CROSS_MODEL}/${TUPLE}-ar$"
    export TESTRANLIB="${CROSS_MODEL}/${TUPLE}-ranlib"
    export TESTFLAG="-specs=archc -static -g"
    export ENDIAN
    export HTML_TESTROOT
    export HTMLPREFIX
    acsimhlt_run ${MODEL} "${TESTROOT}/acsim/${MODEL}_mibench" "${TESTROOT}/acsim/${MODEL}_spec" "${REV_MODEL}" ${DIRSIMULATOR}

    CPUINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-cpuinfo.txt
    MEMINFOFILE=${HTMLPREFIX}-${MODEL}-${DIRSIMULATOR}-meminfo.txt
    cat /proc/cpuinfo > ${HTML_TESTROOT}/$CPUINFOFILE
    cat /proc/meminfo > ${HTML_TESTROOT}/$MEMINFOFILE
    echo -ne "<td> ${HOSTNAME} (<a href=\"${CPUINFOFILE}\">cpuinfo</a>, <a href=\"${MEMINFOFILE}\">meminfo</a>) </td></tr>\n" >> $HTMLLOG_TESTROOT

    finalize_test
}

