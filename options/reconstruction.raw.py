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

# input and output
input_sims = [f.strip() for f in str.split(os.environ["JUGGLER_SIM_FILE"], ",") if f.strip()]
output_rec = str(os.environ["JUGGLER_REC_FILE"])
n_events = int(os.environ["JUGGLER_N_EVENTS"])

# services
services = []
# auditor service
services.append(AuditorSvc("AuditorSvc", Auditors=['ChronoAuditor', 'MemStatAuditor']))
# geometry service
services.append(GeoSvc("GeoSvc", detectors=["{}.xml".format(compact_path)], OutputLevel=WARNING))
# data service
services.append(EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING))

# juggler components
from Configurables import PodioInput

from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

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

# DRICH
drich_digi = PhotoMultiplierDigi("drich_digi",
        inputHitCollection="DRICHHits",
        outputHitCollection="DRICHRawHits",
        quantumEfficiency=[(a*units.eV, b) for a, b in qe_data])
algorithms.append(drich_digi)

# MRICH
if 'acadia' in detector_version:
    mrich_digi = PhotoMultiplierDigi("mrich_digi",
            inputHitCollection="MRICHHits",
            outputHitCollection="MRICHRawHits",
            quantumEfficiency=[(a*units.eV, b) for a, b in qe_data])
    algorithms.append(mrich_digi)

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
        "keep *RawHits"
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
