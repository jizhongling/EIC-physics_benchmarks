from Gaudi.Configuration import *

from Configurables import ApplicationMgr, AuditorSvc, EICDataSvc, PodioOutput, GeoSvc
from Configurables import Gaudi__Monitoring__MessageSvcSink as MessageSvcSink
from Configurables import Gaudi__Histograming__Sink__Root as RootHistoSink
from GaudiKernel import SystemOfUnits as units
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

if "PBEAM" in os.environ:
    ionBeamEnergy = str(os.environ["PBEAM"])
else:
    ionBeamEnergy = 100

# ZDC reconstruction calibrations
try:
    ffi_zdc_calibrations = "calibrations/ffi_zdc.json"
    with open(os.path.join(detector_path, ffi_zdc_calibrations)) as f:
        ffi_zdc_config = json.load(f)

        def ffi_zdc_cal_parse(ffi_zdc_cal):
            ffi_zdc_cal_sf = float(ffi_zdc_cal["sampling_fraction"])
            ffi_zdc_cal_cl_kwargs = {
                "minClusterCenterEdep": eval(ffi_zdc_cal["minClusterCenterEdep"]),
                "minClusterHitEdep": eval(ffi_zdc_cal["minClusterHitEdep"]),
                "localDistXY": [
                    eval(ffi_zdc_cal["localDistXY"][0]),
                    eval(ffi_zdc_cal["localDistXY"][1]),
                ],
                "splitCluster": bool(ffi_zdc_cal["splitCluster"]),
            }
            return ffi_zdc_cal_sf, ffi_zdc_cal_cl_kwargs

        ffi_zdc_ecal_sf, ffi_zdc_ecal_cl_kwargs = ffi_zdc_cal_parse(
            ffi_zdc_config["ffi_zdc_ecal"]
        )
        ffi_zdc_hcal_sf, ffi_zdc_hcal_cl_kwargs = ffi_zdc_cal_parse(
            ffi_zdc_config["ffi_zdc_hcal"]
        )
except (IOError, OSError):
    print(f"Using default ffi_zdc calibrations; {ffi_zdc_calibrations} not found.")
    ffi_zdc_ecal_sf = float(os.environ.get("FFI_ZDC_ECAL_SAMP_FRAC", 1.0))
    ffi_zdc_hcal_sf = float(os.environ.get("FFI_ZDC_HCAL_SAMP_FRAC", 1.0))

# RICH reconstruction
qe_data = [
    (1.0, 0.25),
    (7.5, 0.25),
]

# CAL reconstruction
# get sampling fractions from system environment variable
ci_ecal_sf = float(os.environ.get("CI_ECAL_SAMP_FRAC", 0.03))
cb_hcal_sf = float(os.environ.get("CB_HCAL_SAMP_FRAC", 0.038))
ci_hcal_sf = float(os.environ.get("CI_HCAL_SAMP_FRAC", 0.025))
ce_hcal_sf = float(os.environ.get("CE_HCAL_SAMP_FRAC", 0.025))

# input arguments from calibration file
with open(f"{detector_path}/calibrations/emcal_barrel_calibration.json") as f:
    calib_data = json.load(f)["electron"]

print(calib_data)

# input calorimeter DAQ info
calo_daq = {}
with open(f"{detector_path}/calibrations/calo_digi_default.json") as f:
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

img_barrel_sf = float(calib_data["sampling_fraction_img"])
scifi_barrel_sf = float(calib_data["sampling_fraction_scfi"])

# input and output
input_sims = [
    f.strip() for f in str.split(os.environ["JUGGLER_SIM_FILE"], ",") if f.strip()
]
output_rec = str(os.environ["JUGGLER_REC_FILE"])
n_events = int(os.environ["JUGGLER_N_EVENTS"])

# services
services = []
# auditor service
services.append(AuditorSvc("AuditorSvc", Auditors=["ChronoAuditor", "MemStatAuditor"]))
# geometry service
## note: old version of material map is called material-maps.XXX, new version is materials-map.XXX
##       these names are somewhat inconsistent, and should probably all be renamed to 'material-map.XXX'
##       FIXME
services.append(
    GeoSvc(
        "GeoSvc",
        detectors=["{}/{}.xml".format(detector_path, detector_config)],
        materials="calibrations/materials-map.cbor",
        OutputLevel=WARNING,
    )
)
# data service
services.append(EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING))

# message service
MessageSvc().OutputLevel = INFO
services.append(MessageSvcSink())

# ROOT histogram service
RootHistSvc("RootHistSvc").OutputFile = "histo.root"
services.append(RootHistoSink())

# juggler components
from Configurables import PodioInput

from Configurables import Jug__Fast__MC2SmearedParticle as MC2DummyParticle
from Configurables import Jug__Fast__ParticlesWithTruthPID as ParticlesWithTruthPID
from Configurables import Jug__Fast__SmearedFarForwardParticles as FFSmearedParticles

from Configurables import Jug__Fast__MatchClusters as MatchClusters
from Configurables import Jug__Fast__ClusterMerger as ClusterMerger
from Configurables import (
    Jug__Fast__TruthEnergyPositionClusterMerger as EnergyPositionClusterMerger,
)
from Configurables import (
    Jug__Fast__InclusiveKinematicsTruth as InclusiveKinematicsTruth,
)
from Configurables import Jug__Fast__TruthClustering as TruthClustering

from Configurables import Jug__Digi__SimTrackerHitsCollector as SimTrackerHitsCollector
from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

from Configurables import Jug__Reco__FarForwardParticles as FarForwardParticles

from Configurables import (
    Jug__Reco__TrackerHitReconstruction as TrackerHitReconstruction,
)
from Configurables import Jug__Reco__TrackingHitsCollector2 as TrackingHitsCollector
from Configurables import Jug__Reco__TrackerSourceLinker as TrackerSourceLinker

