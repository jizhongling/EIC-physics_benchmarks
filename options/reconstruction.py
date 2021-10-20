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

# RICH reconstruction
qe_data = [(1.0, 0.25), (7.5, 0.25),]

# CAL reconstruction
# get sampling fractions from system environment variable
ci_ecal_sf = float(os.environ.get("CI_ECAL_SAMP_FRAC", 0.253))
cb_hcal_sf = float(os.environ.get("CB_HCAL_SAMP_FRAC", 0.038))
ci_hcal_sf = float(os.environ.get("CI_HCAL_SAMP_FRAC", 0.025))
ce_hcal_sf = float(os.environ.get("CE_HCAL_SAMP_FRAC", 0.025))

# input arguments from calibration file
with open('config/emcal_barrel_calibration.json') as f:
    calib_data = json.load(f)['electron']

print(calib_data)

img_barrel_sf = float(calib_data['sampling_fraction_img'])
scifi_barrel_sf = float(calib_data['sampling_fraction_scfi'])

# input and output
input_sims = [f.strip() for f in str.split(os.environ["JUGGLER_SIM_FILE"], ",") if f.strip()]
output_rec = str(os.environ["JUGGLER_REC_FILE"])
n_events = int(os.environ["JUGGLER_N_EVENTS"])

# services
services = []
# auditor service
services.append(AuditorSvc("AuditorSvc", Auditors=['ChronoAuditor', 'MemStatAuditor']))
# geometry service
## only have material maps for acadia right now
if detector_version == 'acadia':
    services.append(GeoSvc("GeoSvc", detectors=["{}/{}.xml".format(detector_path,detector_name)],
                                     materials="config/material-maps.json",
                                     OutputLevel=WARNING))
else:
    services.append(GeoSvc("GeoSvc", detectors=["{}/{}.xml".format(detector_path,detector_name)],
                                    #materials="config/material-maps.json",
                                    OutputLevel=WARNING))
# data service
services.append(EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING))

# juggler components
from Configurables import PodioInput
from Configurables import Jug__Base__InputCopier_dd4pod__Geant4ParticleCollection_dd4pod__Geant4ParticleCollection_ as MCCopier
from Configurables import Jug__Base__InputCopier_dd4pod__CalorimeterHitCollection_dd4pod__CalorimeterHitCollection_ as CalCopier
from Configurables import Jug__Base__InputCopier_dd4pod__TrackerHitCollection_dd4pod__TrackerHitCollection_ as TrkCopier
from Configurables import Jug__Base__InputCopier_dd4pod__PhotoMultiplierHitCollection_dd4pod__PhotoMultiplierHitCollection_ as PMTCopier

from Configurables import Jug__Fast__MC2SmearedParticle as MC2DummyParticle
from Configurables import Jug__Fast__ParticlesWithTruthPID as ParticlesWithTruthPID
from Configurables import Jug__Fast__SmearedFarForwardParticles as FFSmearedParticles
from Configurables import Jug__Fast__MatchClusters as MatchClusters
from Configurables import Jug__Fast__ClusterMerger as ClusterMerger
from Configurables import Jug__Fast__TruthEnergyPositionClusterMerger as EnergyPositionClusterMerger
from Configurables import Jug__Fast__InclusiveKinematicsTruth as InclusiveKinematicsTruth

from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

from Configurables import Jug__Reco__TrackerHitReconstruction as TrackerHitReconstruction
from Configurables import Jug__Reco__TrackingHitsCollector2 as TrackingHitsCollector
from Configurables import Jug__Reco__TrackerSourceLinker as TrackerSourceLinker

