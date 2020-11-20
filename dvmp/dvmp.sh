#!/bin/bash

## =============================================================================
## Run the DVMP benchmarks in 5 steps:
## 1. Build/install detector package
## 2. Detector simulation through npsim
## 3. Digitization and reconstruction through Juggler
## 4. Root-based Physics analyses
## 5. Finalize
## =============================================================================

echo "Running the DVMP benchmarks"

## make sure we launch this script from the project root directory
PROJECT_ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/..
pushd ${PROJECT_ROOT}

## =============================================================================
## Load the environment variables. To build the detector we need the following
## variables:
##
## - JUGGLER_INSTALL_PREFIX: Install prefix for Juggler (simu/recon)
## - JUGGLER_DETECTOR:       the detector package we want to use for this benchmark
## - DETECTOR_PATH:          full path to the detector definitions
##
## You can ready config/env.sh for more in-depth explanations of the variables
## and how they can be controlled.
source config/env.sh

## Extra environment variables for DVMP:
## file tag for these tests
JUGGLER_FILE_NAME_TAG="dvmp"
# Generator file, hardcoded for now FIXME
JUGGLER_GEN_FILE="results/dvmp/jpsi_central_electron-10on100-gen.hepmc"
# FIXME use the input file name, as we will be generating a lot of these
# in the future...
## note: these variables need to be exported to be accessible from
##       the juggler options.py. We should really work on a dedicated
##       juggler launcher to get rid of these "magic" variables. FIXME
export JUGGLER_SIM_FILE="sim_${JUGGLER_FILE_NAME_TAG}.root"
export JUGGLER_REC_FILE="rec_${JUGGLER_FILE_NAME_TAG}.root"


## =============================================================================
## Step 1: Build/install the desired detector package
bash util/build_detector.sh

## =============================================================================
## Step 2: Run the simulation
echo "Running Geant4 simulation"
npsim --runType batch \
      --part.minimalKineticEnergy 1000*GeV  \
      -v WARNING \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --inputFiles ${JUGGLER_GEN_FILE} \
      --outputFile ${JUGGLER_SIM_FILE}
if [ "$?" -ne "0" ] ; then
  echo "ERROR running npsim"
  exit 1
fi

## =============================================================================
## Step 3: Run digitization & reconstruction
echo "Running the digitization and reconstruction"
# FIXME Need to figure out how to pass file name to juggler from the commandline
xenv -x ${JUGGLER_INSTALL_PREFIX}/Juggler.xenv \
  gaudirun.py options/tracker_reconstruction.py
if [ "$?" -ne "0" ] ; then
  echo "ERROR running juggler"
  exit 1
fi
ls -l

## =============================================================================
## Step 4: Analysis
root -b -q "dvmp/analysis/vm_mass.cxx(\
 \"${JUGGLER_REC_FILE}\", \
 \"jpsi\", \
 \"electron\", \
 \"${JUGGLER_DETECTOR}\", \
 \"results/dvmp/plot\")"

if [ "$?" -ne "0" ] ; then
  echo "ERROR running root script"
  exit 1
fi

## =============================================================================
## Step 5: finalize
echo "Finalizing ${JUGGLER_FILE_NAME_TAG} benchmark"

## Copy over reconsturction artifacts as long as we don't have
## too many events
if [ "${JUGGLER_N_EVENTS}" -lt "500" ] ; then 
  cp ${JUGGLER_REC_FILE} results/dvmp/.
fi

## cleanup output files
rm ${JUGGLER_REC_FILE} ${JUGGLER_SIM_FILE}

## =============================================================================
## All done!
echo "${JUGGLER_FILE_NAME_TAG} benchmarks complete"
