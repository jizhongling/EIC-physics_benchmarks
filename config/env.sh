#!/bin/bash

if [[ ! -n  "${JUGGLER_DETECTOR}" ]] ; then 
  export JUGGLER_DETECTOR="topside"
fi

if [[ ! -n  "${JUGGLER_N_EVENTS}" ]] ; then 
  export JUGGLER_N_EVENTS=100
fi

if [[ ! -n  "${JUGGLER_INSTALL_PREFIX}" ]] ; then 
  export JUGGLER_INSTALL_PREFIX="/usr/local"
fi

# not sure this is needed
if [[ ! -n "${DETECTOR_PREFIX}" ]]; then
  # reuse the custom juggler install prefix for detector
  export DETECTOR_INSTALL_PREFIX=${JUGGLER_INSTALL_PREFIX}
fi

## ensure absolute paths
# not sure this is needed either 
export JUGGLER_INSTALL_PREFIX=`realpath ${JUGGLER_INSTALL_PREFIX}`
export DETECTOR_INSTALL_PREFIX=`realpath ${DETECTOR_INSTALL_PREFIX}`

## setup root results artifact path
# this should be in the CI File instead
# https://docs.gitlab.com/ee/ci/yaml/README.html#variables
# export RESULTS_PATH=`realpath results`
