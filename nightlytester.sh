#!/bin/bash

# NightlyTester script for ArchC.
# Clone ArchC source in GIT and tests current version
#
# ArchC Team

# Parameters adjustable by environment variables

NIGHTLYVERSION=3.0

####################################
### Import external funtions
####################################
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. bin/localsim.sh
. bin/acsimhlt.sh

####################################
### ENTRY POINT
####################################

command_line_handler $@


if [ ! -d $HTMLROOT ]; then
    echo -ne "\nERROR: The output path $HTMLROOT not exist\n\n"
    exit 1
fi


# Asserts when CONDOR mode on
if [[ $CONDOR == "yes" ]]; then
    if [[ $TESTROOT != "/tmp"* ]]; then
        echo -ne "When CONDOR is enabled, the TESTROOT must be into /tmp\n"
        exit 0
    fi

    # Check if condor is running LSC jobs. Probably is a Nightly execution.
    if [ `condor_q | grep lsc | wc -l` != "0" ]; then
        echo -ne "Condor is running LSC jobs. Is Nightly?\n"
        exit 0
    fi
fi

# Checks if other instance of Nightly is running in Sumit Machine
# If no --condor option, just checks if other instance of Nightly is running on local Machine
if [ -a /tmp/nightly-token ]; then
    echo -ne "A instance of Nightly is running...\n"
    exit 0
else
    touch /tmp/nightly-token
fi

export SUBMIT_MACHINE=$HOSTNAME

mkdir -p ${TESTROOT}

if [ ! -f $HTMLINDEX ]; then
    cp htmllogs/index.htm ${HTMLROOT}
    HTMLINDEX=${HTMLROOT}/index.htm
fi

# Initializing HTML log files
# Discover this run's number and prefix all our HTML files with it
export HTMLPREFIX=`sed -n -e '/<tr><td>[0-9]\+/{s/<tr><td>\([0-9]\+\).*/\1/;p;q}' <${HTMLINDEX}`
export LASTHTMLPREFIX=$HTMLPREFIX
export HTMLPREFIX=$(($HTMLPREFIX + 1))
export LASTARCHCREV=`grep -e "<tr><td>" < ${HTMLINDEX} | head -n 1 | cut -d\> -f 7 | cut -d\< -f 1`

if [ -z $LASTARCHCREV ]; then
    echo -ne "WARNING: Last ArchC Rev don't found.\n"
    LASTARCHCREV="na"
fi

export LASTEQCURRENT="yes"
export HTMLLOG=${HTMLROOT}/${HTMLPREFIX}-index.htm

# Temporary HTML files, necessary for Condor approach. If use $HTMLROOT and HTMLLOG only (without $HTML_TESTROOT), all page 
# generates by jobs (in many machines) would use the network. The $HTML_TESTROOT folder was a alternative
# to save Bandwidth and avoid the Race Condition, creating the pages locally. The only pages that use the NFS is $HTMLINDEX and 
# the 'component' table in $HTMLLOG, because they must be shared. 
export    HTML_TESTROOT=${TESTROOT}/public_html
export HTMLLOG_TESTROOT=${TESTROOT}/public_html/${HTMLPREFIX}-index.htm
mkdir -p ${HTML_TESTROOT}

initialize_html $HTMLLOG "NightlyTester ${NIGHTLYVERSION} Run #${HTMLPREFIX}"
export DATE=`LANG=en_US date '+%a %D %T'`
echo -ne "<p>Produced by NightlyTester @ ${DATE}</p>"   >> $HTMLLOG
echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">" >> $HTMLLOG
echo -ne "<tr><th>Component</th><th>Link/Path</th><th>Version</th><th>Status</th></tr>\n" >> $HTMLLOG

######################################
### Archc, git clone
######################################
ARCHCLINK="${ARCHCGITLINK}${ARCHCWORKINGCOPY}"
echo -ne "<tr><td>ArchC</td><td>${ARCHCLINK}</td>" >> $HTMLLOG

