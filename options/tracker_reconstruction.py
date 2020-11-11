from Gaudi.Configuration import *

from GaudiKernel.DataObjectHandleBase import DataObjectHandleBase
from Configurables import ApplicationMgr, EICDataSvc, PodioOutput, GeoSvc
from GaudiKernel import SystemOfUnits as units

detector_name = "topside"
if "JUGGLER_DETECTOR" in os.environ :
  detector_name = str(os.environ["JUGGLER_DETECTOR"])

# todo add checks
input_sim_file  = str(os.environ["JUGGLER_SIM_FILE"])
output_rec_file = str(os.environ["JUGGLER_REC_FILE"])
n_events = str(os.environ["JUGGLER_N_EVENTS"])

geo_service  = GeoSvc("GeoSvc", detectors=["{}.xml".format(detector_name)])
podioevent   = EICDataSvc("EventDataSvc", inputs=[input_sim_file], OutputLevel=DEBUG)

from Configurables import PodioInput
from Configurables import Jug__Base__InputCopier_dd4pod__Geant4ParticleCollection_dd4pod__Geant4ParticleCollection_ as MCCopier
from Configurables import Jug__Base__InputCopier_dd4pod__CalorimeterHitCollection_dd4pod__CalorimeterHitCollection_ as CalCopier
from Configurables import Jug__Base__InputCopier_dd4pod__TrackerHitCollection_dd4pod__TrackerHitCollection_ as TrkCopier

from Configurables import Jug__Digi__ExampleCaloDigi as ExampleCaloDigi
from Configurables import Jug__Digi__UFSDTrackerDigi as UFSDTrackerDigi
from Configurables import Jug__Digi__EMCalorimeterDigi as EMCalorimeterDigi

from Configurables import Jug__Reco__TrackerHitReconstruction as TrackerHitReconstruction

from Configurables import Jug__Reco__TrackerSourceLinker as TrackerSourceLinker
from Configurables import Jug__Reco__TrackingHitsSourceLinker as TrackingHitsSourceLinker
from Configurables import Jug__Reco__TrackParamTruthInit as TrackParamTruthInit
from Configurables import Jug__Reco__TrackParamClusterInit as TrackParamClusterInit
from Configurables import Jug__Reco__TrackParamVertexClusterInit as TrackParamVertexClusterInit

from Configurables import Jug__Reco__TrackFindingAlgorithm as TrackFindingAlgorithm
from Configurables import Jug__Reco__ParticlesFromTrackFit as ParticlesFromTrackFit
from Configurables import Jug__Reco__EMCalReconstruction as EMCalReconstruction

from Configurables import Jug__Reco__SimpleClustering as SimpleClustering



podioinput = PodioInput("PodioReader", 
                        collections=["mcparticles","SiTrackerBarrelHits","SiVertexBarrelHits","EcalBarrelHits"])#, OutputLevel=DEBUG)

## copiers to get around input --> output copy bug. Note the "2" appended to the output collection.
copier = MCCopier("MCCopier", 
        inputCollection="mcparticles", 
        outputCollection="mcparticles2") 
trkcopier = TrkCopier("TrkCopier", 
        inputCollection="SiTrackerBarrelHits", 
        outputCollection="SiTrackerBarrelHits2") 

ecal_digi = EMCalorimeterDigi("ecal_digi", 
        inputHitCollection="EcalBarrelHits", 
        outputHitCollection="RawEcalBarrelHits")

ufsd_digi = UFSDTrackerDigi("ufsd_digi", 
        inputHitCollection="SiTrackerBarrelHits",
        outputHitCollection="SiTrackerBarrelRawHits",
        timeResolution=8)

vtx_digi = UFSDTrackerDigi("vtx_digi", 
        inputHitCollection="SiVertexBarrelHits",
        outputHitCollection="SiVertexBarrelRawHits",
        timeResolution=8)


ecal_reco = EMCalReconstruction("ecal_reco", 
        inputHitCollection="RawEcalBarrelHits", 
        outputHitCollection="RecEcalBarrelHits",
        minModuleEdep=0.0*units.MeV,
        OutputLevel=DEBUG)

simple_cluster = SimpleClustering("simple_cluster", 
        inputHitCollection="RecEcalBarrelHits", 
        outputClusters="SimpleClusters",
        minModuleEdep=1.0*units.MeV,
        maxDistance=50.0*units.cm,
        OutputLevel=DEBUG)

