#!/bin/bash

function print_the_help {
  echo "USAGE: ${0} -j <job> -n <nevents> -e <energy> -a <angle> -t <nametag> -p <particle> "
  echo "  OPTIONS: "
  echo "    -j,--job         Index of job"
  echo "    -n,--nevents     Number of events"
  echo "    -e,--energy      Energy in GeV"
  echo "    -a,--angle       Input angle in degree"
  echo "    -t,--nametag     Name tag"
  echo "    -p,--particle    Particle type"
  echo "                     Allowed types: pi0, pi+, pi-, kaon0, kaon+, kaon-, proton, neutron, e-, e+, mu-, mu+, gamma"
  exit
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    -h|--help)
      shift # past argument
      print_the_help
      ;;
    -j|--job)
      export PROC="$2"
      shift # past argument
      shift # past value
      ;;
    -n|--nevents)
      export JUGGLER_N_EVENTS="$2"
      shift # past argument
      shift # past value
      ;;
    -e|--energy)
      export ENERGY="$2"
      shift # past argument
      shift # past value
      ;;
    -a|--angle)
      ANGLE="$2"
      shift # past argument
      shift # past value
      ;;
    -t|--nametag)
      nametag="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--particle)
      particle="$2"
      shift # past argument
      shift # past value
      ;;
    *) # unknown option
      #POSITIONAL+=("$1") # save it in an array for later
      echo "unknown option $1"
      print_the_help
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

export PYTHONPATH=${EIC_SHELL_PREFIX}/python:${PYTHONPATH}
export DETECTOR_PATH=${EIC_SHELL_PREFIX}/../athena
export JUGGLER_DETECTOR=athena
export JUGGLER_DETECTOR_VERSION=default
export JUGGLER_COMPACT_PATH=${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml

if [[ ! -n "${JUGGLER_N_EVENTS}" ]] ; then
  export JUGGLER_N_EVENTS=1000
fi

if [[ ! -n "${ENERGY}" ]] ; then
  export ENERGY=10
fi

OUTDIR=${SPIN}/data/eic/${nametag}
mkdir -p ${OUTDIR}
SKIP_N_EVENTS=$(( 0 * PROC * JUGGLER_N_EVENTS ))
export GEN_FILE="${OUTDIR}/gen_${ENERGY}GeV_${ANGLE}deg-${PROC}.hepmc"
export JUGGLER_SIM_FILE="${OUTDIR}/sim_${ENERGY}GeV_${ANGLE}deg-${PROC}.root"
export JUGGLER_REC_FILE="${OUTDIR}/rec_${ENERGY}GeV_${ANGLE}deg-${PROC}.edm4hep.root"

echo "Number of events: ${JUGGLER_N_EVENTS}"
echo "Skip number of events: ${SKIP_N_EVENTS}"
echo "Energy list: ${ENERGY}"
echo "NPSim Detector: ${NPSIM_COMPACT_PATH}"
echo "Juggler Detector: ${JUGGLER_COMPACT_PATH}"

# Generate the input events
python scripts/gen_particles.py ${GEN_FILE} -n ${JUGGLER_N_EVENTS}\
    --angmin ${ANGLE} --angmax ${ANGLE} --parray ${ENERGY} --particles="${particle}"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running script: generating input events"
  exit 1
fi

ls -lh ${GEN_FILE}

# Run geant4 simulations
npsim --runType batch \
      -v WARNING \
      --part.minimalKineticEnergy "0.5*GeV" \
      --physics.list "FTFP_BERT_HP" \
      --physics.rangecut "0.01*mm" \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --skipNEvents ${SKIP_N_EVENTS} \
      --compactFile ${JUGGLER_COMPACT_PATH} \
      --inputFiles ${GEN_FILE} \
      --outputFile ${JUGGLER_SIM_FILE}
#-G --gun.particle "${particle}" --gun.energy "${ENERGY}*GeV" --gun.position "-2.5025*cm 2.4747*cm 350.*cm" --gun.direction "0 0.17364817766 0.98480775301" \

if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running npdet"
  exit 1
fi

rootls -t "${JUGGLER_SIM_FILE}"

# Run Juggler
gaudirun.py options/reconstruction.ecal.py
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running juggler"
  exit 1
fi
