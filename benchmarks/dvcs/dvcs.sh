#!/bin/bash

function print_the_help {
  echo "USAGE: ${0} [--data-init]  "
  echo "  OPTIONS: "
  exit 
}

DATA_INIT=
REC_ONLY=
ANALYSIS_ONLY=

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    -h|--help)
      shift # past argument
      print_the_help
      ;;
    --data-init)
      DATA_INIT=1
      shift # past value
      ;;
    *)    # unknown option
      #POSITIONAL+=("$1") # save it in an array for later
      echo "unknown option $1"
      print_the_help
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters
# these variables might not need exported.
export FILE_NAME_TAG="dvcs"

export JUGGLER_SIM_FILE="sim_${FILE_NAME_TAG}.root"
export JUGGLER_REC_FILE="rec_${FILE_NAME_TAG}.root"

echo "JUGGLER_N_EVENTS      = ${JUGGLER_N_EVENTS}"
echo "JUGGLER_DETECTOR      = ${JUGGLER_DETECTOR}"
echo "FILE_NAME_TAG = ${FILE_NAME_TAG}"

print_env.sh

## To run the reconstruction, we need the following global variables:
## - JUGGLER_INSTALL_PREFIX: Install prefix for Juggler (simu/recon)
## - JUGGLER_DETECTOR:       the detector package we want to use for this benchmark
## - DETECTOR_PATH:          full path to the detector definitions

if [[ -n "${DATA_INIT}" ]] ; then 
  mc -C . config host add S3 https://dtn01.sdcc.bnl.gov:9000 $S3_ACCESS_KEY $S3_SECRET_KEY
  mc -C . cat  --insecure S3/eictest/ATHENA/EVGEN/DVCS/DVCS_10x100_2M/DVCS.1.hepmc |  head  -n 1004 > "${LOCAL_DATA_PATH}/dvcs_test.hepmc"
  if [[ "$?" -ne "0" ]] ; then
    echo "Failed to download hepmc file"
    exit 1
  fi
  exit
fi


#curl -o test_proton_dvcs_eic.hepmc "https://eicweb.phy.anl.gov/api/v4/projects/345/jobs/artifacts/master/raw/data/test_proton_dvcs_eic.hepmc?job=compile"


## run geant4 simulations
npsim --runType batch \
      --part.minimalKineticEnergy 1000*GeV  \
      -v ERROR \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --inputFiles "${LOCAL_DATA_PATH}/dvcs_test.hepmc" \
      --outputFile  ${JUGGLER_SIM_FILE}
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running npsim"
  exit 1
fi

# Need to figure out how to pass file name to juggler from the commandline
xenv -x ${JUGGLER_INSTALL_PREFIX}/Juggler.xenv \
  gaudirun.py options/reconstruction.py
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running juggler"
  exit 1
fi

mkdir -p results/dvcs
rootls -t ${JUGGLER_SIM_FILE}

root -b -q "benchmarks/dvcs/scripts/dvcs_tests.cxx(\"${JUGGLER_REC_FILE}\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running root script"
  exit 1
fi

# copy data if it is not too big
if [[ "${JUGGLER_N_EVENTS}" -lt "500" ]] ; then 
cp ${JUGGLER_REC_FILE} results/dvcs/.
fi





