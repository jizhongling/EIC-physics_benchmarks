#!/bin/bash

## Init the environment
source config/env.sh

## Build and install the detector plugins.
if [[ ! -d ${JUGGLER_DETECTOR} ]]; then
  git clone https://eicweb.phy.anl.gov/EIC/detectors/${JUGGLER_DETECTOR}.git
  # this might be temporary. There are multiple solutions here but this is the simple pattern for now
  # I do not want to use git submodules here -whit
  git clone https://eicweb.phy.anl.gov/EIC/detectors/accelerator.git
  pushd ${JUGGLER_DETECTOR}
  ln -s ../accelerator/eic
  popd
else
  pushd ${JUGGLER_DETECTOR}
  git pull --ff-only
  popd
  pushd accelerator
  git pull --ff-only
  popd
fi
mkdir -p detector-build
pushd detector-build
# Always keep the detector directory at the top level.
echo cmake ../${JUGGLER_DETECTOR} -DCMAKE_INSTALL_PREFIX=${DETECTOR_INSTALL_PREFIX} && make -j30 install
cmake ../${JUGGLER_DETECTOR} -DCMAKE_INSTALL_PREFIX=${DETECTOR_INSTALL_PREFIX} && make -j30 install
popd
