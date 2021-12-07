#!/bin/bash

function print_the_help {
  echo "USAGE: ${0} -n <nevents> -e <energy> -t <nametag> -p <particle> "
  echo "  OPTIONS: "
  echo "    -n,--nevents     Number of events"
  echo "    -e,--energy      Energy"
  echo "    -t,--nametag     Name tag"
  echo "    -p,--particle    Particle type"
  echo "                     Allowed types: pion0, pion+, pion-, kaon0, kaon+, kaon-, proton, neutron, electron, positron, photon"
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
    -n|--nevents)
      export JUGGLER_N_EVENTS="$2"
      shift # past argument
      shift # past value
      ;;
    -e|--energy)
      #energies=(0.1 0.2 0.5 1 2 5 10 20 40 60)
      #export ENERGY="${energies[$2]}"
      export ENERGY="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      #POSITIONAL+=("$1") # save it in an array for later
      echo "unknown option $1"
      print_the_help
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

#export PYTHONPATH=${ATHENA_PREFIX}/python:${PYTHONPATH}
export DETECTOR_PATH=${ATHENA_PREFIX}/../athena
export JUGGLER_DETECTOR=athena
export JUGGLER_COMPACT_PATH=${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml

if [[ ! -n  "${JUGGLER_N_EVENTS}" ]] ; then
  export JUGGLER_N_EVENTS=1000
fi

if [[ ! -n  "${ENERGY}" ]] ; then
  export ENERGY=10
fi

mkdir -p ${nametag}_FTFP
export GEN_FILE="${nametag}_FTFP/${nametag}_${ENERGY}GeV.hepmc"
export JUGGLER_SIM_FILE="${nametag}_FTFP/sim_${nametag}_${ENERGY}GeV.root"
export JUGGLER_REC_FILE="${nametag}_FTFP/rec_${nametag}_${ENERGY}GeV.root"
export OUT_FILE="${nametag}_${ENERGY}GeV_FTFP.pdf"

echo "Number of events: ${JUGGLER_N_EVENTS}"
echo "Energy list: ${ENERGY}"
echo "Detector path: ${JUGGLER_COMPACT_PATH}"

# Generate the input events
#python scripts/gen_particles.py ${GEN_FILE} -n ${JUGGLER_N_EVENTS}\
#    --angmin 20 --angmax 20 --parray ${ENERGY} --particles="${particle}"
#if [[ "$?" -ne "0" ]] ; then
#  echo "ERROR running script: generating input events"
#  exit 1
#fi

ls -lh ${GEN_FILE}

# Run geant4 simulations
npsim --runType batch \
      -v WARNING \
      --part.minimalKineticEnergy "0.5*MeV" \
      --physics.list "FTFP_BERT_HP" \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${JUGGLER_COMPACT_PATH} \
      --inputFiles ${GEN_FILE} \
      --outputFile ${JUGGLER_SIM_FILE}
#-G --gun.particle "${particle}" --gun.energy "${ENERGY}*GeV" --gun.position "2.5025*cm 2.4747*cm -8.5*cm" --gun.direction "0 0.3420201433 0.9396926208" \

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

# Directory for plots
mkdir -p results

# Plot clusters first
python scripts/plot_reco_endcap.py ${JUGGLER_REC_FILE} ${OUT_FILE} -o results
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running analysis script: plot_reco_endcap.py"
  exit 1
fi