from Configurables import Jug__Reco__TrackParamTruthInit as TrackParamTruthInit
from Configurables import Jug__Reco__TrackParamClusterInit as TrackParamClusterInit
from Configurables import Jug__Reco__TrackParamVertexClusterInit as TrackParamVertexClusterInit
from Configurables import Jug__Reco__CKFTracking as CKFTracking
from Configurables import Jug__Reco__ParticlesFromTrackFit as ParticlesFromTrackFit
from Configurables import Jug__Reco__TrajectoryFromTrackFit as TrajectoryFromTrackFit
from Configurables import Jug__Reco__InclusiveKinematicsElectron as InclusiveKinematicsElectron

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
    'mcparticles',
    'EcalEndcapNHits',
    'EcalEndcapPHits',
    'EcalBarrelHits',
    'EcalBarrelScFiHits',
    'HcalBarrelHits',
    'HcalEndcapPHits',
    'HcalEndcapNHits',
    'TrackerEndcapHits',
    'TrackerBarrelHits',
    'GEMTrackerEndcapHits',
    'VertexBarrelHits',
    'DRICHHits',
]
if 'acadia' in detector_version:
    sim_coll.append('VertexEndcapHits')
    sim_coll.append('MRICHHits')
else:
    sim_coll.append('MPGDTrackerBarrelHits')

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

# Generated particles
dummy = MC2DummyParticle("dummy",
        inputParticles="mcparticles",
        outputParticles="GeneratedParticles",
        smearing=0)
algorithms.append(dummy)

# Truth level kinematics
truth_incl_kin = InclusiveKinematicsTruth("truth_incl_kin",
        inputMCParticles="mcparticles",
        outputData="InclusiveKinematicsTruth"
)
algorithms.append(truth_incl_kin)

# Crystal Endcap Ecal
ce_ecal_daq = dict(
        dynamicRangeADC=5.*units.GeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=3)

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
        readoutClass="EcalEndcapNHits",
        sectorField="sector",
        **ce_ecal_daq)
algorithms.append(ce_ecal_reco)

ce_ecal_cl = IslandCluster("ce_ecal_cl",
        inputHitCollection=ce_ecal_reco.outputHitCollection,
        outputProtoClusterCollection="EcalEndcapNProtoClusters",
        splitCluster=False,
        minClusterHitEdep=1.0*units.MeV,  # discard low energy hits
        minClusterCenterEdep=30*units.MeV,
        sectorDist=5.0*units.cm,
        dimScaledLocalDistXY=[1.8, 1.8]) # dimension scaled dist is good for hybrid sectors with different module size
algorithms.append(ce_ecal_cl)

ce_ecal_clreco = RecoCoG("ce_ecal_clreco",
        inputHitCollection=ce_ecal_cl.inputHitCollection,
        inputProtoClusterCollection=ce_ecal_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalEndcapNClusters",
        mcHits="EcalEndcapNHits",
        samplingFraction=0.998,      # this accounts for a small fraction of leakage
        logWeightBase=4.6)
algorithms.append(ce_ecal_clreco)

ce_ecal_clmerger = ClusterMerger("ce_ecal_clmerger",
        inputClusters = ce_ecal_clreco.outputClusterCollection,
        outputClusters = "EcalEndcapNMergedClusters",
        outputRelations = "EcalEndcapNMergedClusterRelations")
algorithms.append(ce_ecal_clmerger)

