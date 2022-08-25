from Gaudi.Configuration import *

from Configurables import ApplicationMgr, AuditorSvc, EICDataSvc, PodioOutput, GeoSvc

from GaudiKernel.SystemOfUnits import eV, MeV, GeV, mm, cm, mrad

import json

detector_path = str(os.environ.get("DETECTOR_PATH", "."))
detector_name = str(os.environ.get("DETECTOR_CONFIG", "epic"))
detector_config = str(os.environ.get("DETECTOR_CONFIG", detector_name))
detector_version = str(os.environ.get("DETECTOR_VERSION", "main"))

# Detector features that affect reconstruction
has_ecal_barrel_scfi = False
if "epic" in detector_name and "imaging" in detector_config:
    has_ecal_barrel_scfi = True

# CAL reconstruction
# get sampling fractions from system environment variable
cb_hcal_sf = float(os.environ.get("CB_HCAL_SAMP_FRAC", 0.038))
ci_hcal_sf = float(os.environ.get("CI_HCAL_SAMP_FRAC", 0.025))
ce_hcal_sf = float(os.environ.get("CE_HCAL_SAMP_FRAC", 0.025))

# input calorimeter DAQ info
calo_daq = {}
with open(
    "{}/calibrations/calo_digi_default.json".format(detector_path)
) as f:
    calo_config = json.load(f)
    ## add proper ADC capacity based on bit depth
    for sys in calo_config:
        cfg = calo_config[sys]
        calo_daq[sys] = {
            "dynamicRangeADC": eval(cfg["dynamicRange"]),
            "capacityADC": 2 ** int(cfg["capacityBitsADC"]),
            "pedestalMean": int(cfg["pedestalMean"]),
            "pedestalSigma": float(cfg["pedestalSigma"]),
        }
print(calo_daq)

# input and output
input_sims = [
    f.strip() for f in str.split(os.environ["JUGGLER_SIM_FILE"], ",") if f.strip()
]
output_rec = str(os.environ["JUGGLER_REC_FILE"])
n_events = int(os.environ["JUGGLER_N_EVENTS"])

# services
services = []
# geometry service
services.append(
    GeoSvc(
        "GeoSvc",
        detectors=["{}/{}.xml".format(detector_path, detector_config)],
        OutputLevel=WARNING,
    )
)
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
    "MCParticles",
    #"HcalBarrelHits",
    #"HcalBarrelHitsContributions",
    "HcalEndcapPHits",
    "HcalEndcapPHitsContributions",
    #"HcalEndcapNHits",
    #"HcalEndcapNHitsContributions",
]

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

# Hcal Hadron Endcap
ci_hcal_daq = calo_daq["hcal_pos_endcap"]

ci_hcal_digi = CalHitDigi(
    "ci_hcal_digi",
    inputHitCollection="HcalEndcapPHits",
    outputHitCollection="HcalEndcapPRawHits",
    **ci_hcal_daq
)
algorithms.append(ci_hcal_digi)

ci_hcal_reco = CalHitReco(
    "ci_hcal_reco",
    inputHitCollection=ci_hcal_digi.outputHitCollection,
    outputHitCollection="HcalEndcapPRecHits",
    thresholdFactor=5.0,
    samplingFraction=ci_hcal_sf,
    **ci_hcal_daq
)
algorithms.append(ci_hcal_reco)

ci_hcal_merger = CalHitsMerger(
    "ci_hcal_merger",
    inputHitCollection=ci_hcal_reco.outputHitCollection,
    outputHitCollection="HcalEndcapPMergedHits",
    readoutClass="HcalEndcapPHits",
    fields=["layer", "slice"],
    fieldRefNumbers=[1, 0],
)
algorithms.append(ci_hcal_merger)

ci_hcal_cl = IslandCluster(
    "ci_hcal_cl",
    inputHitCollection=ci_hcal_merger.outputHitCollection,
    outputProtoClusterCollection="HcalEndcapPProtoClusters",
    splitCluster=False,
    minClusterCenterEdep=30.0 * MeV,
    localDistXY=[15.0 * cm, 15.0 * cm],
)
algorithms.append(ci_hcal_cl)

ci_hcal_clreco = RecoCoG(
    "ci_hcal_clreco",
    inputProtoClusterCollection=ci_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="HcalEndcapPClusters",
    logWeightBase=6.2,
)
algorithms.append(ci_hcal_clreco)

# Hcal Electron Endcap
ce_hcal_daq = calo_daq["hcal_neg_endcap"]

ce_hcal_digi = CalHitDigi(
    "ce_hcal_digi",
    inputHitCollection="HcalEndcapNHits",
    outputHitCollection="HcalEndcapNRawHits",
    **ce_hcal_daq
)
#algorithms.append(ce_hcal_digi)

ce_hcal_reco = CalHitReco(
    "ce_hcal_reco",
    inputHitCollection=ce_hcal_digi.outputHitCollection,
    outputHitCollection="HcalEndcapNRecHits",
    thresholdFactor=5.0,
    samplingFraction=ce_hcal_sf,
    **ce_hcal_daq
)
#algorithms.append(ce_hcal_reco)

ce_hcal_merger = CalHitsMerger(
    "ce_hcal_merger",
    inputHitCollection=ce_hcal_reco.outputHitCollection,
    outputHitCollection="HcalEndcapNMergedHits",
    readoutClass="HcalEndcapNHits",
    fields=["layer", "slice"],
    fieldRefNumbers=[1, 0],
)
#algorithms.append(ce_hcal_merger)

ce_hcal_cl = IslandCluster(
    "ce_hcal_cl",
    inputHitCollection=ce_hcal_merger.outputHitCollection,
    outputProtoClusterCollection="HcalEndcapNProtoClusters",
    splitCluster=False,
    minClusterCenterEdep=30.0 * MeV,
    localDistXY=[15.0 * cm, 15.0 * cm],
)
#algorithms.append(ce_hcal_cl)

ce_hcal_clreco = RecoCoG(
    "ce_hcal_clreco",
    inputProtoClusterCollection=ce_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="HcalEndcapNClusters",
    logWeightBase=6.2,
)
#algorithms.append(ce_hcal_clreco)

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
] + ["drop " + c for c in sim_coll]
algorithms.append(podout)

ApplicationMgr(
    TopAlg=algorithms,
    EvtSel="NONE",
    EvtMax=n_events,
    ExtSvc=services,
    OutputLevel=WARNING,
    AuditAlgorithms=True,
)