from Configurables import Jug__Reco__TrackParamTruthInit as TrackParamTruthInit
from Configurables import Jug__Reco__TrackParamClusterInit as TrackParamClusterInit
from Configurables import (
    Jug__Reco__TrackParamVertexClusterInit as TrackParamVertexClusterInit,
)
from Configurables import Jug__Reco__CKFTracking as CKFTracking
from Configurables import Jug__Reco__ParticlesFromTrackFit as ParticlesFromTrackFit

# from Configurables import Jug__Reco__TrajectoryFromTrackFit as TrajectoryFromTrackFit
from Configurables import (
    Jug__Reco__InclusiveKinematicsElectron as InclusiveKinematicsElectron,
)
from Configurables import Jug__Reco__InclusiveKinematicsDA as InclusiveKinematicsDA
from Configurables import Jug__Reco__InclusiveKinematicsJB as InclusiveKinematicsJB
from Configurables import (
    Jug__Reco__InclusiveKinematicsSigma as InclusiveKinematicsSigma,
)
from Configurables import (
    Jug__Reco__InclusiveKinematicseSigma as InclusiveKinematicseSigma,
)

from Configurables import Jug__Reco__FarForwardParticles as FFRecoRP
from Configurables import Jug__Reco__FarForwardParticlesOMD as FFRecoOMD

from Configurables import Jug__Reco__CalorimeterHitReco as CalHitReco
from Configurables import Jug__Reco__CalorimeterHitsMerger as CalHitsMerger
from Configurables import Jug__Reco__CalorimeterIslandCluster as IslandCluster

from Configurables import Jug__Reco__ImagingPixelReco as ImCalPixelReco
from Configurables import Jug__Reco__ImagingTopoCluster as ImagingCluster

from Configurables import Jug__Reco__ClusterRecoCoG as RecoCoG
from Configurables import Jug__Reco__ImagingClusterReco as ImagingClusterReco

from Configurables import Jug__Reco__PhotoMultiplierReco as PhotoMultiplierReco
from Configurables import Jug__Reco__PhotoRingClusters as PhotoRingClusters

from Configurables import Jug__Reco__ParticleCollector as ParticleCollector

# branches needed from simulation root file
sim_coll = [
    "MCParticles",
    "B0TrackerHits",
    "EcalEndcapNHits",
    "EcalEndcapNHitsContributions",
    "EcalEndcapPHits",
    "EcalEndcapPHitsContributions",
    "EcalBarrelHits",
    "EcalBarrelHitsContributions",
    "HcalBarrelHits",
    "HcalBarrelHitsContributions",
    "HcalEndcapPHits",
    "HcalEndcapPHitsContributions",
    "HcalEndcapNHits",
    "HcalEndcapNHitsContributions",
    "DRICHHits",
    "ZDCEcalHits",
    "ZDCEcalHitsContributions",
    "ZDCHcalHits",
    "ZDCHcalHitsContributions",
]
ecal_barrel_scfi_collections = [
    "EcalBarrelScFiHits",
    "EcalBarrelScFiHitsContributions",
]
if has_ecal_barrel_scfi:
    sim_coll += ecal_barrel_scfi_collections

forward_romanpot_collections = [
    "ForwardRomanPotHits1",
    "ForwardRomanPotHits2",
]
forward_offmtracker_collections = [
    "ForwardOffMTrackerHits1",
    "ForwardOffMTrackerHits2",
    "ForwardOffMTrackerHits3",
    "ForwardOffMTrackerHits4",
]
sim_coll += forward_romanpot_collections + forward_offmtracker_collections

tracker_endcap_collections = [
    "InnerTrackerEndcapPHits",
    "InnerTrackerEndcapNHits",
    "MiddleTrackerEndcapPHits",
    "MiddleTrackerEndcapNHits",
    "OuterTrackerEndcapPHits",
    "OuterTrackerEndcapNHits",
]
tracker_barrel_collections = [
    "SagittaSiBarrelHits",
    "OuterSiBarrelHits",
]
vertex_barrel_collections = [
    "VertexBarrelHits",
]
mpgd_barrel_collections = [
    "InnerMPGDBarrelHits",
    "OuterMPGDBarrelHits",
]
sim_coll += (
    tracker_endcap_collections
    + tracker_barrel_collections
    + vertex_barrel_collections
    + mpgd_barrel_collections
)

sim_coll.append("MRICHHits")

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

# Generated particles
dummy = MC2DummyParticle(
    "dummy",
    inputParticles="MCParticles",
    outputParticles="GeneratedParticles",
    smearing=0,
)
algorithms.append(dummy)

# Truth level kinematics
truth_incl_kin = InclusiveKinematicsTruth(
    "truth_incl_kin",
    inputMCParticles="MCParticles",
    outputInclusiveKinematics="InclusiveKinematicsTruth",
)
algorithms.append(truth_incl_kin)

## Roman pots
ffi_romanpot_coll = SimTrackerHitsCollector(
    "ffi_romanpot_coll",
    inputSimTrackerHits=forward_romanpot_collections,
    outputSimTrackerHits="ForwardRomanPotAllHits",
)
algorithms.append(ffi_romanpot_coll)
ffi_romanpot_digi = TrackerDigi(
    "ffi_romanpot_digi",
    inputHitCollection=ffi_romanpot_coll.outputSimTrackerHits,
    outputHitCollection="ForwardRomanPotRawHits",
    timeResolution=8,
)
algorithms.append(ffi_romanpot_digi)

ffi_romanpot_reco = TrackerHitReconstruction(
    "ffi_romanpot_reco",
    inputHitCollection=ffi_romanpot_digi.outputHitCollection,
    outputHitCollection="ForwardRomanPotRecHits",
)
algorithms.append(ffi_romanpot_reco)

