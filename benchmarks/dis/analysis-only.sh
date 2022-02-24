#!/bin/bash

## =============================================================================
## Run the DIS benchmarks in 5 steps:
## 1. Parse the command line and setup environment
## 2. Detector simulation through ddsim
## 3. Digitization and reconstruction through Juggler
## 4. Root-based Physics analyses
## 5. Finalize
## =============================================================================

## make sure we launch this script from the project root directory
PROJECT_ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/../..
pushd ${PROJECT_ROOT}

echo "Running the DIS benchmarks"

## =============================================================================
## Step 1: Setup the environment variables
##
## First parse the command line flags.
## This sets the following environment variables:
## - CONFIG:   The specific generator configuration
## - EBEAM:    The electron beam energy
## - PBEAM:    The ion beam energy
source parse_cmd.sh $@

## To run the reconstruction, we need the following global variables:
## - JUGGLER_INSTALL_PREFIX: Install prefix for Juggler (simu/recon)
## - JUGGLER_DETECTOR:       the detector package we want to use for this benchmark
## - DETECTOR_PATH:          full path to the detector definitions
##

## We also need the following benchmark-specific variables:
##
## - BENCHMARK_TAG: Unique identified for this benchmark process.
## - BEAM_TAG:      Identifier for the chosen beam configuration
## - INPUT_PATH:    Path for generator-level input to the benchmarks
## - TMP_PATH:      Path for temporary data (not exported as artifacts)
## - RESULTS_PATH:  Path for benchmark output figures and files
##
## You can read dvmp/env.sh for more in-depth explanations of the variables.
source benchmarks/dis/env.sh

## Get a unique file names based on the configuration options
GEN_FILE=${INPUT_PATH}/gen-${CONFIG}_${JUGGLER_N_EVENTS}.hepmc

SIM_FILE=${TMP_PATH}/sim-${CONFIG}.edm4hep.root
SIM_LOG=${TMP_PATH}/sim-${CONFIG}.log


REC_FILE=${TMP_PATH}/rec-${CONFIG}.root
REC_LOG=${TMP_PATH}/sim-${CONFIG}.log

PLOT_TAG=${CONFIG}

## =============================================================================
## Step 2: Run the simulation
echo "Running Geant4 simulation"
#ddsim --runType batch \
#      --part.minimalKineticEnergy 1000*GeV  \
#      --filter.tracker edep0 \
#      -v WARNING \
#      --numberOfEvents ${JUGGLER_N_EVENTS} \
#      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
#      --inputFiles ${GEN_FILE} \
#      --outputFile ${SIM_FILE}
#if [ "$?" -ne "0" ] ; then
#  echo "ERROR running ddsim"
#  exit 1
#fi

## =============================================================================
## Step 3: Run digitization & reconstruction
#echo "Running the digitization and reconstruction"
## FIXME Need to figure out how to pass file name to juggler from the commandline
## the tracker_reconstruction.py options file uses the following environment
## variables:
## - JUGGLER_SIM_FILE:    input detector simulation
## - JUGGLER_REC_FILE:    output reconstructed data
## - JUGGLER_N_EVENTS:    number of events to process (part of global environment)
## - JUGGLER_DETECTOR:    detector package (part of global environment)
#export JUGGLER_SIM_FILE=${SIM_FILE}
#export JUGGLER_REC_FILE=${REC_FILE}
#gaudirun.py options/tracker_reconstruction.py 
## on-error, first retry running juggler again as there is still a random
## crash we need to address FIXME
#if [ "$?" -ne "0" ] ; then
#  echo "Juggler crashed, retrying..."
#  gaudirun.py options/tracker_reconstruction.py \
#    2>&1 > ${REC_LOG}
#  if [ "$?" -ne "0" ] ; then
#    echo "ERROR running juggler, both attempts failed"
#    exit 1
#  fi
#fi

## =============================================================================
## Step 4: Analysis
## write a temporary configuration file for the analysis script
echo "Running analysis"
CONFIG="${TMP_PATH}/${PLOT_TAG}.json"
cat << EOF > ${CONFIG}
{
  "rec_file": "${REC_FILE}",
  "detector": "${JUGGLER_DETECTOR}",
  "output_prefix": "${RESULTS_PATH}/${PLOT_TAG}",
  "test_tag": "${BEAM_TAG}"
}
EOF
#cat ${CONFIG}
root -b -q "benchmarks/dis/analysis/dis_electrons.cxx+(\"${CONFIG}\")"
#root -b -q "benchmarks/dis/analysis/dis_electrons.cxx(\"${CONFIG}\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running rec_dis_electron script"
  exit 1
fi

## =============================================================================
## Step 5: finalize
#echo "Finalizing DIS benchmark"

## Move over reconsturction artifacts as long as we don't have
## too many events
#if [ "${JUGGLER_N_EVENTS}" -lt "500" ] ; then 
#  cp ${REC_FILE} ${RESULTS_PATH}
#fi

## Always move over log files to the results path
#cp ${REC_LOG} ${RESULTS_PATH}

## =============================================================================
## All done!
echo "DIS benchmarks complete"
