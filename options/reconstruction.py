from Gaudi.Configuration import *

from Configurables import ApplicationMgr, EICDataSvc, PodioOutput, GeoSvc
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

# geometry service
geo_service = GeoSvc("GeoSvc", detectors=["{}.xml".format(compact_path)], OutputLevel=WARNING)
# data service
podioevent = EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING)

# juggler components
from Configurables import PodioInput
from Configurables import Jug__Base__InputCopier_dd4pod__Geant4ParticleCollection_dd4pod__Geant4ParticleCollection_ as MCCopier
from Configurables import Jug__Base__InputCopier_dd4pod__CalorimeterHitCollection_dd4pod__CalorimeterHitCollection_ as CalCopier
from Configurables import Jug__Base__InputCopier_dd4pod__TrackerHitCollection_dd4pod__TrackerHitCollection_ as TrkCopier
from Configurables import Jug__Base__InputCopier_dd4pod__PhotoMultiplierHitCollection_dd4pod__PhotoMultiplierHitCollection_ as PMTCopier

from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__UFSDTrackerDigi as TrackerDigi

from Configurables import Jug__Reco__TrackerHitReconstruction as TrackerHitReconstruction
from Configurables import Jug__Reco__TrackingHitsCollector2 as TrackingHitsCollector
from Configurables import Jug__Reco__TrackerSourceLinker as TrackerSourceLinker
from Configurables import Jug__Reco__TrackerSourcesLinker as TrackerSourcesLinker
#from Configurables import Jug__Reco__TrackingHitsSourceLinker as TrackingHitsSourceLinker
from Configurables import Jug__Reco__TrackParamTruthInit as TrackParamTruthInit
from Configurables import Jug__Reco__TrackParamClusterInit as TrackParamClusterInit
from Configurables import Jug__Reco__TrackParamVertexClusterInit as TrackParamVertexClusterInit
from Configurables import Jug__Reco__TrackFindingAlgorithm as TrackFindingAlgorithm
from Configurables import Jug__Reco__ParticlesFromTrackFit as ParticlesFromTrackFit

from Configurables import Jug__Reco__CalorimeterHitReco as CalHitReco
from Configurables import Jug__Reco__CalorimeterHitsMerger as CalHitsMerger
from Configurables import Jug__Reco__CalorimeterIslandCluster as IslandCluster

from Configurables import Jug__Reco__ImagingPixelReco as ImCalPixelReco
from Configurables import Jug__Reco__ImagingTopoCluster as ImagingCluster

from Configurables import Jug__Reco__ClusterRecoCoG as RecoCoG
from Configurables import Jug__Reco__ImagingClusterReco as ImagingClusterReco

from Configurables import Jug__Reco__PhotoMultiplierReco as PhotoMultiplierReco
from Configurables import Jug__Reco__PhotoRingClusters as PhotoRingClusters

from Configurables import Jug__Reco__EMCalReconstruction as EMCalReconstruction

# branches needed from simulation root file
sim_coll = [
    "mcparticles",
    "EcalEndcapNHits",
    "EcalEndcapPHits",
    "EcalBarrelHits",
    "EcalBarrelScFiHits",
    "HcalBarrelHits",
    "HcalEndcapPHits",
    "HcalEndcapNHits",
    "TrackerEndcapHits",
    "TrackerBarrelHits",
    "GEMTrackerEndcapHits",
    "VertexBarrelHits",
    "VertexEndcapHits",
    "DRICHHits",
    "MRICHHits"
]

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

## copiers to get around input --> output copy bug. Note the "2" appended to the output collection.
copier = MCCopier("MCCopier",
        inputCollection="mcparticles",
        outputCollection="mcparticles2")
algorithms.append(copier)

trkcopier = TrkCopier("TrkCopier",
        inputCollection="TrackerBarrelHits",
        outputCollection="TrackerBarrelHits2")
algorithms.append(trkcopier)

pmtcopier = PMTCopier("PMTCopier",
        inputCollection="DRICHHits",
        outputCollection="DRICHHits2")
algorithms.append(pmtcopier)

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
        samplingFraction=0.998,      # this accounts for a small fraction of leakage
        logWeightBase=4.6)
