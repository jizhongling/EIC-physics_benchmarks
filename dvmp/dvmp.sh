#!/bin/bash

## =============================================================================
## Run the DVMP benchmarks in 7 steps:
## 1. Parse the command line and setup environment
## 2. Build/install detector package
## 3. Detector simulation through npsim
## 4. Digitization and reconstruction through Juggler
## 5. Root-based Physics analyses
## 6. Finalize
## =============================================================================

## make sure we launch this script from the project root directory
PROJECT_ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/..
pushd ${PROJECT_ROOT}

echo "Running the DVMP benchmarks"


## =============================================================================
## Step 1: Setup the environment variables
##
## First parse the command line flags.
## This sets the following environment variables:
## - CONFIG:   The specific generator configuration
## - EBEAM:    The electron beam energy
## - PBEAM:    The ion beam energy
## - DECAY:    The decay particle for the generator
## - LEADING:  Leading particle of interest (J/psi)
export REQUIRE_DECAY=1
export REQUIRE_LEADING=1
source util/parse_cmd.sh $@

## To run the reconstruction, we need the following global variables:
## - JUGGLER_INSTALL_PREFIX: Install prefix for Juggler (simu/recon)
## - JUGGLER_DETECTOR:       the detector package we want to use for this benchmark
## - DETECTOR_PATH:          full path to the detector definitions
##
## You can ready config/env.sh for more in-depth explanations of the variables
## and how they can be controlled.
source config/env.sh

## We also need the following benchmark-specific variables:
##
## - BENCHMARK_TAG: Unique identified for this benchmark process.
## - DATA_PATH:     Place to store our persistent output artifacts.
##
## You can read dvmp/env.sh for more in-depth explanations of the variables.
source dvmp/env.sh

## Get a unique file names based on the configuration options
GEN_FILE=${DATA_PATH}/`util/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type gen`.hepmc
SIM_FILE=${LOCAL_PREFIX}/`util/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type sim`.root
REC_FILE=${LOCAL_PREFIX}/`util/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type rec`.root
PLOT_PREFIX=${DATA_PATH}/`util/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type rec`

## =============================================================================
## Step 1: Build/install the desired detector package
# moved to different CI step TODO remove
#bash util/build_detector.sh

## =============================================================================
## Step 2: Run the simulation
echo "Running Geant4 simulation"
npsim --runType batch \
      --part.minimalKineticEnergy 1000*GeV  \
      -v WARNING \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --inputFiles ${GEN_FILE} \
      --outputFile ${SIM_FILE}
if [ "$?" -ne "0" ] ; then
  echo "ERROR running npsim"
  exit 1
fi

## =============================================================================
## Step 3: Run digitization & reconstruction
echo "Running the digitization and reconstruction"
## FIXME Need to figure out how to pass file name to juggler from the commandline
## the tracker_reconstruction.py options file uses the following environment
## variables:
## - JUGGLER_SIM_FILE:    input detector simulation
## - JUGGLER_REC_FILE:    output reconstructed data
## - JUGGLER_DETECTOR_PATH: Location of the detector geometry
## - JUGGLER_N_EVENTS:    number of events to process (part of global environment)
## - JUGGLER_DETECTOR:    detector package (part of global environment)
export JUGGLER_SIM_FILE=${SIM_FILE}
export JUGGLER_REC_FILE=${REC_FILE}
export JUGGLER_DETECTOR_PATH=${DETECTOR_PATH}
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
 \"${REC_FILE}\", \
 \"${LEADING}\", \
 \"${DECAY}\", \
 \"${JUGGLER_DETECTOR}\", \
 \"${PLOT_PREFIX}\")"


if [ "$?" -ne "0" ] ; then
  echo "ERROR running root script"
  exit 1
fi

## =============================================================================
## Step 5: finalize
echo "Finalizing DVMP benchmark"

## Copy over reconsturction artifacts as long as we don't have
## too many events
if [ "${JUGGLER_N_EVENTS}" -lt "500" ] ; then 
  cp ${REC_FILE} ${DATA_PATH}
fi

## cleanup output files
rm ${REC_FILE} ${SIM_FILE}

## =============================================================================
## All done!
echo "DVMP benchmarks complete"
