from Gaudi.Configuration import *

from Configurables import ApplicationMgr, EICDataSvc, PodioOutput, GeoSvc
from GaudiKernel import SystemOfUnits as units
from GaudiKernel.SystemOfUnits import MeV, GeV, mm, cm, mrad


detector_name = "topside"
if "JUGGLER_DETECTOR" in os.environ :
  detector_name = str(os.environ["JUGGLER_DETECTOR"])

# todo add checks
input_sim_file  = str(os.environ["JUGGLER_SIM_FILE"])
output_rec_file = str(os.environ["JUGGLER_REC_FILE"])
n_events = str(os.environ["JUGGLER_N_EVENTS"])

detector_path = detector_name
if "DETECTOR_PATH" in os.environ :
    detector_path = str(os.environ["DETECTOR_PATH"])

# get sampling fractions from system environment variable, 1.0 by default
ci_ecal_sf = float(os.environ.get("CI_ECAL_SAMP_FRAC", 0.253))
cb_ecal_sf = float(os.environ.get("CB_ECAL_SAMP_FRAC", 0.01324))
cb_hcal_sf = float(os.environ.get("CB_HCAL_SAMP_FRAC", 0.038))
ci_hcal_sf = float(os.environ.get("CI_HCAL_SAMP_FRAC", 0.025))
ce_hcal_sf = float(os.environ.get("CE_HCAL_SAMP_FRAC", 0.025))
scifi_barrel_sf = float(os.environ.get("CB_EMCAL_SCFI_SAMP_FRAC",0.0938))


geo_service  = GeoSvc("GeoSvc",
        detectors=["{}/{}.xml".format(detector_path, detector_name)])
podioevent   = EICDataSvc("EventDataSvc", inputs=[input_sim_file], OutputLevel=DEBUG)

from Configurables import PodioInput
from Configurables import Jug__Base__InputCopier_dd4pod__Geant4ParticleCollection_dd4pod__Geant4ParticleCollection_ as MCCopier
from Configurables import Jug__Base__InputCopier_dd4pod__CalorimeterHitCollection_dd4pod__CalorimeterHitCollection_ as CalCopier
from Configurables import Jug__Base__InputCopier_dd4pod__TrackerHitCollection_dd4pod__TrackerHitCollection_ as TrkCopier

from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

from Configurables import Jug__Base__MC2DummyParticle as MC2DummyParticle

from Configurables import Jug__Reco__TrackerHitReconstruction as TrackerHitReconstruction

from Configurables import Jug__Reco__TrackerSourceLinker as TrackerSourceLinker
from Configurables import Jug__Reco__Tracker2SourceLinker as Tracker2SourceLinker
#from Configurables import Jug__Reco__TrackerSourcesLinker as TrackerSourcesLinker
#from Configurables import Jug__Reco__TrackingHitsSourceLinker as TrackingHitsSourceLinker
from Configurables import Jug__Reco__TrackParamTruthInit as TrackParamTruthInit
from Configurables import Jug__Reco__TrackParamClusterInit as TrackParamClusterInit
from Configurables import Jug__Reco__TrackParamVertexClusterInit as TrackParamVertexClusterInit

from Configurables import Jug__Reco__TrackFindingAlgorithm as TrackFindingAlgorithm
from Configurables import Jug__Reco__ParticlesFromTrackFit as ParticlesFromTrackFit

from Configurables import Jug__Digi__EMCalorimeterDigi as EMCalorimeterDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Reco__EMCalReconstruction as EMCalReconstruction
from Configurables import Jug__Reco__CalorimeterHitReco as CalHitReco
from Configurables import Jug__Reco__CalorimeterIslandCluster as IslandCluster
from Configurables import Jug__Reco__ClusterRecoCoG as RecoCoG
from Configurables import Jug__Reco__CalorimeterHitsMerger as CalHitsMerger
from Configurables import Jug__Reco__ImagingPixelReco as ImCalPixelReco
from Configurables import Jug__Reco__ImagingTopoCluster as ImagingCluster
from Configurables import Jug__Reco__ImagingClusterReco as ImagingClusterReco






podioinput = PodioInput("PodioReader",
        collections=["mcparticles",
            "TrackerEndcapHits","TrackerBarrelHits",
            "VertexBarrelHits","VertexEndcapHits",
            "EcalEndcapNHits", "EcalEndcapPHits",
            "EcalBarrelHits", "EcalBarrelScFiHits", 
            "HcalEndcapPHits", "HcalEndcapNHits",
            "HcalBarrelHits",
            ])#, OutputLevel=DEBUG)

