#!/bin/bash

## =============================================================================
## Local configuration variables for this particular benchmark 
## It defines the following additional variables: 
##
##  - BENCHMARK_TAG:          Tag to identify this particular benchmark
##  - DATA_PATH:              Data path for all artifact output
##
## =============================================================================

## Tag for the local benchmark. Should be the same as the directory name for
## this particular benchmark set (for clarity). 
## This tag is used for the output artifacts directory (results/${JUGGLER_TAG}) 
## and a tag in some of the output files.
export BENCHMARK_TAG="dvmp"
echo "Setting up the local environment for the ${BENCHMARK_TAG^^} benchmarks"

## Data path for all artifact output
export DATA_PATH="results/${BENCHMARK_TAG}"
mkdir -p ${DATA_PATH}
echo "DATA_PATH:              ${DATA_PATH}"

## =============================================================================
## That's all!
echo "Local environment setup complete."
