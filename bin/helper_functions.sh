#!/bin/bash

# NightlyTester script for ArchC.
# Clone ArchC source in GIT and tests current version
#
# ArchC Team

# Parameters adjustable by environment variables

usage(){
		echo -ne "\nusage: ./nightlytester.sh configfile.conf [options]\n"
        echo -ne "\n    Options:"
        echo -ne "\n        -f      : optional flags to make the Nightly Tester run even if no changes in GIT repositories."
        echo -ne "\n        --condor: make changes in execution flow to adapt to Condor schedule"
        echo -ne "\n\n"
}

command_line_handler() {
    if [ $# -eq 0 ]; then
        usage
        exit
    fi
    case "$1" in
        -h)
            usage
            exit
            ;;
        *)
            if ! [ -f "$1" ]; then
               echo -ne "\nConfiguration file not found. Must run with a valid configuration file.\n\n"
               exit 1
            fi
            CONFIGFILE=$1
           ;;
    esac
    shift 1
    while [ $# -gt 0 ]; do
        case $1 in
            -f)
                FORCENIGHTLY="yes";
                shift 
                ;;
            --condor)
                CONDOR="yes";
                shift 
                ;;
            *)
                if ! [ -z "$2" ]; then
                    echo -ne "\nOption unrecognized: $2\n\n"
                    exit
                fi
                ;;
        esac
    done
    . $CONFIGFILE

    # Configuring ACSIM param
    if [ "$COLLECT_STATS" != "no" ]; then
      ACSIM_PARAMS="${ACSIM_PARAMS} --stats"
    fi
}



# ********************************
# * Trap control                **
# ********************************

cleanup()
{
    echo -ne "Cleaning ${TESTROOT}\n"
    rm -rf ${TESTROOT}  &> /dev/null

    rm -rf /tmp/nightly-token
}


control_c()
{
  echo -en "\n***Exiting ***\n"
  cleanup
  exit $?
}
 
# trap keyboard interrupt (control-c)
trap control_c SIGINT

# *************************************
# * Extracted sources path constants **
# *************************************

# Functions

is_spec2006_enabled(){
    if  [ $BZIP_2 == "no" ] &&
        [ $GCC == "no" ] &&
        [ $MCF == "no" ] &&
        [ $GOBMK == "no" ] &&
        [ $HMMER == "no" ] &&      
        [ $SJENG == "no" ] &&
        [ $LIBQUANTUM == "no" ] &&
        [ $H264 == "no" ] &&        
        [ $OMNETPP == "no" ] &&
        [ $ASTAR == "no" ]; then
        return 1;
    else
        return 0;
    fi
}

is_acsim_enabled() {
    if [ "$RUN_ARM_ACSIM" != "no" ] ||
       [ "$RUN_MIPS_ACSIM" != "no" ] ||
       [ "$RUN_SPARC_ACSIM" != "no" ] ||
       [ "$RUN_POWERPC_ACSIM" != "no" ]; then
       return 0;
    else
       return 1;
    fi
}

is_accsim_enabled() {
    if [ "$RUN_ARM_ACCSIM" != "no" -o   \
         "$RUN_MIPS_ACCSIM" != "no" -o  \
         "$RUN_SPARC_ACCSIM" != "no" -o \
         "$RUN_POWERPC_ACCSIM" != "no" ]; then
        return 0;
    else
        return 1;
    fi
}

have_workingcopy() {
    if [ -z "$ARCHCWORKINGCOPY" ] &&
       [ -z "$ARMWORKINGCOPY" ] &&
       [ -z "$SPARCWORKINGCOPY" ] &&
       [ -z "$POWERPCWORKINGCOPY" ] &&
       [ -z "$MIPSWORKINGCOPY" ]; then
       return 1;
   else
       return 0;
   fi
}