ffi_romanpot_parts = FarForwardParticles(
    "ffi_romanpot_parts",
    inputCollection=ffi_romanpot_reco.outputHitCollection,
    outputCollection="ForwardRomanPotParticles",
)
algorithms.append(ffi_romanpot_parts)

## Off momentum tracker
ffi_offmtracker_coll = SimTrackerHitsCollector(
    "ffi_offmtracker_coll",
    inputSimTrackerHits=forward_offmtracker_collections,
    outputSimTrackerHits="ForwardOffMTrackerAllHits",
)
algorithms.append(ffi_offmtracker_coll)
ffi_offmtracker_digi = TrackerDigi(
    "ffi_offmtracker_digi",
    inputHitCollection=ffi_offmtracker_coll.outputSimTrackerHits,
    outputHitCollection="ForwardOffMTrackerRawHits",
    timeResolution=8,
)
algorithms.append(ffi_offmtracker_digi)

ffi_offmtracker_reco = TrackerHitReconstruction(
    "ffi_offmtracker_reco",
    inputHitCollection=ffi_offmtracker_digi.outputHitCollection,
    outputHitCollection="ForwardOffMTrackerRecHits",
)
algorithms.append(ffi_offmtracker_reco)

ffi_offmtracker_parts = FarForwardParticles(
    "ffi_offmtracker_parts",
    inputCollection=ffi_offmtracker_reco.outputHitCollection,
    outputCollection="ForwardOffMTrackerParticles",
)
algorithms.append(ffi_offmtracker_parts)

## B0 tracker
trk_b0_digi = TrackerDigi(
    "trk_b0_digi",
    inputHitCollection="B0TrackerHits",
    outputHitCollection="B0TrackerRawHits",
    timeResolution=8,
)
algorithms.append(trk_b0_digi)

trk_b0_reco = TrackerHitReconstruction(
    "trk_b0_reco",
    inputHitCollection=trk_b0_digi.outputHitCollection,
    outputHitCollection="B0TrackerRecHits",
)
algorithms.append(trk_b0_reco)

# ZDC ECAL WSciFi
ffi_zdc_ecal_digi = CalHitDigi(
    "ffi_zdc_ecal_digi",
    inputHitCollection="ZDCEcalHits",
    outputHitCollection="ZDCEcalRawHits",
)
algorithms.append(ffi_zdc_ecal_digi)

ffi_zdc_ecal_reco = CalHitReco(
    "ffi_zdc_ecal_reco",
    inputHitCollection=ffi_zdc_ecal_digi.outputHitCollection,
    outputHitCollection="ZDCEcalRecHits",
    readoutClass="ZDCEcalHits",
    localDetFields=["system"],
)
algorithms.append(ffi_zdc_ecal_reco)

ffi_zdc_ecal_cl = IslandCluster(
    "ffi_zdc_ecal_cl",
    inputHitCollection=ffi_zdc_ecal_reco.outputHitCollection,
    outputProtoClusterCollection="ZDCEcalProtoClusters",
    **ffi_zdc_ecal_cl_kwargs,
)
algorithms.append(ffi_zdc_ecal_cl)

ffi_zdc_ecal_clreco = RecoCoG(
    "ffi_zdc_ecal_clreco",
    mcHits=ffi_zdc_ecal_digi.inputHitCollection,
    inputProtoClusterCollection=ffi_zdc_ecal_cl.outputProtoClusterCollection,
    outputClusterCollection="ZDCEcalClusters",
    outputAssociations="ZDCEcalClusterAssociations",
    logWeightBase=3.6,
    samplingFraction=ffi_zdc_ecal_sf,
)
algorithms.append(ffi_zdc_ecal_clreco)

# ZDC HCAL PbSciFi
ffi_zdc_hcal_digi = CalHitDigi(
    "ffi_zdc_hcal_digi",
    inputHitCollection="ZDCHcalHits",
    outputHitCollection="ZDCHcalRawHits",
)
algorithms.append(ffi_zdc_hcal_digi)

ffi_zdc_hcal_reco = CalHitReco(
    "ffi_zdc_hcal_reco",
    inputHitCollection=ffi_zdc_hcal_digi.outputHitCollection,
    outputHitCollection="ZDCHcalRecHits",
    readoutClass="ZDCHcalHits",
    localDetFields=["system"],
)
algorithms.append(ffi_zdc_hcal_reco)

ffi_zdc_hcal_cl = IslandCluster(
    "ffi_zdc_hcal_cl",
    inputHitCollection=ffi_zdc_hcal_reco.outputHitCollection,
    outputProtoClusterCollection="ZDCHcalProtoClusters",
    **ffi_zdc_hcal_cl_kwargs,
)
algorithms.append(ffi_zdc_hcal_cl)

ffi_zdc_hcal_clreco = RecoCoG(
    "ffi_zdc_hcal_clreco",
    mcHits=ffi_zdc_hcal_digi.inputHitCollection,
    inputProtoClusterCollection=ffi_zdc_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="ZDCHcalClusters",
    outputAssociations="ZDCHcalClusterAssociations",
    logWeightBase=3.6,
    samplingFraction=ffi_zdc_hcal_sf,
)
algorithms.append(ffi_zdc_hcal_clreco)

# Crystal Endcap Ecal
ce_ecal_daq = calo_daq["ecal_neg_endcap"]
ce_ecal_digi = CalHitDigi(
    "ce_ecal_digi",
    inputHitCollection="EcalEndcapNHits",
    outputHitCollection="EcalEndcapNRawHits",
    energyResolutions=[0.0, 0.02, 0.0],
    **ce_ecal_daq,
)
algorithms.append(ce_ecal_digi)