trk_barrel_reco = TrackerHitReconstruction("trk_barrel_reco",
        inputHitCollection="SiTrackerBarrelRawHits",
        outputHitCollection="TrackerBarrelRecHits")

vtx_barrel_reco = TrackerHitReconstruction("vtx_barrel_reco",
        inputHitCollection = vtx_digi.outputHitCollection,
        outputHitCollection="VertexBarrelRecHits")

# Source linker 
sourcelinker = TrackerSourceLinker("trk_srclinker",
        inputHitCollection="TrackerBarrelRecHits",
        outputSourceLinks="BarrelTrackSourceLinks",
        OutputLevel=DEBUG)

trk_hits_srclnkr = TrackingHitsSourceLinker("trk_hits_srclnkr",
        inputTrackerCollections=["TrackerBarrelRecHits","VertexBarrelRecHits"],
        outputSourceLinks="BarrelSourceLinks",
        OutputLevel=DEBUG)

## Track param init
truth_trk_init = TrackParamTruthInit("truth_trk_init",
        inputMCParticles="mcparticles",
        outputInitialTrackParameters="InitTrackParams",
        OutputLevel=DEBUG)

clust_trk_init = TrackParamClusterInit("clust_trk_init",
        inputClusters="SimpleClusters",
        outputInitialTrackParameters="InitTrackParamsFromClusters",
        OutputLevel=DEBUG)

vtxcluster_trk_init = TrackParamVertexClusterInit("vtxcluster_trk_init",
        inputVertexHits="VertexBarrelRecHits",
        inputClusters="SimpleClusters",
        outputInitialTrackParameters="InitTrackParamsFromVtxClusters",
        maxHitRadius=40.0*units.mm,
        OutputLevel=DEBUG)

# Tracking algorithms
trk_find_alg = TrackFindingAlgorithm("trk_find_alg",
        inputSourceLinks="BarrelSourceLinks",
        inputInitialTrackParameters= "InitTrackParams",#"InitTrackParamsFromClusters", 
        outputTrajectories="trajectories",
        OutputLevel=DEBUG)
parts_from_fit = ParticlesFromTrackFit("parts_from_fit",
        inputTrajectories="trajectories",
        outputParticles="ReconstructedParticles",
        outputTrackParameters="outputTrackParameters",
        OutputLevel=DEBUG)

trk_find_alg1 = TrackFindingAlgorithm("trk_find_alg1",
        inputSourceLinks="BarrelSourceLinks",
        inputInitialTrackParameters= "InitTrackParamsFromClusters", 
        outputTrajectories="trajectories1",
        OutputLevel=DEBUG)
parts_from_fit1 = ParticlesFromTrackFit("parts_from_fit1",
        inputTrajectories="trajectories1",
        outputParticles="ReconstructedParticles1",
        outputTrackParameters="outputTrackParameters1",
        OutputLevel=DEBUG)

trk_find_alg2 = TrackFindingAlgorithm("trk_find_alg2",
        inputSourceLinks="BarrelSourceLinks",
        inputInitialTrackParameters= "InitTrackParamsFromVtxClusters", 
        outputTrajectories="trajectories2",
        OutputLevel=DEBUG)
parts_from_fit2 = ParticlesFromTrackFit("parts_from_fit2",
        inputTrajectories="trajectories2",
        outputParticles="ReconstructedParticles2",
        outputTrackParameters="outputTrackParameters2",
        OutputLevel=DEBUG)


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
#        if isinstance(prop, DataObjectHandleBase):
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

ApplicationMgr(
    TopAlg = [podioinput, 
              copier, trkcopier,
              ecal_digi, ufsd_digi, vtx_digi, 
              ecal_reco, 
              simple_cluster,
              trk_barrel_reco, 
              vtx_barrel_reco, 
              sourcelinker, trk_hits_srclnkr,
              clust_trk_init, 
              truth_trk_init, 
              vtxcluster_trk_init, 
              trk_find_alg, parts_from_fit,
              trk_find_alg1, parts_from_fit1,
              trk_find_alg2, parts_from_fit2,
              out
              ],
    EvtSel = 'NONE',
    EvtMax   = n_events,
    ExtSvc = [podioevent,geo_service],
    OutputLevel=DEBUG
 )