finalize_startup(){
    mv ${LOGTMP}/* ${LOGROOT}/
}

finalize_nightly_tester() {
  TEMPFL=${RANDOM}.out

  DATE_TMP=`LANG=en_US date '+%a %D %T'`
  sed -n -e  "s@Produced by NightlyTester.*@Produced by NightlyTester \@ $DATE_TMP <\/p>@;p" < ${HTMLINDEX} > TMPFILE
  mv TMPFILE ${HTMLINDEX}
  rm -f TMPFILE


  if [ "$FORCENIGHTLY" == "yes" -o "$LASTEQCURRENT" == "no" ]; then
      HTMLLINE="<tr><td>${HTMLPREFIX}</td><td>${DATE}</td><td>${ARCHCREV}</td><td><a href=\"${HTMLPREFIX}-index.htm\">Here</a></td><td>${REVMESSAGE}</td><td>${HOSTNAME}</td></tr>"
      sed -e "/<tr><td>${LASTHTMLPREFIX}/i${HTMLLINE}" $HTMLINDEX > $TEMPFL
      mv ${TEMPFL} $HTMLINDEX
  fi

  # Copy the HTML generates by Jobs to HTMLLOG final.
  # Use the $LOGROOT in all code, degrades the Network bandwidth 
  cp -r ${LOGTMP}/* ${LOGROOT}  &> /dev/null

  if [ "$DELETEWHENDONE" != "no" ]; then
    rm -rf $TESTROOT
  else
    echo -ne "${TESTROOT} folder with all the tests won't be deleted because \$DELETEWHENDONE is set to \"no\".\n"
  fi

  rm -f /tmp/nightly-token

}

do_abort() {
  echo -ne "Aborting...\n\n"
  finalize_nightly_tester
  exit 1
}

#
# Below some useful HTML formating functions from validation.sh
#

# Param1 is the HTML file name
# Param2 is the "title" string
initialize_html() {
	echo -ne "<html> <head> <title> ${2} </title> </head> <body>" > $1
	echo -ne "<h1>${2}</h1>" >> $1
}

# Param1 is the HTML file name
# Param2 is an string containing extra tag terminations (e.g. "</table>")
finalize_html() {
	echo -ne "${2}</body>" >> ${1}
}

# Param1 is the input raw text to format
# Param2 is the HTML file name
format_html_output() {
	echo -ne "<table><tr><td><font face=\"Courier\">" >>$2
	sed -e 'a\<br\>' -e 's/ /\&nbsp;/g' -e 's/error/\<b\>\<font color=\"crimson\"\>error\<\/font\>\<\/b\>/' -e 's/warning/\<b\>\<font color=\"fuchsia\"\>warning\<\/font\>\<\/b\>/' <$1 1>>$2 2>/dev/null
	echo -ne "</font></td></tr></table>"  >>$2
}

# This function is used to get source model, in GIT repository or local Working Copy
clone_or_copy_model(){
  MODELNAME=$1
  GITLINK=$2
  MODELWORKINGCOPY=$3

  mkdir -p ${TESTROOT}/${MODELNAME}/base
  if [ -z "$GITLINK" ]; then
    echo -ne "Copying $MODELNAME source from a local directory...\n"
    cp -a ${MODELWORKINGCOPY} ${TESTROOT}/${MODELNAME}/modelbase &> /dev/null
    [ $? -ne 0 ] && {
      echo -ne "<p><b><font color=\"crimson\">${MODELNAME} source copy failed. Check script parameters.</font></b></p>\n" >> $HTMLLOG
      finalize_html $HTMLLOG ""
      echo -ne "Local directory copy \e[31mfailed\e[m. Check script parameters.\n"
      do_abort
    }
    cd ${TESTROOT}/${MODELNAME}/base
    MODELREV="N/A"
    cd - &> /dev/null
  else
    echo -ne "Cloning ${MODELNAME} ArchC Model GIT...\n"
    TEMPFL=${RANDOM}.out
    #svn co ${SVNLINK} ${TESTROOT}/${MODELNAME} > $TEMPFL 3>&2
    git clone ${GITLINK} ${TESTROOT}/${MODELNAME}/base > $TEMPFL 2>&1
    [ $? -ne 0 ] && {
      rm $TEMPFL
      echo -ne "<p><b><font color=\"crimson\">${MODELNAME} model git clone failed. Check script parameters.</font></b></p>\n" >> $HTMLLOG
      finalize_html $HTMLLOG ""
      echo -ne "git clone \e[31mfailed\e[m. Check script parameters.\n"
      do_abort
    } 
    # Extract model revision number
    cd ${TESTROOT}/${MODELNAME}/base
    #MODELREV=$(git log | head -n1 | cut -c8-13)"..."$(git log | head -n1 | cut -c42-)
    MODELREV=$(git log | head -n1 | cut -c8-15)".."
    if [ "$LASTHTMLPREFIX" != "0" ]; then
        LASTMODELREV=`grep -e "<td>$MODELNAME" < ${LOGROOT}/${LASTHTMLPREFIX}-index.htm | head -n 1 | cut -d\> -f 7 | cut -d\< -f 1`
        if [ "$MODELREV" != "$LASTMODELREV" ]; then
            LASTEQCURRENT="no"
        fi
    else
        LASTEQCURRENT="no"
    fi
    cd - &> /dev/null
    rm $TEMPFL
  fi
}

create_test_env() {
    local MODEL=$1
    local RUN_MODEL=$2
    CROSS_MODEL=$3
    local HTMLLOG=$4

    cd ${TESTROOT}/acsim
    if [ "$RUN_MODEL" != "no" ]; then   
        echo -ne "\nUncompressing Mibench from source to ${MODEL} cross compiling...\n"
        cp ${SCRIPTROOT}/sources/SourceMibench.tar.bz2 .
        tar -xjf SourceMibench.tar.bz2
        [ $? -ne 0 ] && do_abort
        mv SourceMibench ${MODEL}_mibench
        if is_spec2006_enabled; then
            echo -ne "Uncompressing SPEC2006 from source to ${MODEL} cross compiling...\n"
            cp ${SCRIPTROOT}/sources/SourceSPEC2006.tar.bz2 .
            tar -xjf SourceSPEC2006.tar.bz2
            [ $? -ne 0 ] && do_abort
            mv SourceSPEC2006 ${MODEL}_spec
        fi

        echo -ne "Copying Cross ${MODEL} source...\n"
        mkdir ${TESTROOT}/cross &> /dev/null
        cd ${TESTROOT}/cross
        if [[ $CROSS_MODEL == *"http"* ]]; then
            wget ${CROSS_MODEL} &> /dev/null
        else
            cp ${CROSS_MODEL} . &> /dev/null
        fi
        TARFILE=$(basename $CROSS_MODEL)
        tar -xf ${TARFILE}
        RETCODE=$?
        CROSS_ROOT=${TESTROOT}/cross/$(tar -tf ${TARFILE} | head -n1)
        export CROSS_MODEL=$CROSS_ROOT/bin
        chmod 777 $CROSS_ROOT -R 
        if [ $RETCODE -ne 0 ]; then
            sed -i "s@__STATUS_CROSS_${MODEL}__@<b><font color=\"crimson\">Failed </font></b>@g"  ${HTMLLOG}
            do_abort
        else
            sed -i "s@__STATUS_CROSS_${MODEL}__@<b><font color=\"green\">OK </font></b>@g" ${HTMLLOG}
        fi
    fi
}