dummy = MC2DummyParticle("MC2Dummy",
        inputCollection="mcparticles",
        outputCollection="DummyReconstructedParticles",
        smearing = 0.1)


## copiers to get around input --> output copy bug. Note the "2" appended to the output collection.
copier = MCCopier("MCCopier", 
        inputCollection="mcparticles", 
        outputCollection="mcparticles2") 
trkcopier = TrkCopier("TrkCopier", 
        inputCollection="TrackerBarrelHits", 
        outputCollection="TrackerBarrelHits2") 
algorithms = [podioinput,dummy, copier, trkcopier]                                                                              

# Tracker and vertex digitization
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


# Crystal Endcap Ecal
ce_ecal_daq = dict(
        dynamicRangeADC=5.*GeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=3)

ce_ecal_digi = CalHitDigi("ce_ecal_digi",
        inputHitCollection="EcalEndcapNHits",
        outputHitCollection="EcalEndcapNHitsDigi",
        energyResolutions=[0., 0.02, 0.],
        **ce_ecal_daq)
algorithms.append(ce_ecal_digi)

ce_ecal_reco = CalHitReco("ce_ecal_reco",
        inputHitCollection=ce_ecal_digi.outputHitCollection,
        outputHitCollection="EcalEndcapNHitsReco",
        thresholdFactor=4,          # 4 sigma cut on pedestal sigma
        readoutClass="EcalEndcapNHits",
        sectorField="sector",
        **ce_ecal_daq)
algorithms.append(ce_ecal_reco)

ce_ecal_cl = IslandCluster("ce_ecal_cl",
        # OutputLevel=DEBUG,
        inputHitCollection=ce_ecal_reco.outputHitCollection,
        outputProtoClusterCollection="EcalEndcapNProtoClusters",
        splitCluster=False,
        minClusterHitEdep=1.0*MeV,  # discard low energy hits
        minClusterCenterEdep=30*MeV,
        sectorDist=5.0*cm,
        dimScaledLocalDistXY=[1.8, 1.8])          # dimension scaled dist is good for hybrid sectors with different module size
algorithms.append(ce_ecal_cl)

ce_ecal_clreco = RecoCoG("ce_ecal_clreco",
        inputHitCollection=ce_ecal_cl.inputHitCollection,
        inputProtoClusterCollection=ce_ecal_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalEndcapNClusters",
        outputInfoCollection="EcalEndcapNClustersInfo",
        samplingFraction=0.998,      # this accounts for a small fraction of leakage
        logWeightBase=4.6)
algorithms.append(ce_ecal_clreco)

# Endcap Sampling Ecal
ci_ecal_daq = dict(
        dynamicRangeADC=50.*MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

ci_ecal_digi = CalHitDigi("ci_ecal_digi",
        inputHitCollection="EcalEndcapPHits",
        outputHitCollection="EcalEndcapPHitsDigi",
        **ci_ecal_daq)
algorithms.append(ci_ecal_digi)

ci_ecal_reco = CalHitReco("ci_ecal_reco",
        inputHitCollection=ci_ecal_digi.outputHitCollection,
        outputHitCollection="EcalEndcapPHitsReco",
        thresholdFactor=5.0,
        **ci_ecal_daq)
algorithms.append(ci_ecal_reco)

# merge hits in different layer (projection to local x-y plane)
ci_ecal_merger = CalHitsMerger("ci_ecal_merger",
        # OutputLevel=DEBUG,
        inputHitCollection=ci_ecal_reco.outputHitCollection,
        outputHitCollection="EcalEndcapPHitsRecoXY",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0],
        readoutClass="EcalEndcapPHits")
algorithms.append(ci_ecal_merger)

ci_ecal_cl = IslandCluster("ci_ecal_cl",
        # OutputLevel=DEBUG,
        inputHitCollection=ci_ecal_merger.outputHitCollection,
        outputProtoClusterCollection="EcalEndcapProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=10.*MeV,
        localDistXY=[10*mm, 10*mm])
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
cb_ecal_daq = dict(
        dynamicRangeADC=3*MeV,
        capacityADC=8192,
        pedestalMean=400,
        pedestalSigma=20)   # about 6 keV

