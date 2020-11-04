#!/bin/bash

## Init the environment
source config/env.sh

## Build and install the detector plugins.
if [[ ! -d ${DETECTOR_SOURCE_PATH} ]]; then
  git clone https://eicweb.phy.anl.gov/EIC/detectors/${JUGGLER_DETECTOR}.git ${DETECTOR_SOURCE_PATH}
else
  pushd ${DETECTOR_SOURCE_PATH}
  git pull --ff-only
  popd
fi
mkdir -p detector-build
pushd detector-build
echo cmake ${DETECTOR_SOURCE_PATH} -DCMAKE_INSTALL_PREFIX=${DETECTOR_PREFIX} && make -j30 install
cmake ${DETECTOR_SOURCE_PATH} -DCMAKE_INSTALL_PREFIX=${DETECTOR_PREFIX} && make -j30 install
popd
