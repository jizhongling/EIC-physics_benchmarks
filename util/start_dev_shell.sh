#!/bin/bash

OS=`uname -s`

if [ "${OS}" = "Linux" ]; then
  echo "Detected OS: Linux"
  if [ ! -f juggler_latest.sif ]; then
    echo "Need to fetch singularity image"
    wget https://eicweb.phy.anl.gov/eic/juggler/-/jobs/artifacts/master/raw/build/juggler.sif?job=docker:singularity -O juggler_latest.sif
  fi
  echo "Launching dev shell (through singularity)..."
  singularity exec juggler_latest.sif eic-shell
elif [ "${OS}" = "Darwin" ]; then
  echo "Detector OS: MacOS"
  echo "Syncing docker container"
  docker pull sly2j/juggler:latest
  echo "Launching dev shell (through docker)..."
  docker run -v /Users:/Users -w=$PWD -i -t --rm sly2j/juggler:latest eic-shell
else
  echo "ERROR: dev shell not available for this OS (${OS})"
fi