mkdir ${TESTROOT}/acsrc
cd ${TESTROOT}/acsrc
if [ -z "$ARCHCGITLINK" ]; then
  echo -ne "Copying ArchC source from a local directory...\n"
  cp -a ${ARCHCWORKINGCOPY} ./ &> /dev/null
  make distclean &> /dev/null
  [ $? -ne 0 ] && {
    echo -ne "<td><b><font color=\"crimson\"> Copy Failed </font></b></td><td> - </td></tr>\n" >> $HTMLLOG
    echo -ne "</table></p>\n" >> $HTMLLOG
    finalize_html $HTMLLOG ""
    echo -ne "Local directory copy \e[31mfailed\e[m. Check script parameters.\n"

  }
  ARCHCREV="N/A"
else
  echo -ne "Cloning ArchC GIT version...\n"
  git clone $ARCHCGITLINK . > /dev/null 2>&1  
  [ $? -ne 0 ] && {
    echo -ne "<td>-</td><td><b><font color=\"crimson\"> Clone Failed </font></b></td></tr>\n" >> $HTMLLOG
    echo -ne "</table></p>\n" >> $HTMLLOG
    finalize_html $HTMLLOG ""
    echo -ne "GIT clone \e[31mfailed\e[m. Check2 script parameters.\n"
    do_abort
  } 
  # Extract revision number
  cd ${TESTROOT}/acsrc &> /dev/null
  #ARCHCREV=$(git log | head -n1 | cut -c8-13)"..."$(git log | head -n1 | cut -c42-)
  ARCHREVFULL=$(git log | head -n1 | cut -d\  -f2)
  ARCHCREV=$(git log | head -n1 | cut -c8-15)".."
  if [ ${ARCHCREV} != ${LASTARCHCREV} ]; then
        LASTEQCURRENT="no"
  fi
  cd - &> /dev/null
fi

if [ -z "$ARCHCGITLINK" ]; then
  echo -ne "<td> ${ARCHCREV} </td><td>__ARCHC_LOG__</td></tr>" >> $HTMLLOG
else
  echo -ne "<td> <a href=https://github.com/ArchC/ArchC/commit/${ARCHREVFULL}> ${ARCHCREV} </a> </td><td>__ARCHC_LOG__</td></tr>" >> $HTMLLOG
fi

################################
### Get ArchC Models
################################
if [ "$RUN_ARM_ACSIM" != "no" -o "$RUN_ARM_ACASM" != "no" -o "$RUN_ARM_ACCSIM" != "no" ]; then
  clone_or_copy_model "arm" "${ARMGITLINK}" "${ARMWORKINGCOPY}" 
  ARMREV=${MODELREV}
fi
if [ "$RUN_SPARC_ACSIM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_SPARC_ACCSIM" != "no" ]; then
  clone_or_copy_model "sparc" "${SPARCGITLINK}" "${SPARCWORKINGCOPY}" 
  SPARCREV=${MODELREV}
fi
if [ "$RUN_MIPS_ACSIM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_MIPS_ACCSIM" != "no" ]; then
  clone_or_copy_model "mips" "${MIPSGITLINK}" "${MIPSWORKINGCOPY}" 
  MIPSREV=${MODELREV}
fi
if [ "$RUN_POWERPC_ACSIM" != "no" -o "$RUN_POWERPC_ACASM" != "no" -o "$RUN_POWERPC_ACCSIM" != "no" ]; then
  clone_or_copy_model "powerpc" "${POWERPCGITLINK}" "${POWERPCWORKINGCOPY}" 
  POWERPCREV=${MODELREV}
fi

########################################################
### Execute or Abort?
########################################################