ce_ecal_reco = CalHitReco(
    "ce_ecal_reco",
    inputHitCollection=ce_ecal_digi.outputHitCollection,
    outputHitCollection="EcalEndcapNRecHits",
    thresholdFactor=4,  # 4 sigma cut on pedestal sigma
    samplingFraction=0.998,  # this accounts for a small fraction of leakage
    readoutClass="EcalEndcapNHits",
    sectorField="sector",
    **ce_ecal_daq,
)
algorithms.append(ce_ecal_reco)

ce_ecal_cl = TruthClustering(
    "ce_ecal_cl",
    mcHits="EcalEndcapNHits",
    inputHits=ce_ecal_reco.outputHitCollection,
    outputProtoClusters="EcalEndcapNTruthProtoClusters",
)
algorithms.append(ce_ecal_cl)

ce_ecal_cl_island = IslandCluster(
    "ce_ecal_cl_island",
    inputHitCollection=ce_ecal_reco.outputHitCollection,
    outputProtoClusterCollection="EcalEndcapNIslandProtoClusters",
    splitCluster=False,
    minClusterHitEdep=1.0 * MeV,  # discard low energy hits
    minClusterCenterEdep=30 * MeV,
    sectorDist=5.0 * cm,
    dimScaledLocalDistXY=[1.8, 1.8],
)  # dimension scaled dist is good for hybrid sectors with different module size
algorithms.append(ce_ecal_cl_island)

ce_ecal_clreco = RecoCoG(
    "ce_ecal_clreco",
    mcHits="EcalEndcapNHits",  # to create truth associations
    inputProtoClusterCollection=ce_ecal_cl.outputProtoClusters,
    outputClusterCollection="EcalEndcapNClusters",
    outputAssociations="EcalEndcapNClustersAssoc",
    logWeightBase=4.6,
)
algorithms.append(ce_ecal_clreco)

ce_ecal_clmerger = ClusterMerger(
    "ce_ecal_clmerger",
    inputClusters=ce_ecal_clreco.outputClusterCollection,
    inputAssociations=ce_ecal_clreco.outputAssociations,
    outputClusters="EcalEndcapNMergedClusters",
    outputAssociations="EcalEndcapNMergedClustersAssoc",
)
algorithms.append(ce_ecal_clmerger)

# Endcap ScFi Ecal
ci_ecal_daq = calo_daq["ecal_pos_endcap"]

ci_ecal_digi = CalHitDigi(
    "ci_ecal_digi",
    inputHitCollection="EcalEndcapPHits",
    outputHitCollection="EcalEndcapPRawHits",
    scaleResponse=ci_ecal_sf,
    energyResolutions=[0.1, 0.0015, 0.0],
    **ci_ecal_daq,
)
algorithms.append(ci_ecal_digi)

ci_ecal_reco = CalHitReco(
    "ci_ecal_reco",
    inputHitCollection=ci_ecal_digi.outputHitCollection,
    outputHitCollection="EcalEndcapPRecHits",
    thresholdFactor=5.0,
    samplingFraction=ci_ecal_sf,
    **ci_ecal_daq,
)
algorithms.append(ci_ecal_reco)

# merge hits in different layer (projection to local x-y plane)
ci_ecal_merger = CalHitsMerger(
    "ci_ecal_merger",
    inputHitCollection=ci_ecal_reco.outputHitCollection,
    outputHitCollection="EcalEndcapPRecMergedHits",
    fields=["fiber_x", "fiber_y"],
    fieldRefNumbers=[1, 1],
    # fields = ["layer", "slice"],
    # fieldRefNumbers = [1, 0],
    readoutClass="EcalEndcapPHits",
)
algorithms.append(ci_ecal_merger)

ci_ecal_cl = TruthClustering(
    "ci_ecal_cl",
    mcHits="EcalEndcapPHits",
    inputHits=ci_ecal_reco.outputHitCollection,
    outputProtoClusters="EcalEndcapPTruthProtoClusters",
)
algorithms.append(ci_ecal_cl)

ci_ecal_cl_island = IslandCluster(
    "ci_ecal_cl_island",
    inputHitCollection=ci_ecal_merger.outputHitCollection,
    outputProtoClusterCollection="EcalEndcapPIslandProtoClusters",
    splitCluster=False,
    minClusterCenterEdep=10.0 * MeV,
    localDistXY=[10 * mm, 10 * mm],
)
algorithms.append(ci_ecal_cl_island)

ci_ecal_clreco = RecoCoG(
    "ci_ecal_clreco",
    mcHits=ci_ecal_cl.mcHits,
    inputProtoClusterCollection=ci_ecal_cl.outputProtoClusters,
    outputClusterCollection="EcalEndcapPClusters",
    outputAssociations="EcalEndcapPClustersAssoc",
    enableEtaBounds=True,
    logWeightBase=6.2,
)
algorithms.append(ci_ecal_clreco)

ci_ecal_clmerger = ClusterMerger(
    "ci_ecal_clmerger",
    inputClusters=ci_ecal_clreco.outputClusterCollection,
    inputAssociations=ci_ecal_clreco.outputAssociations,
    outputClusters="EcalEndcapPMergedClusters",
    outputAssociations="EcalEndcapPMergedClustersAssoc",
)
algorithms.append(ci_ecal_clmerger)

