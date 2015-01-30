#!/bin/bash

# NightlyTester script for ArchC.
# Clone ArchC source in GIT and tests current version
#
# ArchC Team

# Parameters adjustable by environment variables

NIGHTLYVERSION=2.1

####################################
### Import external funtions
####################################
. bin/helper_functions.sh
. bin/acsim.sh
. bin/powersc.sh
. bin/localsim.sh

#####################################
### Functions
#####################################
create_test_env() {
    MODEL=$1
    RUN_MODEL=$2
    if [ "$RUN_MODEL" != "no" ]; then   
        if [ "$COMPILE" != "no" ]; then
            echo -ne "Uncompressing Mibench from source to ${MODEL} cross compiling...\n"
            tar -xjf ${SCRIPTROOT}/sources/SourceMibench.tar.bz2
            [ $? -ne 0 ] && do_abort
            mv SourceMibench ${MODEL}_mibench
            if is_spec2006_enabled; then
                echo -ne "Uncompressing SPEC2006 from source to ${MODEL} cross compiling...\n"
                tar -xjf ${SCRIPTROOT}/sources/SourceSPEC2006.tar.bz2
                [ $? -ne 0 ] && do_abort
                mv SourceSPEC2006 ${MODEL}_spec
            fi
        else
            echo -ne "Precompiled unavailable: use the cross-compilers from ArchC.org and set COMPILER=yes in .config file\n"
            do_abort
#            echo -ne "Uncompressing Mibench precompiled for ${MODEL}...\n"
#            tar -xjf ${SCRIPTROOT}/sources/ARMMibench.tar.bz2
#            [ $? -ne 0 ] && do_abort
#    
#            #FIXME: Make precompiled for SPEC2006
#            if is_spec2006_enabled; then
#            echo -ne "SPEC precompiled unavailable\n"
#            do_abort
        fi
    fi
}


####################################
### ENTRY POINT
####################################

# Check if other instance of Nightly is running (LOCK file)
if [ -a /tmp/nightly-token ]; then
    echo -ne "A instance of Nightly is running...\n"
    exit 0
else
    touch /tmp/nightly-token
fi

# Initializing HTML log files
# Discover this run's number and prefix all our HTML files with it

if [ ! -f $HTMLINDEX ]; then
    mkdir $LOGROOT &> /dev/null
    cp htmllogs/index.htm $HTMLINDEX
fi
export HTMLPREFIX=`sed -n -e '/<tr><td>[0-9]\+/{s/<tr><td>\([0-9]\+\).*/\1/;p;q}' <${HTMLINDEX}`
export LASTHTMLPREFIX=$HTMLPREFIX
export LASTARCHCREV=`grep -e "<tr><td>" < ${HTMLINDEX} | head -n 1 | cut -d\> -f 7 | cut -d\< -f 1`

if [ -z $LASTARCHCREV ]; then
    echo -ne "Problem in index.html file.\n"
    do_abort
fi

export LASTEQCURRENT="yes"

HTMLPREFIX=$(($HTMLPREFIX + 1))
HTMLLOG=${LOGROOT}/${HTMLPREFIX}-index.htm

initialize_html $HTMLLOG "NightlyTester ${NIGHTLYVERSION} Run #${HTMLPREFIX}"
export DATE=`LANG=en_US date '+%a %D %T'`
echo -ne "<p>Produced by NightlyTester @ ${DATE}</p>"   >> $HTMLLOG
echo -ne "<p><table border=\"1\" cellspacing=\"1\" cellpadding=\"5\">" >> $HTMLLOG
echo -ne "<tr><th>Component</th><th>Link/Path</th><th>Version</th><th>Compilation</th></tr>\n" >> $HTMLLOG

######################################
### Clone, configure & install ArchC
######################################
mkdir ${TESTROOT}
mkdir ${TESTROOT}/acsrc
mkdir ${TESTROOT}/install

ARCHCLINK="${ARCHCGITLINK}${ARCHCWORKINGCOPY}"
echo -ne "<tr><td>ArchC</td><td>${ARCHCLINK}</td>" >> $HTMLLOG

cd ${TESTROOT}/acsrc
if [ -z "$ARCHCGITLINK" ]; then
  echo -ne "Copying ArchC source from a local directory...\n"
  cp -a ${ARCHCWORKINGCOPY} ./ &> /dev/null
  make distclean &> /dev/null
  [ $? -ne 0 ] && {
    echo -ne "<td><font color=\"crimson\"> Copy Failed </font></td><td> - </td></tr>\n" >> $HTMLLOG
    echo -ne "</table></p>\n" >> $HTMLLOG
    finalize_html $HTMLLOG ""
    echo -ne "Local directory copy \e[31mfailed\e[m. Check script parameters.\n"
    do_abort
  }
  ARCHCREV="N/A"
else
  echo -ne "Cloning ArchC GIT version...\n"
  git clone $ARCHCGITLINK . > /dev/null 2>&1  
  [ $? -ne 0 ] && {
    echo -ne "<td><font color=\"crimson\"> Clone Failed </font></td><td> - </td></tr>\n" >> $HTMLLOG
    echo -ne "</table></p>\n" >> $HTMLLOG
    finalize_html $HTMLLOG ""
    echo -ne "GIT clone \e[31mfailed\e[m. Check script parameters.\n"
    do_abort
  } 
  # Extract revision number
  cd ${TESTROOT}/acsrc &> /dev/null
  #ARCHCREV=$(git log | head -n1 | cut -c8-13)"..."$(git log | head -n1 | cut -c42-)
  ARCHCREV=$(git log | head -n1 | cut -c8-15)".."
  if [ ${ARCHCREV} != ${LASTARCHCREV} ]; then
        LASTEQCURRENT="no"
  fi
  cd - &> /dev/null
