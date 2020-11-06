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

if [[ ! -n "${DETECTOR_PREFIX}" ]]; then
  export DETECTOR_PREFIX=detector
fi

## ensure absolute paths
export JUGGLER_INSTALL_PREFIX=`realpath ${JUGGLER_INSTALL_PREFIX}`
export DETECTOR_PREFIX=`realpath ${DETECTOR_PREFIX}`

## setup detector paths
export LD_LIBRARY_PATH=${DETECTOR_PREFIX}/lib:$LD_LIBRARY_PATH
export DETECTOR_SOURCE_PATH=${DETECTOR_PREFIX}/src

## setup root results artifact path
export RESULTS_PATH=`realpath results`