# Central Barrel Ecal
if has_ecal_barrel_scfi:
    # Central ECAL Imaging Calorimeter
    img_barrel_daq = calo_daq["ecal_barrel_imaging"]

    img_barrel_digi = CalHitDigi(
        "img_barrel_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelImagingRawHits",
        energyResolutions=[0.0, 0.02, 0.0],  # 2% flat resolution
        **img_barrel_daq,
    )
    algorithms.append(img_barrel_digi)

    img_barrel_reco = ImCalPixelReco(
        "img_barrel_reco",
        inputHitCollection=img_barrel_digi.outputHitCollection,
        outputHitCollection="EcalBarrelImagingRecHits",
        thresholdFactor=3,  # about 20 keV
        samplingFraction=img_barrel_sf,
        readoutClass="EcalBarrelHits",  # readout class
        layerField="layer",  # field to get layer id
        sectorField="module",  # field to get sector id
        **img_barrel_daq,
    )
    algorithms.append(img_barrel_reco)

    img_barrel_cl = ImagingCluster(
        "img_barrel_cl",
        inputHitCollection=img_barrel_reco.outputHitCollection,
        outputProtoClusterCollection="EcalBarrelImagingProtoClusters",
        localDistXY=[2.0 * mm, 2 * mm],  # same layer
        layerDistEtaPhi=[10 * mrad, 10 * mrad],  # adjacent layer
        neighbourLayersRange=2,  # id diff for adjacent layer
        sectorDist=3.0 * cm,
    )  # different sector
    algorithms.append(img_barrel_cl)

    img_barrel_clreco = ImagingClusterReco(
        "img_barrel_clreco",
        mcHits=img_barrel_digi.inputHitCollection,
        inputProtoClusters=img_barrel_cl.outputProtoClusterCollection,
        outputLayers="EcalBarrelImagingLayers",
        outputClusters="EcalBarrelImagingClusters",
        outputAssociations="EcalBarrelImagingClusterAssociations",
    )
    algorithms.append(img_barrel_clreco)

    # Central ECAL SciFi
    scfi_barrel_daq = calo_daq["ecal_barrel_scfi"]

    scfi_barrel_digi = CalHitDigi(
        "scfi_barrel_digi",
        inputHitCollection="EcalBarrelScFiHits",
        outputHitCollection="EcalBarrelScFiRawHits",
        **scfi_barrel_daq,
    )
    algorithms.append(scfi_barrel_digi)

    scfi_barrel_reco = CalHitReco(
        "scfi_barrel_reco",
        inputHitCollection=scfi_barrel_digi.outputHitCollection,
        outputHitCollection="EcalBarrelScFiRecHits",
        thresholdFactor=5.0,
        samplingFraction=scifi_barrel_sf,
        readoutClass="EcalBarrelScFiHits",
        layerField="layer",
        sectorField="module",
        localDetFields=[
            "system",
            "module",
        ],  # use local coordinates in each module (stave)
        **scfi_barrel_daq,
    )
    algorithms.append(scfi_barrel_reco)

    # merge hits in different layer (projection to local x-y plane)
    scfi_barrel_merger = CalHitsMerger(
        "scfi_barrel_merger",
        inputHitCollection=scfi_barrel_reco.outputHitCollection,
        outputHitCollection="EcalBarrelScFiMergedHits",
        fields=["fiber"],
        fieldRefNumbers=[1],
        readoutClass="EcalBarrelScFiHits",
    )
    algorithms.append(scfi_barrel_merger)

    scfi_barrel_cl = IslandCluster(
        "scfi_barrel_cl",
        inputHitCollection=scfi_barrel_merger.outputHitCollection,
        outputProtoClusterCollection="EcalBarrelScFiProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=10.0 * MeV,
        localDistXZ=[30 * mm, 30 * mm],
    )
    algorithms.append(scfi_barrel_cl)

    scfi_barrel_clreco = RecoCoG(
        "scfi_barrel_clreco",
        mcHits=scfi_barrel_digi.inputHitCollection,
        inputProtoClusterCollection=scfi_barrel_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalBarrelScFiClusters",
        outputAssociations="EcalBarrelScFiClustersAssoc",
        logWeightBase=6.2,
    )
    algorithms.append(scfi_barrel_clreco)

    ## barrel cluster merger
    barrel_clus_merger = EnergyPositionClusterMerger(
        "barrel_clus_merger",
        inputMCParticles="MCParticles",
        inputEnergyClusters=scfi_barrel_clreco.outputClusterCollection,
        inputEnergyAssociations=scfi_barrel_clreco.outputAssociations,
        inputPositionClusters=img_barrel_clreco.outputClusters,
        inputPositionAssociations=img_barrel_clreco.outputAssociations,
        outputClusters="EcalBarrelMergedClusters",
        outputAssociations="EcalBarrelMergedClustersAssoc",
    )
    algorithms.append(barrel_clus_merger)

else:
    # SciGlass calorimeter
    sciglass_ecal_daq = dict(
        dynamicRangeADC=5.0 * GeV, capacityADC=32768, pedestalMean=400, pedestalSigma=3
    )

    sciglass_ecal_digi = CalHitDigi(
        "sciglass_ecal_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelHitsDigi",
        energyResolutions=[0.0, 0.02, 0.0],  # 2% flat resolution
        **sciglass_ecal_daq,
    )
    algorithms.append(sciglass_ecal_digi)

    sciglass_ecal_reco = CalHitReco(
        "sciglass_ecal_reco",
        inputHitCollection=sciglass_ecal_digi.outputHitCollection,
        outputHitCollection="EcalBarrelHitsReco",
        thresholdFactor=3,  # about 20 keV
        readoutClass="EcalBarrelHits",  # readout class
        sectorField="sector",  # field to get sector id
        samplingFraction=0.998,  # this accounts for a small fraction of leakage
        **sciglass_ecal_daq,
    )
    algorithms.append(sciglass_ecal_reco)

    sciglass_ecal_cl = TruthClustering(
        "sciglass_ecal_cl",
        mcHits="EcalBarrelHits",
        inputHits=sciglass_ecal_reco.outputHitCollection,
        outputProtoClusters="EcalBarrelTruthProtoClusters",
    )
    algorithms.append(sciglass_ecal_cl)

    sciglass_ecal_cl_island = IslandCluster(
        "sciglass_ecal_cl_island",
        inputHitCollection=sciglass_ecal_reco.outputHitCollection,
        outputProtoClusterCollection="EcalBarrelIslandProtoClusters",
        splitCluster=False,
        minClusterHitEdep=1.0 * MeV,  # discard low energy hits
        minClusterCenterEdep=30 * MeV,
        sectorDist=5.0 * cm,
    )
    algorithms.append(sciglass_ecal_cl_island)

    sciglass_ecal_clreco = RecoCoG(
        "sciglass_ecal_clreco",
        mcHits="EcalBarrelHits",
        inputProtoClusterCollection=sciglass_ecal_cl.outputProtoClusters,
        outputClusterCollection="EcalBarrelClusters",
        outputAssociations="EcalBarrelClustersAssoc",
        enableEtaBounds=True,
        logWeightBase=6.2,
    )
    algorithms.append(sciglass_ecal_clreco)

    barrel_clus_merger = ClusterMerger(
        "barrel_clus_merger",
        inputClusters=sciglass_ecal_clreco.outputClusterCollection,
        inputAssociations=sciglass_ecal_clreco.outputAssociations,
        outputClusters="EcalBarrelMergedClusters",
        outputAssociations="EcalBarrelMergedClustersAssoc",
    )
    algorithms.append(barrel_clus_merger)