fi

echo -ne "<td> ${ARCHCREV} </td>" >> $HTMLLOG
echo -ne "Building/Installing ArchC...\n"
TEMPFL=${RANDOM}.out

# ./configure
ACSIM_STRING=""
ACASM_STRING=""
ACSTONE_STRING=""
POWERSC_STRING=""
./boot.sh > $TEMPFL 2>&1
if is_acsim_enabled || is_accsim_enabled; then
    ACSIM_STRING="--with-systemc=${SYSTEMCPATH}"
fi
if [ "$RUN_ARM_ACASM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_POWERPC_ACASM" != "no" ]; then
    ACASM_STRING="--with-binutils=${BINUTILSPATH}"
fi
if [ "$RUN_ACSTONE" != "no" ]; then
    ACSTONE_STRING=" --with-gdb=${GDBPATH}"
fi
./configure --prefix=${TESTROOT}/install $ACSIM_STRING $ACASM_STRING $ACSTONE_STRING >> $TEMPFL 2>&1    

# Compile ArchC
make >> $TEMPFL 2>&1 &&
make install >> $TEMPFL 2>&1
RETCODE=$?
HTMLBUILDLOG=${LOGROOT}/${HTMLPREFIX}-archc-build-log.htm
initialize_html $HTMLBUILDLOG "ArchC rev $ARCHCREV build output"
format_html_output $TEMPFL $HTMLBUILDLOG
finalize_html $HTMLBUILDLOG ""
rm $TEMPFL
if [ $RETCODE -ne 0 ]; then
  echo -ne "<td> <font color=\"crimson\">Failed </font> (<a href=\"${HTMLPREFIX}-archc-build-log.htm\">log</a>) </td> </tr>" >> $HTMLLOG
  echo -ne "</table></p>\n" >> $HTMLLOG
  finalize_html $HTMLLOG ""
  echo -ne "ArchC build \e[31mfailed\e[m.\n"
  do_abort
else
  echo -ne "<td> <font color=\"green\">OK </font> (<a href=\"${HTMLPREFIX}-archc-build-log.htm\">log</a>) </td> </tr>" >> $HTMLLOG
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

################
### SystemC
################
echo -ne "<tr><td>SystemC</td><td>${SYSTEMCPATH}</td>" >> $HTMLLOG
if [ "$SYSTEMCCOMPILE" != "yes" ]; then
  echo -ne "<td>-</td><td>-</td></tr>\n" >> $HTMLLOG
fi

echo -ne "</table></p>\n" >> $HTMLLOG

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
  PPCREV=${MODELREV}
fi

########################################################
### Execute or Abort?
########################################################

if  [ "$FORCENIGHTLY" != "yes" ] &&       # If -f args; then Execute;
    ! have_workingcopy &&            # If WorkingCopy links; then Execute;
    [ "$LASTEQCURRENT" == "yes" ]; then  # If last execution have GIT Revisions equal the current, Abort
        echo -ne "All Revisions tested in last execution\n"
        rm ${LOGROOT}/${HTMLPREFIX}-* 
        do_abort
fi

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

############################

ARMLINK="${ARMGITLINK}${ARMWORKINGCOPY}"
SPARCLINK="${SPARCGITLINK}${SPARCWORKINGCOPY}"
MIPSLINK="${MIPSGITLINK}${MIPSWORKINGCOPY}"
POWERPCLINK="${POWERPCGITLINK}${POWERPCWORKINGCOPY}"


create_test_env "arm"     $RUN_ARM_ACSIM
create_test_env "sparc"   $RUN_SPARC_ACSIM
create_test_env "mips"    $RUN_MIPS_ACSIM
create_test_env "powerpc" $RUN_POWERPC_ACSIM

if [ "$LOCALSIMULATOR" != "no" ]; then

    localsim_prologue
    localsim_test "arm"     $RUN_ARM_ACSIM     $ARMREV     $CROSS_ARM "little"
    localsim_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $CROSS_SPARC "big"
    localsim_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $CROSS_MIPS "big"
    localsim_test "powerpc" $RUN_POWERPC_ACSIM $PPCREV     $CROSS_POWERPC "big"
    localsim_epilogue

    finalize_nightly_tester
    exit 0
fi

acsim_prologue
acsim_test "arm"     $RUN_ARM_ACSIM     $ARMREV     $ARMLINK        $CROSS_ARM "little"
acsim_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $SPARCLINK      $CROSS_SPARC "big"
acsim_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $MIPSLINK       $CROSS_MIPS "big"
acsim_test "powerpc" $RUN_POWERPC_ACSIM $PPCREV     $POWERPCLINK    $CROSS_POWERPC "big"
acsim_epilogue

if [ $RUN_POWERSC != "no" ]; then
    powersc_prologue
    powersc_test "sparc"   $RUN_SPARC_ACSIM   $SPARCREV   $CROSS_SPARC "big"
    powersc_test "mips"    $RUN_MIPS_ACSIM    $MIPSREV    $CROSS_MIPS "big"
    powersc_epilogue
fi

# FIXME DEPRECATED
if [ "$RUN_ARM_ACCSIM" != "no" -o "$RUN_MIPS_ACCSIM" != "no" -o "$RUN_SPARC_ACCSIM" != "no" -o "$RUN_POWERPC_ACCSIM" != "no" ]; then
    accsim_test
fi

if [ "$RUN_ARM_ACASM" != "no" -o "$RUN_MIPS_ACASM" != "no" -o "$RUN_SPARC_ACASM" != "no" -o "$RUN_POWERPC_ACASM" != "no" ]; then
    acasm_test
fi

if [ $RUN_ACSTONE != "no" ]; then
    acstone_test
fi
# FIXME ----------- 


#########################

finalize_nightly_tester

exit 0

