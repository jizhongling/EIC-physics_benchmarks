from Gaudi.Configuration import *

from Configurables import ApplicationMgr, AuditorSvc, EICDataSvc, PodioOutput, GeoSvc
from GaudiKernel import SystemOfUnits as units
from GaudiKernel.SystemOfUnits import MeV, GeV, mm, cm, mrad

import json

detector_name = "athena"
if "JUGGLER_DETECTOR" in os.environ :
  detector_name = str(os.environ["JUGGLER_DETECTOR"])

detector_path = ""
if "DETECTOR_PATH" in os.environ :
  detector_path = str(os.environ["DETECTOR_PATH"])

compact_path = os.path.join(detector_path, detector_name)

# CAL reconstruction
# get sampling fractions from system environment variable
cb_hcal_sf = float(os.environ.get("CB_HCAL_SAMP_FRAC", 0.038))
ci_hcal_sf = float(os.environ.get("CI_HCAL_SAMP_FRAC", 0.025))
ce_hcal_sf = float(os.environ.get("CE_HCAL_SAMP_FRAC", 0.025))

# input and output
input_sims = [f.strip() for f in str.split(os.environ["JUGGLER_SIM_FILE"], ",") if f.strip()]
output_rec = str(os.environ["JUGGLER_REC_FILE"])
n_events = int(os.environ["JUGGLER_N_EVENTS"])

# services
services = []
# geometry service
services.append(GeoSvc("GeoSvc", detectors=["{}.xml".format(compact_path)], OutputLevel=WARNING))
# data service
services.append(EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING))

# juggler components
from Configurables import PodioInput
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Reco__CalorimeterHitReco as CalHitReco
from Configurables import Jug__Reco__CalorimeterHitsMerger as CalHitsMerger
from Configurables import Jug__Reco__CalorimeterIslandCluster as IslandCluster
from Configurables import Jug__Reco__ClusterRecoCoG as RecoCoG

# branches needed from simulation root file
sim_coll = [
    "mcparticles",
    "HcalEndcapPHits",
    "HcalEndcapNHits",
]

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

# Hcal Hadron Endcap
ci_hcal_daq = dict(
         dynamicRangeADC=50.*units.MeV,
         capacityADC=32768,
         pedestalMean=400,
         pedestalSigma=10)

ci_hcal_digi = CalHitDigi("ci_hcal_digi",
         inputHitCollection="HcalEndcapPHits",
         outputHitCollection="HcalEndcapPRawHits",
         **ci_hcal_daq)
algorithms.append(ci_hcal_digi)

ci_hcal_reco = CalHitReco("ci_hcal_reco",
        inputHitCollection=ci_hcal_digi.outputHitCollection,
        outputHitCollection="HcalEndcapPRecHits",
        thresholdFactor=5.0,
        **ci_hcal_daq)
algorithms.append(ci_hcal_reco)

ci_hcal_merger = CalHitsMerger("ci_hcal_merger",
        inputHitCollection=ci_hcal_reco.outputHitCollection,
        outputHitCollection="HcalEndcapPMergedHits",
        readoutClass="HcalEndcapPHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(ci_hcal_merger)

ci_hcal_cl = IslandCluster("ci_hcal_cl",
        inputHitCollection=ci_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalEndcapPProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*units.MeV,
        localDistXY=[15.*units.cm, 15.*units.cm])
algorithms.append(ci_hcal_cl)

ci_hcal_clreco = RecoCoG("ci_hcal_clreco",
        inputHitCollection=ci_hcal_cl.inputHitCollection,
        inputProtoClusterCollection=ci_hcal_cl.outputProtoClusterCollection,
        outputClusterCollection="HcalEndcapPClusters",
        mcHits="HcalEndcapPHits",
        logWeightBase=6.2,
        samplingFraction=ci_hcal_sf)
algorithms.append(ci_hcal_clreco)

# Hcal Electron Endcap
ce_hcal_daq = dict(
        dynamicRangeADC=50.*units.MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

ce_hcal_digi = CalHitDigi("ce_hcal_digi",
        inputHitCollection="HcalEndcapNHits",
        outputHitCollection="HcalEndcapNRawHits",
        **ce_hcal_daq)
algorithms.append(ce_hcal_digi)

ce_hcal_reco = CalHitReco("ce_hcal_reco",
        inputHitCollection=ce_hcal_digi.outputHitCollection,
        outputHitCollection="HcalEndcapNRecHits",
        thresholdFactor=5.0,
        **ce_hcal_daq)
algorithms.append(ce_hcal_reco)

ce_hcal_merger = CalHitsMerger("ce_hcal_merger",
        inputHitCollection=ce_hcal_reco.outputHitCollection,
        outputHitCollection="HcalEndcapNMergedHits",
        readoutClass="HcalEndcapNHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(ce_hcal_merger)

ce_hcal_cl = IslandCluster("ce_hcal_cl",
        inputHitCollection=ce_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalEndcapNProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*units.MeV,
        localDistXY=[15.*units.cm, 15.*units.cm])
algorithms.append(ce_hcal_cl)

ce_hcal_clreco = RecoCoG("ce_hcal_clreco",
        inputHitCollection=ce_hcal_cl.inputHitCollection,
        inputProtoClusterCollection=ce_hcal_cl.outputProtoClusterCollection,
        outputClusterCollection="HcalEndcapNClusters",
        mcHits="HcalEndcapNHits",
        logWeightBase=6.2,
        samplingFraction=ce_hcal_sf)
algorithms.append(ce_hcal_clreco)

# Output
podout = PodioOutput("out", filename=output_rec)
podout.outputCommands = [
        "keep *",
        "drop *Hits",
        "keep *RecHits",
        "keep *Layers",
        "keep *Clusters",
        "drop *ProtoClusters",
        "drop outputParticles",
        "drop InitTrackParams",
        ] + [ "drop " + c for c in sim_coll]
algorithms.append(podout)

ApplicationMgr(
    TopAlg = algorithms,
    EvtSel = 'NONE',
    EvtMax = n_events,
    ExtSvc = services,
    OutputLevel = WARNING,
    AuditAlgorithms = True
 )
