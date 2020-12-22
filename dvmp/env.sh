#!/bin/bash

## =============================================================================
## Local configuration variables for this particular benchmark 
## It defines the following additional variables: 
##
##  - BENCHMARK_TAG:          Tag to identify this particular benchmark
##  - BEAM_TAG                Tag to identify the beam configuration
##  - INPUT_PATH:             Path for generator-level input to the benchmarks
##  - TMP_PATH:               Path for temporary data (not exported as artifacts)
##  - RESULTS_PATH:           Path for benchmark output figures and files
##
## This script assumes that EBEAM and PBEAM are set as part of the
## calling script (usually as command line argument).
##
## =============================================================================

## Tag for the local benchmark. Should be the same as the directory name for
## this particular benchmark set (for clarity). 
## This tag is used for the output artifacts directory (results/${JUGGLER_TAG}) 
## and a tag in some of the output files.
export BENCHMARK_TAG="dvmp"
echo "Setting up the local environment for the ${BENCHMARK_TAG^^} benchmarks"

## Extra beam tag to identify the desired beam configuration
export BEAM_TAG="${EBEAM}on${PBEAM}"

## Data path for input data (generator-level hepmc file)
INPUT_PATH="input/${BENCHMARK_TAG}/${BEAM_TAG}"
mkdir -p ${INPUT_PATH}
export INPUT_PATH=`realpath ${INPUT_PATH}`
echo "INPUT_PATH:             ${INPUT_PATH}"


## Data path for temporary data (not exported as artifacts)
TMP_PATH=${LOCAL_PREFIX}/tmp/${BEAM_TAG}
mkdir -p ${TMP_PATH}
export TMP_PATH=`realpath ${TMP_PATH}`
echo "TMP_PATH:               ${TMP_PATH}"

## Data path for benchmark output (plots and reconstructed files
## if not too big).
RESULTS_PATH="results/${BENCHMARK_TAG}/${BEAM_TAG}"
mkdir -p ${RESULTS_PATH}
export RESULTS_PATH=`realpath ${RESULTS_PATH}`
echo "RESULTS_PATH:           ${RESULTS_PATH}"

## =============================================================================
## That's all!
echo "Local environment setup complete."