# Central Barrel Hcal
cb_hcal_daq = calo_daq["hcal_barrel"]

cb_hcal_digi = CalHitDigi(
    "cb_hcal_digi",
    inputHitCollection="HcalBarrelHits",
    outputHitCollection="HcalBarrelRawHits",
    **cb_hcal_daq,
)
algorithms.append(cb_hcal_digi)

cb_hcal_reco = CalHitReco(
    "cb_hcal_reco",
    inputHitCollection=cb_hcal_digi.outputHitCollection,
    outputHitCollection="HcalBarrelRecHits",
    thresholdFactor=5.0,
    samplingFraction=cb_hcal_sf,
    readoutClass="HcalBarrelHits",
    layerField="layer",
    sectorField="module",
    **cb_hcal_daq,
)
algorithms.append(cb_hcal_reco)

cb_hcal_merger = CalHitsMerger(
    "cb_hcal_merger",
    inputHitCollection=cb_hcal_reco.outputHitCollection,
    outputHitCollection="HcalBarrelMergedHits",
    readoutClass="HcalBarrelHits",
    fields=["layer", "slice"],
    fieldRefNumbers=[1, 0],
)
algorithms.append(cb_hcal_merger)

cb_hcal_cl = IslandCluster(
    "cb_hcal_cl",
    inputHitCollection=cb_hcal_merger.outputHitCollection,
    outputProtoClusterCollection="HcalBarrelProtoClusters",
    splitCluster=False,
    minClusterCenterEdep=30.0 * MeV,
    localDistXY=[15.0 * cm, 15.0 * cm],
)
algorithms.append(cb_hcal_cl)

cb_hcal_clreco = RecoCoG(
    "cb_hcal_clreco",
    mcHits=cb_hcal_digi.inputHitCollection,
    inputProtoClusterCollection=cb_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="HcalBarrelClusters",
    outputAssociations="HcalBarrelClustersAssoc",
    logWeightBase=6.2,
)
algorithms.append(cb_hcal_clreco)

# Hcal Hadron Endcap
ci_hcal_daq = calo_daq["hcal_pos_endcap"]

ci_hcal_digi = CalHitDigi(
    "ci_hcal_digi",
    inputHitCollection="HcalEndcapPHits",
    outputHitCollection="HcalEndcapPRawHits",
    **ci_hcal_daq,
)
algorithms.append(ci_hcal_digi)

ci_hcal_reco = CalHitReco(
    "ci_hcal_reco",
    inputHitCollection=ci_hcal_digi.outputHitCollection,
    outputHitCollection="HcalEndcapPRecHits",
    thresholdFactor=5.0,
    samplingFraction=ci_hcal_sf,
    **ci_hcal_daq,
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
    mcHits=ci_hcal_digi.inputHitCollection,
    inputProtoClusterCollection=ci_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="HcalEndcapPClusters",
    outputAssociations="HcalEndcapPClustersAssoc",
    logWeightBase=6.2,
)
algorithms.append(ci_hcal_clreco)

# Hcal Electron Endcap
ce_hcal_daq = calo_daq["hcal_neg_endcap"]

ce_hcal_digi = CalHitDigi(
    "ce_hcal_digi",
    inputHitCollection="HcalEndcapNHits",
    outputHitCollection="HcalEndcapNRawHits",
    **ce_hcal_daq,
)
algorithms.append(ce_hcal_digi)

ce_hcal_reco = CalHitReco(
    "ce_hcal_reco",
    inputHitCollection=ce_hcal_digi.outputHitCollection,
    outputHitCollection="HcalEndcapNRecHits",
    thresholdFactor=5.0,
    samplingFraction=ce_hcal_sf,
    **ce_hcal_daq,
)
algorithms.append(ce_hcal_reco)

ce_hcal_merger = CalHitsMerger(
    "ce_hcal_merger",
    inputHitCollection=ce_hcal_reco.outputHitCollection,
    outputHitCollection="HcalEndcapNMergedHits",
    readoutClass="HcalEndcapNHits",
    fields=["layer", "slice"],
    fieldRefNumbers=[1, 0],
)
algorithms.append(ce_hcal_merger)

ce_hcal_cl = IslandCluster(
    "ce_hcal_cl",
    inputHitCollection=ce_hcal_merger.outputHitCollection,
    outputProtoClusterCollection="HcalEndcapNProtoClusters",
    splitCluster=False,
    minClusterCenterEdep=30.0 * MeV,
    localDistXY=[15.0 * cm, 15.0 * cm],
)
algorithms.append(ce_hcal_cl)

