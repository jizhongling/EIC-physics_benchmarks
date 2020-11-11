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

export JUGGLER_FILE_NAME_TAG="dis"
export JUGGLER_GEN_FILE="${JUGGLER_FILE_NAME_TAG}.hepmc"

export JUGGLER_SIM_FILE="sim_${JUGGLER_FILE_NAME_TAG}.root"
export JUGGLER_REC_FILE="rec_${JUGGLER_FILE_NAME_TAG}.root"

echo "JUGGLER_N_EVENTS = ${JUGGLER_N_EVENTS}"
echo "JUGGLER_DETECTOR = ${JUGGLER_DETECTOR}"


### Build the detector constructors.
git clone https://eicweb.phy.anl.gov/EIC/detectors/${JUGGLER_DETECTOR}.git
git clone https://eicweb.phy.anl.gov/EIC/detectors/accelerator.git
pushd ${JUGGLER_DETECTOR}
ln -s ../accelerator/eic
popd
mkdir ${JUGGLER_DETECTOR}/build
pushd ${JUGGLER_DETECTOR}/build
cmake ../. -DCMAKE_INSTALL_PREFIX=/usr/local && make -j30 install
popd

# generate the input events
# temporary standin until hepmc output from pythia is generated.
root -b -q "dis/scripts/gen_central_electrons.cxx(${JUGGLER_N_EVENTS}, \"${JUGGLER_FILE_NAME_TAG}.hepmc\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running script"
  exit 1
fi

#
pushd ${JUGGLER_DETECTOR}

## run geant4 simulations
npsim --runType batch \
      --part.minimalKineticEnergy 1000*GeV  \
      -v WARNING \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${JUGGLER_DETECTOR}.xml \
      --inputFiles ../${JUGGLER_FILE_NAME_TAG}.hepmc \
      --outputFile  ${JUGGLER_SIM_FILE}
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running script"
  exit 1
fi

# Need to figure out how to pass file name to juggler from the commandline
xenv -x ${JUGGLER_INSTALL_PREFIX}/Juggler.xenv \
  gaudirun.py ../options/tracker_reconstruction.py

if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running juggler"
  exit 1
fi
ls -l
popd

pwd
mkdir -p results/dis

root -b -q "dis/scripts/rec_dis_electrons.cxx(\"${JUGGLER_DETECTOR}/${JUGGLER_REC_FILE}\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running root script"
  exit 1
fi

if [[ "${JUGGLER_N_EVENTS}" -lt "500" ]] ; then 
cp ${JUGGLER_DETECTOR}/${JUGGLER_REC_FILE} results/.
fi