cb_ecal_digi = CalHitDigi("cb_ecal_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelHitsDigi",
        energyResolutions=[0., 0.02, 0.],   # 2% flat resolution
        **cb_ecal_daq)
algorithms.append(cb_ecal_digi)

cb_ecal_reco = ImCalPixelReco("cb_ecal_reco",
        inputHitCollection=cb_ecal_digi.outputHitCollection,
        outputHitCollection="EcalBarrelHitsReco",
        thresholdFactor=3,  # about 20 keV
        readoutClass="EcalBarrelHits",  # readout class
        layerField="layer",             # field to get layer id
        sectorField="module",           # field to get sector id
        **cb_ecal_daq)
algorithms.append(cb_ecal_reco)

cb_ecal_cl = ImagingCluster("cb_ecal_cl",
        inputHitCollection=cb_ecal_reco.outputHitCollection,
        outputProtoClusterCollection="EcalBarrelProtoClusters",
        localDistXY=[2.*mm, 2*mm],              # same layer
        layerDistEtaPhi=[10*mrad, 10*mrad],     # adjacent layer
        neighbourLayersRange=2,                 # id diff for adjacent layer
        sectorDist=3.*cm)                       # different sector
algorithms.append(cb_ecal_cl)

cb_ecal_clreco = ImagingClusterReco("cb_ecal_clreco",
        samplingFraction=cb_ecal_sf,
        inputHitCollection=cb_ecal_cl.inputHitCollection,
        inputProtoClusterCollection=cb_ecal_cl.outputProtoClusterCollection,
        outputClusterCollection="EcalBarrelClusters",
        outputInfoCollection="EcalBarrelClustersInfo",
        outputLayerCollection="EcalBarrelLayers")
algorithms.append(cb_ecal_clreco)

