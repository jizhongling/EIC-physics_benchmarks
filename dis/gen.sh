#!/bin/bash

## =============================================================================
## Standin for a proper pythia generation process, similar to how we
## generate events for DVMP
## =============================================================================

## TODO: use JUGGLER_FILE_NAME_TAG instead of explicitly refering to dis

echo "Running the DIS benchmarks"

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

## Setup local environment
export DATA_PATH=results/dis

## Extra environment variables for DVMP:
## file tag for these tests
JUGGLER_FILE_NAME_TAG="dis"

## =============================================================================
## Step 1: Dummy event generator
## TODO better file name that encodes the actual configuration we're running
root -b -q "dis/generator/gen_central_electrons.cxx(${JUGGLER_N_EVENTS}, \".local/${JUGGLER_FILE_NAME_TAG}.hepmc\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running script"
  exit 1
fi

## =============================================================================
## Step 2: finalize
echo "Moving event generator output into ${DATA_PATH}"
mv .local/${JUGGLER_FILE_NAME_TAG}.hepmc ${DATA_PATH}/${JUGGLER_FILE_NAME_TAG}.hepmc

## =============================================================================
## All done!
echo "dis event generation complete"