ce_hcal_clreco = RecoCoG(
    "ce_hcal_clreco",
    mcHits=ce_hcal_digi.inputHitCollection,
    inputProtoClusterCollection=ce_hcal_cl.outputProtoClusterCollection,
    outputClusterCollection="HcalEndcapNClusters",
    outputAssociations="HcalEndcapNClustersAssoc",
    logWeightBase=6.2,
)
algorithms.append(ce_hcal_clreco)

# Tracking
trk_b_coll = SimTrackerHitsCollector(
    "trk_b_coll",
    inputSimTrackerHits=tracker_barrel_collections,
    outputSimTrackerHits="TrackerBarrelAllHits",
)
algorithms.append(trk_b_coll)

trk_b_digi = TrackerDigi(
    "trk_b_digi",
    inputHitCollection=trk_b_coll.outputSimTrackerHits,
    outputHitCollection="TrackerBarrelRawHits",
    timeResolution=8,
)
algorithms.append(trk_b_digi)

trk_ec_coll = SimTrackerHitsCollector(
    "trk_ec_coll",
    inputSimTrackerHits=tracker_endcap_collections,
    outputSimTrackerHits="TrackerEndcapAllHits",
)
algorithms.append(trk_ec_coll)

trk_ec_digi = TrackerDigi(
    "trk_ec_digi",
    inputHitCollection=trk_ec_coll.outputSimTrackerHits,
    outputHitCollection="TrackerEndcapRawHits",
    timeResolution=8,
)
algorithms.append(trk_ec_digi)

vtx_b_coll = SimTrackerHitsCollector(
    "vtx_b_coll",
    inputSimTrackerHits=vertex_barrel_collections,
    outputSimTrackerHits="VertexBarrelAllHits",
)
algorithms.append(vtx_b_coll)

vtx_b_digi = TrackerDigi(
    "vtx_b_digi",
    inputHitCollection=vtx_b_coll.outputSimTrackerHits,
    outputHitCollection="VertexBarrelRawHits",
    timeResolution=8,
)
algorithms.append(vtx_b_digi)

mpgd_b_coll = SimTrackerHitsCollector(
    "mpgd_b_coll",
    inputSimTrackerHits=mpgd_barrel_collections,
    outputSimTrackerHits="MPGDTrackerBarrelAllHits",
)
algorithms.append(mpgd_b_coll)

mpgd_b_digi = TrackerDigi(
    "mpgd_b_digi",
    inputHitCollection=mpgd_b_coll.outputSimTrackerHits,
    outputHitCollection="MPGDTrackerBarrelRawHits",
    timeResolution=8,
)
algorithms.append(mpgd_b_digi)

# Tracker and vertex reconstruction
trk_b_reco = TrackerHitReconstruction(
    "trk_b_reco",
    inputHitCollection=trk_b_digi.outputHitCollection,
    outputHitCollection="TrackerBarrelRecHits",
)
algorithms.append(trk_b_reco)

trk_ec_reco = TrackerHitReconstruction(
    "trk_ec_reco",
    inputHitCollection=trk_ec_digi.outputHitCollection,
    outputHitCollection="TrackerEndcapRecHits",
)
algorithms.append(trk_ec_reco)

vtx_b_reco = TrackerHitReconstruction(
    "vtx_b_reco",
    inputHitCollection=vtx_b_digi.outputHitCollection,
    outputHitCollection="VertexBarrelRecHits",
)
algorithms.append(vtx_b_reco)

mpgd_b_reco = TrackerHitReconstruction(
    "mpgd_b_reco",
    inputHitCollection=mpgd_b_digi.outputHitCollection,
    outputHitCollection="MPGDTrackerBarrelRecHits",
)
algorithms.append(mpgd_b_reco)

input_tracking_hits = [
    str(trk_b_reco.outputHitCollection),
    str(trk_ec_reco.outputHitCollection),
    str(vtx_b_reco.outputHitCollection),
    str(mpgd_b_reco.outputHitCollection),
]

trk_hit_col = TrackingHitsCollector(
    "trk_hit_col",
    inputTrackingHits=input_tracking_hits,
    trackingHits="trackingHits",
)
algorithms.append(trk_hit_col)

# Hit Source linker
sourcelinker = TrackerSourceLinker(
    "trk_srcslnkr",
    inputHitCollection=trk_hit_col.trackingHits,
    outputSourceLinks="TrackSourceLinks",
    outputMeasurements="TrackMeasurements",
)
algorithms.append(sourcelinker)

## Track param init
truth_trk_init = TrackParamTruthInit(
    "truth_trk_init",
    inputMCParticles="MCParticles",
    outputInitialTrackParameters="InitTrackParams",
)
algorithms.append(truth_trk_init)

# Tracking algorithms
trk_find_alg = CKFTracking(
    "trk_find_alg",
    inputSourceLinks=sourcelinker.outputSourceLinks,
    inputMeasurements=sourcelinker.outputMeasurements,
    inputInitialTrackParameters=truth_trk_init.outputInitialTrackParameters,
    outputTrajectories="trajectories",
    chi2CutOff=[50.0],
)
algorithms.append(trk_find_alg)

parts_from_fit = ParticlesFromTrackFit(
    "parts_from_fit",
    inputTrajectories=trk_find_alg.outputTrajectories,
    outputParticles="outputParticles",
    outputTrackParameters="outputTrackParameters",
)
algorithms.append(parts_from_fit)

# trajs_from_fit = TrajectoryFromTrackFit("trajs_from_fit",
#         inputTrajectories = trk_find_alg.outputTrajectories,
#         outputTrajectoryParameters = "outputTrajectoryParameters")
# algorithms.append(trajs_from_fit)

# Event building
parts_with_truth_pid = ParticlesWithTruthPID(
    "parts_with_truth_pid",
    inputMCParticles="MCParticles",
    inputTrackParameters=parts_from_fit.outputTrackParameters,
    outputParticles="ReconstructedChargedParticles",
    outputAssociations="ReconstructedChargedParticlesAssoc",
)
algorithms.append(parts_with_truth_pid)