#Central ECAL SciFi
# use the same daq_setting for digi/reco pair
scfi_barrel_daq = dict(
        dynamicRangeADC=50.*MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

scfi_barrel_digi = CalHitDigi("scfi_barrel_digi",
        inputHitCollection="EcalBarrelScFiHits",
        outputHitCollection="EcalBarrelScFiHitsDigi",
        **scfi_barrel_daq)
algorithms.append(scfi_barrel_digi)

scfi_barrel_reco = CalHitReco("scfi_barrel_reco",
        inputHitCollection=scfi_barrel_digi.outputHitCollection,
        outputHitCollection="EcalBarrelScFiHitsReco",
        thresholdFactor=5.0,
        readoutClass="EcalBarrelScFiHits",
        layerField="layer",
        sectorField="module",
        localDetFields=["system", "module"], # use local coordinates in each module (stave)
        **scfi_barrel_daq)
algorithms.append(scfi_barrel_reco)

# merge hits in different layer (projection to local x-y plane)
scfi_barrel_merger = CalHitsMerger("scfi_barrel_merger",
        # OutputLevel=DEBUG,
        inputHitCollection=scfi_barrel_reco.outputHitCollection,
        outputHitCollection="EcalBarrelScFiGridReco",
        fields=["fiber"],
        fieldRefNumbers=[1],
        readoutClass="EcalBarrelScFiHits")
algorithms.append(scfi_barrel_merger)

scfi_barrel_cl = IslandCluster("scfi_barrel_cl",
        # OutputLevel=DEBUG,
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
         dynamicRangeADC=50.*MeV,
         capacityADC=32768,
         pedestalMean=400,
         pedestalSigma=10)

cb_hcal_digi = CalHitDigi("cb_hcal_digi",
         inputHitCollection="HcalBarrelHits",
         outputHitCollection="HcalBarrelHitsDigi",
         **cb_hcal_daq)
algorithms.append(cb_hcal_digi)

cb_hcal_reco = CalHitReco("cb_hcal_reco",
        inputHitCollection=cb_hcal_digi.outputHitCollection,
        outputHitCollection="HcalBarrelHitsReco",
        thresholdFactor=5.0,
        readoutClass="HcalBarrelHits",
        layerField="layer",
        sectorField="module",
        **cb_hcal_daq)
algorithms.append(cb_hcal_reco)

cb_hcal_merger = CalHitsMerger("cb_hcal_merger",
        inputHitCollection=cb_hcal_reco.outputHitCollection,
        outputHitCollection="HcalBarrelHitsRecoXY",
        readoutClass="HcalBarrelHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(cb_hcal_merger)

cb_hcal_cl = IslandCluster("cb_hcal_cl",
        inputHitCollection=cb_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalBarrelProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*MeV,
        localDistXY=[15.*cm, 15.*cm])
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
         dynamicRangeADC=50.*MeV,
         capacityADC=32768,
         pedestalMean=400,
         pedestalSigma=10)
ci_hcal_digi = CalHitDigi("ci_hcal_digi",
         inputHitCollection="HcalEndcapPHits",
         outputHitCollection="HcalEndcapPHitsDigi",
         **ci_hcal_daq)
algorithms.append(ci_hcal_digi)

ci_hcal_reco = CalHitReco("ci_hcal_reco",
        inputHitCollection=ci_hcal_digi.outputHitCollection,
        outputHitCollection="HcalEndcapPHitsReco",
        thresholdFactor=5.0,
        **ci_hcal_daq)
algorithms.append(ci_hcal_reco)

ci_hcal_merger = CalHitsMerger("ci_hcal_merger",
        inputHitCollection=ci_hcal_reco.outputHitCollection,
        outputHitCollection="HcalEndcapPHitsRecoXY",
        readoutClass="HcalEndcapPHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(ci_hcal_merger)

ci_hcal_cl = IslandCluster("ci_hcal_cl",
        inputHitCollection=ci_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalEndcapPProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*MeV,
        localDistXY=[15.*cm, 15.*cm])
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
        dynamicRangeADC=50.*MeV,
        capacityADC=32768,
        pedestalMean=400,
        pedestalSigma=10)

ce_hcal_digi = CalHitDigi("ce_hcal_digi",
        inputHitCollection="HcalEndcapNHits",
        outputHitCollection="HcalEndcapNHitsDigi",
        **ce_hcal_daq)
algorithms.append(ce_hcal_digi)

ce_hcal_reco = CalHitReco("ce_hcal_reco",
        inputHitCollection=ce_hcal_digi.outputHitCollection,
        outputHitCollection="HcalEndcapNHitsReco",
        thresholdFactor=5.0,
        **ce_hcal_daq)
algorithms.append(ce_hcal_reco)

ce_hcal_merger = CalHitsMerger("ce_hcal_merger",
        inputHitCollection=ce_hcal_reco.outputHitCollection,
        outputHitCollection="HcalEndcapNHitsRecoXY",
        readoutClass="HcalEndcapNHits",
        fields=["layer", "slice"],
        fieldRefNumbers=[1, 0])
algorithms.append(ce_hcal_merger)

ce_hcal_cl = IslandCluster("ce_hcal_cl",
        inputHitCollection=ce_hcal_merger.outputHitCollection,
        outputProtoClusterCollection="HcalEndcapNProtoClusters",
        splitCluster=False,
        minClusterCenterEdep=30.*MeV,
        localDistXY=[15.*cm, 15.*cm])
algorithms.append(ce_hcal_cl)

ce_hcal_clreco = RecoCoG("ce_hcal_clreco",
        inputHitCollection=ce_hcal_cl.inputHitCollection,
        inputProtoClusterCollection=ce_hcal_cl.outputProtoClusterCollection,
        outputClusterCollection="HcalEndcapNClusters",
        outputInfoCollection="HcalEndcapNClustersInfo",
        logWeightBase=6.2,
        samplingFraction=ce_hcal_sf)
algorithms.append(ce_hcal_clreco)

# Track Source linker 
sourcelinker = TrackerSourceLinker("trk_srclinker",
        inputHitCollection="TrackerBarrelRecHits",
        outputSourceLinks="BarrelTrackSourceLinks",
        OutputLevel=DEBUG)
algorithms.append(sourcelinker)

trk_hits_srclnkr = Tracker2SourceLinker("trk_hits_srclnkr",
        TrackerBarrelHits="TrackerBarrelRecHits",
        TrackerEndcapHits="TrackerEndcapRecHits",
        outputMeasurements="lnker2Measurements",
        outputSourceLinks="lnker2Links",
        allTrackerHits="linker2AllHits",
        OutputLevel=DEBUG)
algorithms.append(trk_hits_srclnkr)

## Track param init
truth_trk_init = TrackParamTruthInit("truth_trk_init",
        inputMCParticles="mcparticles",
        outputInitialTrackParameters="InitTrackParams",
        OutputLevel=DEBUG)
algorithms.append(truth_trk_init)

#clust_trk_init = TrackParamClusterInit("clust_trk_init",
#        inputClusters="SimpleClusters",
#        outputInitialTrackParameters="InitTrackParamsFromClusters",
#        OutputLevel=DEBUG)
#algorithms.append(clust_trk_init)

#vtxcluster_trk_init = TrackParamVertexClusterInit("vtxcluster_trk_init",
#        inputVertexHits="VertexBarrelRecHits",
#        inputClusters="SimpleClusters",
#        outputInitialTrackParameters="InitTrackParamsFromVtxClusters",
#        maxHitRadius=40.0*units.mm,
#        OutputLevel=DEBUG)

# Tracking algorithms
trk_find_alg = TrackFindingAlgorithm("trk_find_alg",
        inputSourceLinks = sourcelinker.outputSourceLinks,
        inputMeasurements = sourcelinker.outputMeasurements,
        inputInitialTrackParameters= "InitTrackParams",#"InitTrackParamsFromClusters", 
        outputTrajectories="trajectories",
        OutputLevel=DEBUG)
algorithms.append(trk_find_alg)

parts_from_fit = ParticlesFromTrackFit("parts_from_fit",
        inputTrajectories="trajectories",
        outputParticles="ReconstructedParticles",
        outputTrackParameters="outputTrackParameters",
        OutputLevel=DEBUG)
algorithms.append(parts_from_fit)

#trk_find_alg1 = TrackFindingAlgorithm("trk_find_alg1",
#        inputSourceLinks = trk_hits_srclnkr.outputSourceLinks,
#        inputMeasurements = trk_hits_srclnkr.outputMeasurements,
#        inputInitialTrackParameters= "InitTrackParamsFromClusters", 
#        outputTrajectories="trajectories1",
#        OutputLevel=DEBUG)
#parts_from_fit1 = ParticlesFromTrackFit("parts_from_fit1",
#        inputTrajectories="trajectories1",
#        outputParticles="ReconstructedParticles1",
#        outputTrackParameters="outputTrackParameters1",
#        OutputLevel=DEBUG)
#
#trk_find_alg2 = TrackFindingAlgorithm("trk_find_alg2",
#        inputSourceLinks = trk_hits_srclnkr.outputSourceLinks,
#        inputMeasurements = trk_hits_srclnkr.outputMeasurements,
#        inputInitialTrackParameters= "InitTrackParams",#"InitTrackParamsFromClusters", 
#        #inputInitialTrackParameters= "InitTrackParamsFromVtxClusters", 
#        outputTrajectories="trajectories2",
#        OutputLevel=DEBUG)
#parts_from_fit2 = ParticlesFromTrackFit("parts_from_fit2",
#        inputTrajectories="trajectories2",
#        outputParticles="ReconstructedParticles2",
#        outputTrackParameters="outputTrackParameters2",
#        OutputLevel=DEBUG)


#types = []
## this printout is useful to check that the type information is passed to python correctly
#print("---------------------------------------\n")
#print("---\n# List of input and output types by class")
#for configurable in sorted([ PodioInput, EICDataSvc, PodioOutput,
#                             TrackerHitReconstruction,ExampleCaloDigi, 
#                             UFSDTrackerDigi, TrackerSourceLinker,
#                             PodioOutput],
#                           key=lambda c: c.getType()):
#    print("\"{}\":".format(configurable.getType()))
#    props = configurable.getDefaultProperties()
#    for propname, prop in sorted(props.items()):
#        print(" prop name: {}".format(propname))
#        if isinstance(prop, DataHandleBase):
#            types.append(prop.type())
#            print("  {}: \"{}\"".format(propname, prop.type()))
#print("---")

out = PodioOutput("out", filename=output_rec_file)
out.outputCommands = ["keep *", 
        "drop BarrelTrackSourceLinks", 
        "drop InitTrackParams",
        "drop trajectories",
        "drop outputSourceLinks",
        "drop outputInitialTrackParameters",
        "drop mcparticles"
        ]
algorithms.append(out)

ApplicationMgr(
    TopAlg = algorithms,
    EvtSel = 'NONE',
    EvtMax   = n_events,
    ExtSvc = [podioevent,geo_service],
    OutputLevel=DEBUG
 )


