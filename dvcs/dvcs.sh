#!/bin/bash

# these variables might not need exported.
export JUGGLER_FILE_NAME_TAG="dvcs"

export JUGGLER_SIM_FILE="sim_${JUGGLER_FILE_NAME_TAG}.root"
export JUGGLER_REC_FILE="rec_${JUGGLER_FILE_NAME_TAG}.root"

echo "JUGGLER_N_EVENTS      = ${JUGGLER_N_EVENTS}"
echo "JUGGLER_DETECTOR      = ${JUGGLER_DETECTOR}"
echo "JUGGLER_FILE_NAME_TAG = ${JUGGLER_FILE_NAME_TAG}"

## To run the reconstruction, we need the following global variables:
## - JUGGLER_INSTALL_PREFIX: Install prefix for Juggler (simu/recon)
## - JUGGLER_DETECTOR:       the detector package we want to use for this benchmark
## - DETECTOR_PATH:          full path to the detector definitions
##
## You can ready config/env.sh for more in-depth explanations of the variables
## and how they can be controlled.
source config/env.sh


curl -o test_proton_dvcs_eic.hepmc "https://eicweb.phy.anl.gov/api/v4/projects/345/jobs/artifacts/master/raw/data/test_proton_dvcs_eic.hepmc?job=compile"
if [[ "$?" -ne "0" ]] ; then
  echo "Failed to download hepmc file"
  exit 1
fi

## run geant4 simulations
npsim --runType batch \
      --part.minimalKineticEnergy 1000*GeV  \
      -v ERROR \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --inputFiles test_proton_dvcs_eic.hepmc \
      --outputFile  ${JUGGLER_SIM_FILE}
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running npsim"
  exit 1
fi

# Need to figure out how to pass file name to juggler from the commandline
xenv -x ${JUGGLER_INSTALL_PREFIX}/Juggler.xenv \
  gaudirun.py options/tracker_reconstruction.py
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running juggler"
  exit 1
fi

mkdir -p results/dvcs
echo "STAND-IN FOR ANALYSIS SCRIPT"
#root -b -q "dis/scripts/rec_dis_electrons.cxx(\"${JUGGLER_DETECTOR}/${JUGGLER_REC_FILE}\")"
#if [[ "$?" -ne "0" ]] ; then
#  echo "ERROR running root script"
#  exit 1
#fi

# copy data if it is not too big
if [[ "${JUGGLER_N_EVENTS}" -lt "500" ]] ; then 
cp ${JUGGLER_REC_FILE} results/dvcs/.
fi

# Collect the results
cp dvcs/report.xml results/dvcs/.
cp dvcs/report2.xml results/dvcs/.