algorithms.append(ce_ecal_clreco)

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
        outputHitCollection="EcalEndcapPRecHitsXY",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0],
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
        outputInfoCollection="EcalEndcapPClustersInfo",
        logWeightBase=6.2,
        samplingFraction=ci_ecal_sf)
algorithms.append(ci_ecal_clreco)

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
        outputInfoCollection="EcalBarrelImagingClustersInfo",
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
         outputHitCollection="EcalBarrelScFiGridReco",
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
         outputInfoCollection="EcalBarrelScFiClustersInfo",
         logWeightBase=6.2,
         samplingFraction= scifi_barrel_sf)
algorithms.append(scfi_barrel_clreco)

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
        outputHitCollection="HcalBarrelRecHitsXY",
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
        outputInfoCollection="HcalBarrelClustersInfo",
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
        outputHitCollection="HcalEndcapPRecHitsXY",
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
        outputInfoCollection="HcalEndcapPClustersInfo",
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
        outputHitCollection="HcalEndcapNRecHitsXY",
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
        outputInfoCollection="HcalEndcapNClustersInfo",
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

vtx_ec_digi = TrackerDigi("vtx_ec_digi",
        inputHitCollection="VertexEndcapHits",
        outputHitCollection="VertexEndcapRawHits",
        timeResolution=8)
algorithms.append(vtx_ec_digi)

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

vtx_ec_reco = TrackerHitReconstruction("vtx_ec_reco",
        inputHitCollection = vtx_ec_digi.outputHitCollection,
        outputHitCollection="VertexEndcapRecHits")
algorithms.append(vtx_ec_reco)

gem_ec_reco = TrackerHitReconstruction("gem_ec_reco",
        inputHitCollection=gem_ec_digi.outputHitCollection,
        outputHitCollection="GEMTrackerEndcapRecHits")
algorithms.append(gem_ec_reco)

# Tracking hit collector
trk_hit_col = TrackingHitsCollector("trk_hit_col",
        inputTrackingHits=[
            str(trk_b_reco.outputHitCollection),
            str(trk_ec_reco.outputHitCollection),
            str(vtx_b_reco.outputHitCollection),
            str(vtx_ec_reco.outputHitCollection),
            str(gem_ec_reco.outputHitCollection) ],
        trackingHits="trackingHits")
algorithms.append(trk_hit_col)

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
trk_find_alg = TrackFindingAlgorithm("trk_find_alg",
        inputSourceLinks = sourcelinker.outputSourceLinks,
        inputMeasurements = sourcelinker.outputMeasurements,
        inputInitialTrackParameters = truth_trk_init.outputInitialTrackParameters,
        outputTrajectories = "trajectories")
algorithms.append(trk_find_alg)

parts_from_fit = ParticlesFromTrackFit("parts_from_fit",
        inputTrajectories = trk_find_alg.outputTrajectories,
        outputParticles = "ReconstructedParticles",
        outputTrackParameters = "outputTrackParameters")
algorithms.append(parts_from_fit)

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
mrich_digi = PhotoMultiplierDigi("mrich_digi",
        inputHitCollection="MRICHHits",
        outputHitCollection="MRICHRawHits",
        quantumEfficiency=[(a*units.eV, b) for a, b in qe_data])
algorithms.append(mrich_digi)

mrich_reco = PhotoMultiplierReco("mrich_reco",
        inputHitCollection=mrich_digi.outputHitCollection,
        outputHitCollection="MRICHRecHits")
algorithms.append(mrich_reco)

# FIXME
#mrich_cluster = PhotoRingClusters("drich_cluster",
#        inputHitCollection=pmtreco.outputHitCollection,
#        #inputTrackCollection="ReconstructedParticles",
#        outputClusterCollection="ForwardRICHClusters")

# Output
podout = PodioOutput("out", filename=output_rec)
podout.outputCommands = [
        "keep *",
        "drop *Digi",
        "keep *Reco*",
        "keep *ClusterHits",
        "keep *Clusters",
        "keep *Layers",
        "drop InitTrackParams",
        ] + [ "drop " + c for c in sim_coll]
algorithms.append(podout)

ApplicationMgr(
    TopAlg = algorithms,
    EvtSel = 'NONE',
    EvtMax   = n_events,
    ExtSvc = [podioevent,geo_service],
    OutputLevel=WARNING
 )