match_clusters = MatchClusters(
    "match_clusters",
    inputMCParticles="MCParticles",
    inputParticles=parts_with_truth_pid.outputParticles,
    inputParticlesAssoc=parts_with_truth_pid.outputAssociations,
    inputClusters=[
        str(ce_ecal_clmerger.outputClusters),
        str(barrel_clus_merger.outputClusters),
        str(ci_ecal_clmerger.outputClusters),
        str(ce_hcal_clreco.outputClusterCollection),
        str(cb_hcal_clreco.outputClusterCollection),
        str(ci_hcal_clreco.outputClusterCollection),
    ],
    inputClustersAssoc=[
        str(ce_ecal_clmerger.outputAssociations),
        str(barrel_clus_merger.outputAssociations),
        str(ci_ecal_clmerger.outputAssociations),
        str(ce_hcal_clreco.outputAssociations),
        str(cb_hcal_clreco.outputAssociations),
        str(ci_hcal_clreco.outputAssociations),
    ],
    outputParticles="ReconstructedParticles",
    outputParticlesAssoc="ReconstructedParticlesAssoc",
)
algorithms.append(match_clusters)

## Far Forward for now stored separately
fast_ff = FFSmearedParticles(
    "fast_ff",
    inputMCParticles="MCParticles",
    outputParticles="ReconstructedFFParticles",
    outputAssociations="ReconstructedFFParticlesAssoc",
    enableZDC=True,
    enableB0=True,
    enableRP=True,
    enableOMD=True,
    ionBeamEnergy=ionBeamEnergy,
    crossingAngle=-0.025,
)
algorithms.append(fast_ff)

# DRICH
drich_digi = PhotoMultiplierDigi(
    "drich_digi",
    inputHitCollection="DRICHHits",
    outputHitCollection="DRICHRawHits",
    quantumEfficiency=[(a * eV, b) for a, b in qe_data],
)
algorithms.append(drich_digi)

drich_reco = PhotoMultiplierReco(
    "drich_reco",
    inputHitCollection=drich_digi.outputHitCollection,
    outputHitCollection="DRICHRecHits",
)
algorithms.append(drich_reco)

# FIXME
# drich_cluster = PhotoRingClusters("drich_cluster",
#        inputHitCollection=pmtreco.outputHitCollection,
#        #inputTrackCollection=parts_with_truth_pid.outputParticles,
#        outputClusterCollection="ForwardRICHClusters")

# MRICH
if "acadia" in detector_version:
    mrich_digi = PhotoMultiplierDigi(
        "mrich_digi",
        inputHitCollection="MRICHHits",
        outputHitCollection="MRICHRawHits",
        quantumEfficiency=[(a * eV, b) for a, b in qe_data],
    )
    algorithms.append(mrich_digi)
    mrich_reco = PhotoMultiplierReco(
        "mrich_reco",
        inputHitCollection=mrich_digi.outputHitCollection,
        outputHitCollection="MRICHRecHits",
    )
    algorithms.append(mrich_reco)

# Inclusive kinematics
incl_kin_electron = InclusiveKinematicsElectron(
    "incl_kin_electron",
    inputMCParticles="MCParticles",
    inputReconstructedParticles=parts_with_truth_pid.outputParticles,
    inputParticleAssociations=parts_with_truth_pid.outputAssociations,
    outputInclusiveKinematics="InclusiveKinematicsElectron",
)
algorithms.append(incl_kin_electron)
incl_kin_jb = InclusiveKinematicsJB(
    "incl_kin_jb",
    inputMCParticles="MCParticles",
    inputReconstructedParticles=parts_with_truth_pid.outputParticles,
    inputParticleAssociations=parts_with_truth_pid.outputAssociations,
    outputInclusiveKinematics="InclusiveKinematicsJB",
)
algorithms.append(incl_kin_jb)
incl_kin_da = InclusiveKinematicsDA(
    "incl_kin_da",
    inputMCParticles="MCParticles",
    inputReconstructedParticles=parts_with_truth_pid.outputParticles,
    inputParticleAssociations=parts_with_truth_pid.outputAssociations,
    outputInclusiveKinematics="InclusiveKinematicsDA",
)
algorithms.append(incl_kin_da)
incl_kin_sigma = InclusiveKinematicsSigma(
    "incl_kin_sigma",
    inputMCParticles="MCParticles",
    inputReconstructedParticles=parts_with_truth_pid.outputParticles,
    inputParticleAssociations=parts_with_truth_pid.outputAssociations,
    outputInclusiveKinematics="InclusiveKinematicsSigma",
)
algorithms.append(incl_kin_sigma)
incl_kin_esigma = InclusiveKinematicseSigma(
    "incl_kin_esigma",
    inputMCParticles="MCParticles",
    inputReconstructedParticles=parts_with_truth_pid.outputParticles,
    inputParticleAssociations=parts_with_truth_pid.outputAssociations,
    outputInclusiveKinematics="InclusiveKinematicseSigma",
)
algorithms.append(incl_kin_esigma)

# Output
podout = PodioOutput("out", filename=output_rec)
podout.outputCommands = (
    [
        "keep *",
        "drop *Hits",
        "keep *Layers",
        "keep *Clusters",
        "drop *ProtoClusters",
        "drop outputParticles",
        "drop InitTrackParams",
    ]
    + ["drop " + c for c in sim_coll]
    + ["keep MCParticles"]
)
algorithms.append(podout)

ApplicationMgr(
    TopAlg=algorithms,
    EvtSel="NONE",
    EvtMax=n_events,
    ExtSvc=services,
    OutputLevel=WARNING,
    AuditAlgorithms=True,
    HistogramPersistency="ROOT",
)
