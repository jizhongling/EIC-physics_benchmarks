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

detector_version = 'default'
if "JUGGLER_DETECTOR_VERSION" in os.environ:
    env_version = str(os.environ["JUGGLER_DETECTOR_VERSION"])
    if 'acadia' in env_version:
        detector_version = 'acadia'
compact_path = os.path.join(detector_path, detector_name)


# CAL reconstruction
# get sampling fractions from system environment variable
ci_ecal_sf = float(os.environ.get("CI_ECAL_SAMP_FRAC", 0.253))

# input calorimeter DAQ info
calo_daq = {}
with open('{}/calibrations/calo_digi_{}.json'.format(detector_path, detector_version)) as f:
    calo_config = json.load(f)
    ## add proper ADC capacity based on bit depth
    for sys in calo_config:
        cfg = calo_config[sys]
        calo_daq[sys] = {
            'dynamicRangeADC': eval(cfg['dynamicRange']),
            'capacityADC': 2**int(cfg['capacityBitsADC']),
            'pedestalMean': int(cfg['pedestalMean']),
            'pedestalSigma': float(cfg['pedestalSigma'])
        }
print(calo_daq)

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
from Configurables import Jug__Fast__TruthClustering as TruthClustering
#from Configurables import Jug__Fast__ClusterMerger as ClusterMerger

# branches needed from simulation root file
sim_coll = [
    "MCParticles",
    'EcalEndcapNHits',
    'EcalEndcapNHitsContributions',
    'EcalEndcapPHits',
    'EcalEndcapPHitsContributions',
    'EcalBarrelHits',
    'EcalBarrelHitsContributions',
    'EcalBarrelScFiHits',
    'EcalBarrelScFiHitsContributions',
]

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

# Crystal Endcap Ecal
ce_ecal_daq = calo_daq['ecal_neg_endcap']
ce_ecal_digi = CalHitDigi("ce_ecal_digi",
        inputHitCollection="EcalEndcapNHits",
        outputHitCollection="EcalEndcapNRawHits",
        energyResolutions=[0., 0.02, 0.],
        **ce_ecal_daq)
algorithms.append(ce_ecal_digi)

ce_ecal_reco = CalHitReco("ce_ecal_reco",
        inputHitCollection=ce_ecal_digi.outputHitCollection,
        outputHitCollection="EcalEndcapNRecHits",
        thresholdFactor=4,          # 4 sigma cut on pedestal sigma
        samplingFraction=0.998,      # this accounts for a small fraction of leakage
        readoutClass="EcalEndcapNHits",
        sectorField="sector",
        **ce_ecal_daq)
algorithms.append(ce_ecal_reco)

ce_ecal_cl = TruthClustering("ce_ecal_cl",
        inputHits=ce_ecal_reco.outputHitCollection,
        mcHits="EcalEndcapNHits",
        outputProtoClusters="EcalEndcapNProtoClusters")
#ce_ecal_cl = IslandCluster("ce_ecal_cl",
#        inputHitCollection=ce_ecal_reco.outputHitCollection,
#        outputProtoClusterCollection="EcalEndcapNProtoClusters",
#        splitCluster=False,
#        minClusterHitEdep=1.0*units.MeV,  # discard low energy hits
#        minClusterCenterEdep=30*units.MeV,
#        sectorDist=5.0*units.cm,
#        dimScaledLocalDistXY=[1.8, 1.8]) # dimension scaled dist is good for hybrid sectors with different module size
algorithms.append(ce_ecal_cl)

ce_ecal_clreco = RecoCoG("ce_ecal_clreco",
        inputProtoClusterCollection=ce_ecal_cl.outputProtoClusters,
        outputClusterCollection="EcalEndcapNClusters",
        logWeightBase=4.6)
algorithms.append(ce_ecal_clreco)

#ce_ecal_clmerger = ClusterMerger("ce_ecal_clmerger",
#        inputClusters = ce_ecal_clreco.outputClusterCollection,
#        outputClusters = "EcalEndcapNMergedClusters",
#        outputRelations = "EcalEndcapNMergedClusterRelations")
#algorithms.append(ce_ecal_clmerger)

# Endcap ScFi Ecal
ci_ecal_daq = calo_daq['ecal_pos_endcap']

ci_ecal_digi = CalHitDigi("ci_ecal_digi",
        inputHitCollection="EcalEndcapPHits",
        outputHitCollection="EcalEndcapPRawHits",
        scaleResponse=ci_ecal_sf,
        energyResolutions=[.1, .0015, 0.],
        **ci_ecal_daq)
algorithms.append(ci_ecal_digi)

ci_ecal_reco = CalHitReco("ci_ecal_reco",
        inputHitCollection=ci_ecal_digi.outputHitCollection,
        outputHitCollection="EcalEndcapPRecHits",
        thresholdFactor=5.0,
        samplingFraction=ci_ecal_sf,
        **ci_ecal_daq)
algorithms.append(ci_ecal_reco)

# merge hits in different layer (projection to local x-y plane)
ci_ecal_merger = CalHitsMerger("ci_ecal_merger",
        inputHitCollection=ci_ecal_reco.outputHitCollection,
        outputHitCollection="EcalEndcapPRecMergedHits",
        fields=["fiber_x", "fiber_y"],
        fieldRefNumbers=[1, 1],
        # fields=["layer", "slice"],
        # fieldRefNumbers=[1, 0],
        readoutClass="EcalEndcapPHits")
algorithms.append(ci_ecal_merger)

ci_ecal_cl = TruthClustering("ci_ecal_cl",
        inputHits=ci_ecal_reco.outputHitCollection,
        mcHits="EcalEndcapPHits",
        outputProtoClusters="EcalEndcapPProtoClusters")
#ci_ecal_cl = IslandCluster("ci_ecal_cl",
        #inputHitCollection=ci_ecal_merger.outputHitCollection,
        #outputProtoClusterCollection="EcalEndcapPProtoClusters",
        #splitCluster=False,
        #minClusterCenterEdep=10.*units.MeV,
        #localDistXY=[10*units.mm, 10*units.mm])
algorithms.append(ci_ecal_cl)

ci_ecal_clreco = RecoCoG("ci_ecal_clreco",
        inputProtoClusterCollection=ci_ecal_cl.outputProtoClusters,
        outputClusterCollection="EcalEndcapPClusters",
        enableEtaBounds=True,
        logWeightBase=6.2)
algorithms.append(ci_ecal_clreco)

#ci_ecal_clmerger = ClusterMerger("ci_ecal_clmerger",
#        inputClusters = ci_ecal_clreco.outputClusterCollection,
#        outputClusters = "EcalEndcapPMergedClusters",
#        outputRelations = "EcalEndcapPMergedClusterRelations")
#algorithms.append(ci_ecal_clmerger)

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