if  [ "$FORCENIGHTLY" != "yes" ] &&       # If -f args; then Execute;
    ! have_workingcopy &&            # If WorkingCopy links; then Execute;
    [ "$LASTEQCURRENT" == "yes" ]; then  # If last execution have GIT Revisions equal the current, Abort
        echo -ne "All Revisions tested in last execution\n"
        rm ${HTMLROOT}/${HTMLPREFIX}-* 
        rm -rf ${HTML_TESTROOT}/* 
        do_abort
fi

#################
### binutils
#################
if [ "$RUN_ARM_ACASM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_POWERPC_ACASM" != "no" ]; then
    echo -ne "<p>Using user-supplied Binutils path: ${BINUTILSPATH}</p>\n" >> $HTMLLOG
    if [ -d $BINUTILSPATH ]; then
        echo -ne "Directory binutils found...\n"
        mkdir ${TESTROOT}/binutils
        cd ${TESTROOT}/binutils
        cp -r $BINUTILSPATH .
        BINUTILSPATH=${TESTROOT}/binutils/$(basename $BINUTILSPATH)
    elif [ -f $BINUTILSPATH ]; then
            echo -ne "Uncompressing binutils...\n"    
            mkdir ${TESTROOT}/binutils
            cd ${TESTROOT}/binutils
            tar -xjf $BINUTILSPATH
    else
        echo -ne "ACASM enabled and binutils not found.\n"
        do_abort
    fi
fi

################
### gdb
################
if is_acsim_enabled; then
  if [ "$RUN_ACSTONE" != "no" ]; then
    echo -ne "<p>Using user-supplied GDB path: ${GDBPATH}</p>\n" >> $HTMLLOG
    echo -ne "Copying GDB source...\n"
    mkdir ${TESTROOT}/gdb
    cd ${TESTROOT}/gdb
    cp -r $GDBPATH .
#    wget http://www.ic.unicamp.br/~auler/fix-gdb-6.4.patch > /dev/null 2>&1
#    patch -p1 < ./fix-gdb-6.4.patch 
    GDBPATH=${TESTROOT}/gdb/$(basename $GDBPATH)
  fi
fi

##########################################
### SystemC, untar, configure and install
##########################################
if is_acsim_enabled || is_accsim_enabled; then
    if [ -z ${SYSTEMCPATH} ]; then
        echo -ne "<tr><td>SystemC</td><td>${SYSTEMCSRC}</td><td>-</td>" >> $HTMLLOG
        echo -ne "Building/Installing SystemC...\n"

        TEMPFL=${RANDOM}.out
        mkdir ${TESTROOT}/systemc
        cd ${TESTROOT}/systemc
        tar -xvf ${SYSTEMCSRC} &> /dev/null
        cd systemc*
        ./configure --prefix=${TESTROOT}/systemc/install  >> $TEMPFL 2>&1 
        make  >> $TEMPFL 2>&1 
        make install  >> $TEMPFL 2>&1 
        RETCODE=$?
        HTMLBUILDLOG=${HTML_TESTROOT}/${HTMLPREFIX}-systemc-build-log.htm
        initialize_html $HTMLBUILDLOG "$(basename $(echo ${SYSTEMCSRC%.*})) build output"
        format_html_output $TEMPFL $HTMLBUILDLOG
        finalize_html $HTMLBUILDLOG ""
        rm $TEMPFL
        if [ $RETCODE -ne 0 ]; then
            echo -ne "<td> <b><font color=\"crimson\">Failed </font></b> (<a href=\"${HTMLPREFIX}-systemc-build-log.htm\">log</a>) </td> </tr>" >> $HTMLLOG
            echo -ne "</table></p>\n" >> $HTMLLOG
            finalize_html $HTMLLOG ""
            echo -ne "SystemC build \e[31mfailed\e[m.\n"
            do_abort
        else
            echo -ne "<td> <b><font color=\"green\">OK </font></b> (<a href=\"${HTMLPREFIX}-systemc-build-log.htm\">log</a>) </td> </tr>" >> $HTMLLOG
        fi
        export SYSTEMCPATH=${TESTROOT}/systemc/install
        export LD_LIBRARY_PATH=${SYSTEMCPATH}/lib-linux64/
    else
        echo -ne "<tr><td>SystemC</td><td>${SYSTEMCPATH}</td><td>-</td>" >> $HTMLLOG
        export LD_LIBRARY_PATH=${SYSTEMCPATH}/lib-linux64/
        if [ -d $LD_LIBRARY_PATH ]; then
            echo -ne "<td> <b><font color=\"green\">OK </font></b> </td></tr>" >> $HTMLLOG
        else
            echo -ne "<td> <b><font color=\"crimson\">Failed </font></b></td></tr>" >> $HTMLLOG
            echo -ne "</table></p>\n" >> $HTMLLOG
            finalize_html $HTMLLOG
            echo -ne "SystemC build \e[31mfailed\e[m.\n"
            do_abort
        fi
    fi
fi


##############################################
# Cross-compiler, reserving space in HTML table
#############################################
if [ ${COMPILE} == "yes" ]; then
    if [ ${RUN_ARM_ACSIM} == "yes" ]; then
        echo -ne "<tr><td>Cross arm</td><td>${CROSS_ARM}</td><td>-</td><td>__REPLACELINE_arm_cross__</td>" >> $HTMLLOG
    fi
    if [ ${RUN_SPARC_ACSIM} == "yes" ]; then
        echo -ne "<tr><td>Cross sparc</td><td>${CROSS_SPARC}</td><td>-</td><td>__REPLACELINE_sparc_cross__</td>" >> $HTMLLOG
    fi
    if [ ${RUN_MIPS_ACSIM} == "yes" ]; then
        echo -ne "<tr><td>Cross mips</td><td>${CROSS_MIPS}</td><td>-</td><td>__REPLACELINE_mips_cross__</td>" >> $HTMLLOG
    fi
    if [ ${RUN_POWERPC_ACSIM} == "yes" ]; then
        echo -ne "<tr><td>Cross powerpc</td><td>${CROSS_POWERPC}</td><td>-</td><td>__REPLACELINE_powerpc_cross__</td>" >> $HTMLLOG
    fi
else
    echo -ne "Precompiled unavailable: use the cross-compilers from ArchC.org and set COMPILER=yes in .config file\n"
    do_abort
fi

######################################
### ArchC, configure & install
######################################

if [ "$LOCALSIMULATOR" == "no" ]; then
    
    cd ${TESTROOT}/acsrc
    mkdir ${TESTROOT}/acinstall
    
    echo -ne "Building/Installing ArchC...\n"
    TEMPFL=${RANDOM}.out
    
    # ./configure
    ACSIM_STRING=""
    ACASM_STRING=""
    ACSTONE_STRING=""
    POWERSC_STRING=""
    ./autogen.sh > $TEMPFL 2>&1
    if is_acsim_enabled || is_accsim_enabled; then
        ACSIM_STRING="--with-systemc=${SYSTEMCPATH}"
    fi
    if [ "$RUN_ARM_ACASM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_POWERPC_ACASM" != "no" ]; then
        ACASM_STRING="--with-binutils=${BINUTILSPATH}"
    fi
    if [ "$RUN_ACSTONE" != "no" ]; then
        ACSTONE_STRING=" --with-gdb=${GDBPATH}"
    fi
    ./configure --prefix=${TESTROOT}/acinstall $ACSIM_STRING $ACASM_STRING $ACSTONE_STRING >> $TEMPFL 2>&1    
    
    RETCODE=0

    # Compile ArchC
    make >> $TEMPFL 2>&1 
    RETCODE=$(( $RETCODE + $? ))
    make install >> $TEMPFL 2>&1

    . ./env.sh
    RETCODE=$(( $RETCODE + $? ))
    HTMLBUILDLOG=${HTML_TESTROOT}/${HTMLPREFIX}-archc-build-log.htm
    initialize_html $HTMLBUILDLOG "ArchC rev $ARCHCREV build output"
    format_html_output $TEMPFL $HTMLBUILDLOG
    finalize_html $HTMLBUILDLOG ""
    rm $TEMPFL
    if [ $RETCODE -ne 0 ]; then
      sed -i "s@__ARCHC_LOG__@<b><font color=\"crimson\">Failed </font></b> (<a href=\"${HTMLPREFIX}-archc-build-log.htm\">log</a>)@g" $HTMLLOG
      echo -ne "</table></p>\n" >> $HTMLLOG
      finalize_html $HTMLLOG ""
      echo -ne "ArchC build \e[31mfailed\e[m.\n"
      do_abort
    else
      sed -i "s@__ARCHC_LOG__@<b><font color=\"green\">OK </font></b> (<a href=\"${HTMLPREFIX}-archc-build-log.htm\">log</a>)@g" $HTMLLOG
    fi
else
    sed -i "s@__ARCHC_LOG__@<b><font color=\"crimson\">Unused </font></b>@g" $HTMLLOG
fi

echo -ne "</table></p>\n" >> $HTMLLOG

##########################
# Golden Environment      
##########################

mkdir ${TESTROOT}/acsim

if is_acsim_enabled; then
    echo -ne "Uncompressing correct results for Mibench...\n"
    cd ${TESTROOT}/acsim
    tar -xjf ${SCRIPTROOT}/sources/GoldenMibench.tar.bz2
    [ $? -ne 0 ] && do_abort
    if is_spec2006_enabled; then
        echo -ne "Uncompressing correct results for SPEC2006...\n"
        tar -xjf ${SCRIPTROOT}/sources/GoldenSPEC2006.tar.bz2
        [ $? -ne 0 ] && do_abort
    fi
fi

ARMLINK="${ARMGITLINK}${ARMWORKINGCOPY}"
SPARCLINK="${SPARCGITLINK}${SPARCWORKINGCOPY}"
MIPSLINK="${MIPSGITLINK}${MIPSWORKINGCOPY}"
POWERPCLINK="${POWERPCGITLINK}${POWERPCWORKINGCOPY}"

# Copy the files generated by submit machine and Reset HTML_TESTROOT folder
cp -r ${HTML_TESTROOT}/* ${HTMLROOT}/   &> /dev/null
rm -rf ${HTML_TESTROOT}/*   &> /dev/null

if [ "$CONDOR" == "yes" ]; then

    ###################################################################
    # Here, the condor machine dispatch jobs. 
    ###################################################################

    export SCRIPTROOT
    export CONFIGFILE
    
    mkdir ${TESTROOT}/condor && cd  ${TESTROOT}/condor
    cp ${SCRIPTROOT}/bin/*_condor.sh .

    ######################
    # Testing ACSIM
    ######################
    acsim_html_table "arm" "sparc" "mips" "powerpc" 

    cp ${SCRIPTROOT}/template.condor arm-acsim.condor
    sed -i "s@EXECUTABLE@./acsim_condor.sh@g" arm-acsim.condor
    sed -i "s@ARGUMENTS@arm $RUN_ARM_ACSIM  $ARMREV $ARMLINK $CROSS_ARM little $TESTROOT@g" arm-acsim.condor
    sed -i "s@TESTROOT@${TESTROOT}@g" arm-acsim.condor
    sed -i "s@PREFIX@arm-acsim@g" arm-acsim.condor
    condor_submit arm-acsim.condor

    cp ${SCRIPTROOT}/template.condor sparc-acsim.condor
    sed -i "s@EXECUTABLE@./acsim_condor.sh@g" sparc-acsim.condor
    sed -i "s@ARGUMENTS@sparc $RUN_SPARC_ACSIM  $SPARCREV $SPARCLINK $CROSS_SPARC big $TESTROOT @g" sparc-acsim.condor
    sed -i "s@TESTROOT@${TESTROOT}@g" sparc-acsim.condor
    sed -i "s@PREFIX@sparc-acsim@g" sparc-acsim.condor
    condor_submit sparc-acsim.condor

    cp ${SCRIPTROOT}/template.condor mips-acsim.condor
    sed -i "s@EXECUTABLE@./acsim_condor.sh@g" mips-acsim.condor
    sed -i "s@ARGUMENTS@mips $RUN_MIPS_ACSIM  $MIPSREV $MIPSLINK $CROSS_MIPS big $TESTROOT @g" mips-acsim.condor
    sed -i "s@TESTROOT@${TESTROOT}@g" mips-acsim.condor
    sed -i "s@PREFIX@mips-acsim@g" mips-acsim.condor
    condor_submit mips-acsim.condor

    cp ${SCRIPTROOT}/template.condor powerpc-acsim.condor
    sed -i "s@EXECUTABLE@./acsim_condor.sh@g" powerpc-acsim.condor
    sed -i "s@ARGUMENTS@powerpc $RUN_POWERPC_ACSIM  $POWERPCREV $POWERPCLINK $CROSS_POWERPC big $TESTROOT @g" powerpc-acsim.condor
    sed -i "s@TESTROOT@${TESTROOT}@g" powerpc-acsim.condor
    sed -i "s@PREFIX@powerpc-acsim@g" powerpc-acsim.condor
    condor_submit powerpc-acsim.condor

    ######################
    # Testing ACSIM HLT
    ######################

    if [ $RUN_HLTRACE != "no" ]; then

        # High Level Trace: Clean the older log because they are large (>2Gb)
        rm -rf ${HTMLROOT}/*-hltrace-report*

        acsimhlt_html_table "arm" "sparc" "mips" "powerpc" 

        cp ${SCRIPTROOT}/template.condor arm-acsimhlt.condor
        sed -i "s@EXECUTABLE@./acsimhlt_condor.sh@g" arm-acsimhlt.condor
        sed -i "s@ARGUMENTS@arm $RUN_ARM_ACSIM  $ARMREV $ARMLINK $CROSS_ARM little $TESTROOT@g" arm-acsimhlt.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" arm-acsimhlt.condor
        sed -i "s@PREFIX@arm-acsimhlt@g" arm-acsimhlt.condor
        condor_submit arm-acsimhlt.condor

        cp ${SCRIPTROOT}/template.condor sparc-acsimhlt.condor
        sed -i "s@EXECUTABLE@./acsimhlt_condor.sh@g" sparc-acsimhlt.condor
        sed -i "s@ARGUMENTS@sparc $RUN_SPARC_ACSIM  $SPARCREV $SPARCLINK $CROSS_SPARC big $TESTROOT @g" sparc-acsimhlt.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" sparc-acsimhlt.condor
        sed -i "s@PREFIX@sparc-acsimhlt@g" sparc-acsimhlt.condor
        condor_submit sparc-acsimhlt.condor

        cp ${SCRIPTROOT}/template.condor mips-acsimhlt.condor
        sed -i "s@EXECUTABLE@./acsimhlt_condor.sh@g" mips-acsimhlt.condor
        sed -i "s@ARGUMENTS@mips $RUN_MIPS_ACSIM  $MIPSREV $MIPSLINK $CROSS_MIPS big $TESTROOT @g" mips-acsimhlt.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" mips-acsimhlt.condor
        sed -i "s@PREFIX@mips-acsimhlt@g" mips-acsimhlt.condor
        condor_submit mips-acsimhlt.condor

        cp ${SCRIPTROOT}/template.condor powerpc-acsimhlt.condor
        sed -i "s@EXECUTABLE@./acsimhlt_condor.sh@g" powerpc-acsimhlt.condor
        sed -i "s@ARGUMENTS@powerpc $RUN_POWERPC_ACSIM  $POWERPCREV $POWERPCLINK $CROSS_POWERPC big $TESTROOT @g" powerpc-acsimhlt.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" powerpc-acsimhlt.condor
        sed -i "s@PREFIX@powerpc-acsimhlt@g" powerpc-acsimhlt.condor
        condor_submit powerpc-acsimhlt.condor

    fi

    #########################
    # Testing ACSIM POWERSC
    #########################

    if [ $RUN_POWERSC != "no" ]; then

        powersc_html_table "sparc" "mips"

        cp ${SCRIPTROOT}/template.condor sparc-powersc.condor
        sed -i "s@EXECUTABLE@./powersc_condor.sh@g" sparc-powersc.condor
        sed -i "s@ARGUMENTS@sparc $RUN_SPARC_ACSIM  $SPARCREV $SPARCLINK $CROSS_SPARC big $TESTROOT @g" sparc-powersc.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" sparc-powersc.condor
        sed -i "s@PREFIX@sparc-powersc@g" sparc-powersc.condor
        condor_submit sparc-powersc.condor

        cp ${SCRIPTROOT}/template.condor mips-powersc.condor
        sed -i "s@EXECUTABLE@./powersc_condor.sh@g" mips-powersc.condor
        sed -i "s@ARGUMENTS@mips $RUN_MIPS_ACSIM  $MIPSREV $MIPSLINK $CROSS_MIPS big $TESTROOT @g" mips-powersc.condor
        sed -i "s@TESTROOT@${TESTROOT}@g" mips-powersc.condor
        sed -i "s@PREFIX@mips-powersc@g" mips-powersc.condor
        condor_submit mips-powersc.condor

    fi

    finalize_nightly_tester
    exit 0
fi

#####################################################################
# If is no --condor option, it will run sequentially, don't worry. 
# The code below is the Nightly sequential
####################################################################

if [ "$LOCALSIMULATOR" != "no" ]; then

    acsim_html_table "arm" "sparc" "mips" "powerpc"
    localsim_test "arm"     $RUN_ARM_ACSIM     $ARMREV     $ARMLINK       $CROSS_ARM    "little"   
    localsim_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $SPARCLINK     $CROSS_SPARC  "big"
    localsim_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $MIPSLINK      $CROSS_MIPS   "big"
    localsim_test "powerpc" $RUN_POWERPC_ACSIM $POWERPCREV     $POWERPCLINK   $CROSS_POWERPC    "big"
    finalize_nightly_tester
    exit 0
fi

acsim_html_table "arm" "sparc" "mips" "powerpc"
acsim_test "arm"     $RUN_ARM_ACSIM     $ARMREV     $ARMLINK        $CROSS_ARM "little" 
acsim_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $SPARCLINK      $CROSS_SPARC "big"
acsim_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $MIPSLINK       $CROSS_MIPS "big"
acsim_test "powerpc" $RUN_POWERPC_ACSIM $POWERPCREV     $POWERPCLINK    $CROSS_POWERPC "big"

if [ $RUN_HLTRACE != "no" ]; then

    # High Level Trace: Clean the older log because they are large (>2Gb)
    rm -rf ${HTMLROOT}/*-hltrace-report*

    acsimhlt_html_table "arm" "sparc" "mips" "powerpc"
    acsimhlt_test "arm"     $RUN_ARM_ACSIM     $ARMREV     $ARMLINK        $CROSS_ARM "little" 
    acsimhlt_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $SPARCLINK    $CROSS_SPARC "big"
    acsimhlt_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $MIPSLINK     $CROSS_MIPS "big"
    acsimhlt_test "powerpc" $RUN_POWERPC_ACSIM $POWERPCREV     $POWERPCLINK    $CROSS_POWERPC "big"
fi

if [ $RUN_POWERSC != "no" ]; then
    powersc_html_table "sparc" "mips"
    powersc_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $SPARCLINK    $CROSS_SPARC "big"
    powersc_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $MIPSLINK     $CROSS_MIPS "big"
fi


# FIXME DEPRECATED --------
if [ "$RUN_ARM_ACCSIM" != "no" -o "$RUN_MIPS_ACCSIM" != "no" -o "$RUN_SPARC_ACCSIM" != "no" -o "$RUN_POWERPC_ACCSIM" != "no" ]; then
    accsim_test
fi

if [ "$RUN_ARM_ACASM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_POWERPC_ACASM" != "no" ]; then
    acasm_test
fi

if [ $RUN_ACSTONE != "no" ]; then
    acstone_test
fi
# -------------------------

#########################

# Remove model untested
sed -i "s@__REPLACELINE\(_[a-zA-Z]*\)*@@g" $HTMLLOG

finalize_nightly_tester

exit 0