# Endcap Sampling Ecal
ci_ecal_daq = dict(
        dynamicRangeADC=50.*units.MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

ci_ecal_digi = CalHitDigi("ci_ecal_digi",
        inputHitCollection="EcalEndcapPHits",
        outputHitCollection="EcalEndcapPRawHits",
        **ci_ecal_daq)
algorithms.append(ci_ecal_digi)

ci_ecal_reco = CalHitReco("ci_ecal_reco",
        inputHitCollection=ci_ecal_digi.outputHitCollection,
        outputHitCollection="EcalEndcapPRecHits",
        thresholdFactor=5.0,
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

ci_ecal_cl = IslandCluster("ci_ecal_cl",
        inputHitCollection=ci_ecal_merger.outputHitCollection,
        outputProtoClusterCollection="EcalEndcapPProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=10.*units.MeV,
        localDistXY=[10*units.mm, 10*units.mm])
algorithms.append(ci_ecal_cl)

ci_ecal_clreco = RecoCoG("ci_ecal_clreco",
        inputHitCollection=ci_ecal_cl.inputHitCollection,
        inputProtoClusterCollection=ci_ecal_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalEndcapPClusters",
        mcHits="EcalEndcapPHits",
        logWeightBase=6.2,
        samplingFraction=ci_ecal_sf)
algorithms.append(ci_ecal_clreco)

ci_ecal_clmerger = ClusterMerger("ci_ecal_clmerger",
        inputClusters = ci_ecal_clreco.outputClusterCollection,
        outputClusters = "EcalEndcapPMergedClusters",
        outputRelations = "EcalEndcapPMergedClusterRelations")
algorithms.append(ci_ecal_clmerger)

# Central Barrel Ecal (Imaging Cal.)
img_barrel_daq = dict(
        dynamicRangeADC=3*units.MeV,
        capacityADC=8192,
        pedestalMean=400,
        pedestalSigma=20)   # about 6 keV

img_barrel_digi = CalHitDigi("img_barrel_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelImagingRawHits",
        energyResolutions=[0., 0.02, 0.],   # 2% flat resolution
        **img_barrel_daq)
algorithms.append(img_barrel_digi)

img_barrel_reco = ImCalPixelReco("img_barrel_reco",
        inputHitCollection=img_barrel_digi.outputHitCollection,
        outputHitCollection="EcalBarrelImagingRecHits",
        thresholdFactor=3,  # about 20 keV
        readoutClass="EcalBarrelHits",  # readout class
        layerField="layer",             # field to get layer id
        sectorField="module",           # field to get sector id
        **img_barrel_daq)
algorithms.append(img_barrel_reco)

img_barrel_cl = ImagingCluster("img_barrel_cl",
        inputHitCollection=img_barrel_reco.outputHitCollection,
        outputProtoClusterCollection="EcalBarrelImagingProtoClusters",
        localDistXY=[2.*units.mm, 2*units.mm],  # same layer
        layerDistEtaPhi=[10*units.mrad, 10*units.mrad],     # adjacent layer
        neighbourLayersRange=2,                 # id diff for adjacent layer
        sectorDist=3.*units.cm)                       # different sector
algorithms.append(img_barrel_cl)

img_barrel_clreco = ImagingClusterReco("img_barrel_clreco",
        samplingFraction=img_barrel_sf,
        inputHitCollection=img_barrel_cl.inputHitCollection,
        inputProtoClusterCollection=img_barrel_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalBarrelImagingClusters",
        mcHits="EcalBarrelHits",
        outputLayerCollection="EcalBarrelImagingLayers")
algorithms.append(img_barrel_clreco)

# Central ECAL SciFi
scfi_barrel_daq = dict(
        dynamicRangeADC=50.*MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

scfi_barrel_digi = CalHitDigi("scfi_barrel_digi",
        inputHitCollection="EcalBarrelScFiHits",
        outputHitCollection="EcalBarrelScFiRawHits",
        **scfi_barrel_daq)
algorithms.append(scfi_barrel_digi)

scfi_barrel_reco = CalHitReco("scfi_barrel_reco",
        inputHitCollection=scfi_barrel_digi.outputHitCollection,
        outputHitCollection="EcalBarrelScFiRecHits",
        thresholdFactor=5.0,
        readoutClass="EcalBarrelScFiHits",
        layerField="layer",
        sectorField="module",
        localDetFields=["system", "module"], # use local coordinates in each module (stave)
        **scfi_barrel_daq)
algorithms.append(scfi_barrel_reco)

# merge hits in different layer (projection to local x-y plane)
scfi_barrel_merger = CalHitsMerger("scfi_barrel_merger",
         inputHitCollection=scfi_barrel_reco.outputHitCollection,
         outputHitCollection="EcalBarrelScFiMergedHits",
         fields=["fiber"],
         fieldRefNumbers=[1],
         readoutClass="EcalBarrelScFiHits")
algorithms.append(scfi_barrel_merger)

scfi_barrel_cl = IslandCluster("scfi_barrel_cl",
         inputHitCollection=scfi_barrel_merger.outputHitCollection,
         outputProtoClusterCollection="EcalBarrelScFiProtoClusters",
         splitCluster=False,
         minClusterCenterEdep=10.*MeV,
         localDistXZ=[30*mm, 30*mm])
algorithms.append(scfi_barrel_cl)

scfi_barrel_clreco = RecoCoG("scfi_barrel_clreco",
         inputHitCollection=scfi_barrel_cl.inputHitCollection,
         inputProtoClusterCollection=scfi_barrel_cl.outputProtoClusterCollection,
         outputClusterCollection="EcalBarrelScFiClusters",
         mcHits="EcalBarrelScFiHits",
         logWeightBase=6.2,
         samplingFraction= scifi_barrel_sf)
algorithms.append(scfi_barrel_clreco)

## barrel cluster merger
barrel_clus_merger = EnergyPositionClusterMerger("barrel_clus_merger",
        inputMCParticles = "mcparticles",
        inputEnergyClusters = scfi_barrel_clreco.outputClusterCollection,
        inputPositionClusters = img_barrel_clreco.outputClusterCollection,
        outputClusters = "EcalBarrelMergedClusters",
        outputRelations = "EcalBarrelMergedClusterRelations")
algorithms.append(barrel_clus_merger)


# Central Barrel Hcal
cb_hcal_daq = dict(
         dynamicRangeADC=50.*units.MeV,
         capacityADC=32768,
         pedestalMean=400,
         pedestalSigma=10)

cb_hcal_digi = CalHitDigi("cb_hcal_digi",
         inputHitCollection="HcalBarrelHits",
         outputHitCollection="HcalBarrelRawHits",
         **cb_hcal_daq)
algorithms.append(cb_hcal_digi)

cb_hcal_reco = CalHitReco("cb_hcal_reco",
        inputHitCollection=cb_hcal_digi.outputHitCollection,
        outputHitCollection="HcalBarrelRecHits",
        thresholdFactor=5.0,
        readoutClass="HcalBarrelHits",
        layerField="layer",
        sectorField="module",
        **cb_hcal_daq)
algorithms.append(cb_hcal_reco)

cb_hcal_merger = CalHitsMerger("cb_hcal_merger",
        inputHitCollection=cb_hcal_reco.outputHitCollection,
        outputHitCollection="HcalBarrelMergedHits",
        readoutClass="HcalBarrelHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(cb_hcal_merger)

cb_hcal_cl = IslandCluster("cb_hcal_cl",
        inputHitCollection=cb_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalBarrelProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*units.MeV,
        localDistXY=[15.*units.cm, 15.*units.cm])
algorithms.append(cb_hcal_cl)

cb_hcal_clreco = RecoCoG("cb_hcal_clreco",
        inputHitCollection=cb_hcal_cl.inputHitCollection,
        inputProtoClusterCollection=cb_hcal_cl.outputProtoClusterCollection,
        outputClusterCollection="HcalBarrelClusters",
        mcHits="HcalBarrelHits",
        logWeightBase=6.2,
        samplingFraction=cb_hcal_sf)
algorithms.append(cb_hcal_clreco)

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

# Tracking
trk_b_digi = TrackerDigi("trk_b_digi",
        inputHitCollection="TrackerBarrelHits",
        outputHitCollection="TrackerBarrelRawHits",
        timeResolution=8)
algorithms.append(trk_b_digi)

trk_ec_digi = TrackerDigi("trk_ec_digi",
        inputHitCollection="TrackerEndcapHits",
        outputHitCollection="TrackerEndcapRawHits",
        timeResolution=8)
algorithms.append(trk_ec_digi)

vtx_b_digi = TrackerDigi("vtx_b_digi",
        inputHitCollection="VertexBarrelHits",
        outputHitCollection="VertexBarrelRawHits",
        timeResolution=8)
algorithms.append(vtx_b_digi)

if 'acadia' in detector_version:
    vtx_ec_digi = TrackerDigi("vtx_ec_digi", 
            inputHitCollection="VertexEndcapHits",
            outputHitCollection="VertexEndcapRawHits",
            timeResolution=8)
    algorithms.append( vtx_ec_digi )
else:
    mm_b_digi = TrackerDigi("mm_b_digi", 
            inputHitCollection="MPGDTrackerBarrelHits",
            outputHitCollection="MPGDTrackerBarrelRawHits",
            timeResolution=8)
    algorithms.append( mm_b_digi )

gem_ec_digi = TrackerDigi("gem_ec_digi",
        inputHitCollection="GEMTrackerEndcapHits",
        outputHitCollection="GEMTrackerEndcapRawHits",
        timeResolution=10)
algorithms.append(gem_ec_digi)

# Tracker and vertex reconstruction
trk_b_reco = TrackerHitReconstruction("trk_b_reco",
        inputHitCollection = trk_b_digi.outputHitCollection,
        outputHitCollection="TrackerBarrelRecHits")
algorithms.append(trk_b_reco)

trk_ec_reco = TrackerHitReconstruction("trk_ec_reco",
        inputHitCollection = trk_ec_digi.outputHitCollection,
        outputHitCollection="TrackerEndcapRecHits")
algorithms.append(trk_ec_reco)

vtx_b_reco = TrackerHitReconstruction("vtx_b_reco",
        inputHitCollection = vtx_b_digi.outputHitCollection,
        outputHitCollection="VertexBarrelRecHits")
algorithms.append(vtx_b_reco)

if 'acadia' in detector_version:
    vtx_ec_reco = TrackerHitReconstruction("vtx_ec_reco",
            inputHitCollection = vtx_ec_digi.outputHitCollection,
            outputHitCollection="VertexEndcapRecHits")
    algorithms.append( vtx_ec_reco )
else:
    mm_b_reco = TrackerHitReconstruction("mm_b_reco",
            inputHitCollection = mm_b_digi.outputHitCollection,
            outputHitCollection="MPGDTrackerBarrelRecHits")
    algorithms.append( mm_b_reco )

gem_ec_reco = TrackerHitReconstruction("gem_ec_reco",
        inputHitCollection=gem_ec_digi.outputHitCollection,
        outputHitCollection="GEMTrackerEndcapRecHits")
algorithms.append(gem_ec_reco)

input_tracking_hits = [
    str(trk_b_reco.outputHitCollection),
    str(trk_ec_reco.outputHitCollection),
    str(vtx_b_reco.outputHitCollection),
    str(gem_ec_reco.outputHitCollection) ]
if 'acadia' in detector_version:
    input_tracking_hits.append(str(vtx_ec_reco.outputHitCollection))
else:
    input_tracking_hits.append(str(mm_b_reco.outputHitCollection))

trk_hit_col = TrackingHitsCollector("trk_hit_col",
        inputTrackingHits=input_tracking_hits,
        trackingHits="trackingHits",
        OutputLevel=VERBOSE)
algorithms.append( trk_hit_col )

# Hit Source linker
sourcelinker = TrackerSourceLinker("trk_srcslnkr",
        inputHitCollection = trk_hit_col.trackingHits,
        outputSourceLinks = "TrackSourceLinks",
        outputMeasurements = "TrackMeasurements")
algorithms.append(sourcelinker)

## Track param init
truth_trk_init = TrackParamTruthInit("truth_trk_init",
        inputMCParticles="mcparticles",
        outputInitialTrackParameters="InitTrackParams")
algorithms.append(truth_trk_init)

# Tracking algorithms
trk_find_alg = CKFTracking("trk_find_alg",
        inputSourceLinks = sourcelinker.outputSourceLinks,
        inputMeasurements = sourcelinker.outputMeasurements,
        inputInitialTrackParameters = truth_trk_init.outputInitialTrackParameters,
        outputTrajectories = "trajectories")
algorithms.append(trk_find_alg)

parts_from_fit = ParticlesFromTrackFit("parts_from_fit",
        inputTrajectories = trk_find_alg.outputTrajectories,
        outputParticles = "outputParticles",
        outputTrackParameters = "outputTrackParameters")
algorithms.append(parts_from_fit)

trajs_from_fit = TrajectoryFromTrackFit("trajs_from_fit",
        inputTrajectories = trk_find_alg.outputTrajectories,
        outputTrajectoryParameters = "outputTrajectoryParameters")
algorithms.append(trajs_from_fit)

# Event building
parts_with_truth_pid = ParticlesWithTruthPID("parts_with_truth_pid",
        inputMCParticles = "mcparticles",
        inputTrackParameters = parts_from_fit.outputTrackParameters,
        outputParticles = "ReconstructedChargedParticles")
algorithms.append(parts_with_truth_pid)

match_clusters = MatchClusters("match_clusters",
        inputMCParticles = "mcparticles",
        inputParticles = parts_with_truth_pid.outputParticles,
        inputEcalClusters = [
                str(ce_ecal_clmerger.outputClusters),
                str(barrel_clus_merger.outputClusters),
                str(ci_ecal_clmerger.outputClusters)
        ],
        inputHcalClusters = [
                str(ce_hcal_clreco.outputClusterCollection),
                str(cb_hcal_clreco.outputClusterCollection),
                str(ci_hcal_clreco.outputClusterCollection)
        ],
        outputParticles = "ReconstructedParticles")
algorithms.append(match_clusters)

## Far Forward for now stored separately
fast_ff = FFSmearedParticles("fast_ff",
        inputMCParticles = "mcparticles",
        outputParticles  = "ReconstructedFFParticles",
        enableZDC        = True,
        enableB0         = True,
        enableRP         = True,
        enableOMD        = True,
        ionBeamEnergy    = 100,
        crossingAngle    = -0.025)
algorithms.append(fast_ff)

# DRICH
drich_digi = PhotoMultiplierDigi("drich_digi",
        inputHitCollection="DRICHHits",
        outputHitCollection="DRICHRawHits",
        quantumEfficiency=[(a*units.eV, b) for a, b in qe_data])
algorithms.append(drich_digi)

drich_reco = PhotoMultiplierReco("drich_reco",
        inputHitCollection=drich_digi.outputHitCollection,
        outputHitCollection="DRICHRecHits")
algorithms.append(drich_reco)

# FIXME
#drich_cluster = PhotoRingClusters("drich_cluster",
#        inputHitCollection=pmtreco.outputHitCollection,
#        #inputTrackCollection="ReconstructedParticles",
#        outputClusterCollection="ForwardRICHClusters")

# MRICH
if 'acadia' in detector_version:
    mrich_digi = PhotoMultiplierDigi("mrich_digi",
            inputHitCollection="MRICHHits",
            outputHitCollection="MRICHRawHits",
            quantumEfficiency=[(a*units.eV, b) for a, b in qe_data])
    algorithms.append(mrich_digi)
    mrich_reco = PhotoMultiplierReco("mrich_reco",
            inputHitCollection=mrich_digi.outputHitCollection,
            outputHitCollection="MRICHRecHits")
    algorithms.append(mrich_reco)

# Electron kinematics
electron_incl_kin = InclusiveKinematicsElectron("electron_incl_kin",
        inputMCParticles="mcparticles",
        inputParticles="ReconstructedParticles",
        outputData="InclusiveKinematicsElectron"
)
algorithms.append(electron_incl_kin)

# Output
podout = PodioOutput("out", filename=output_rec)
podout.outputCommands = [
        "keep *",
        "drop *Hits",
        "keep *Layers",
        "keep *Clusters",
        "drop *ProtoClusters",
        "drop outputParticles",
        "drop InitTrackParams",
        ] + [
        "drop " + c for c in sim_coll
        ] + [
        "keep mcparticles"
        ]
algorithms.append(podout)

ApplicationMgr(
    TopAlg = algorithms,
    EvtSel = 'NONE',
    EvtMax = n_events,
    ExtSvc = services,
    OutputLevel = WARNING,
    AuditAlgorithms = True
 )
