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
# auditor service
services.append(AuditorSvc("AuditorSvc", Auditors=['ChronoAuditor', 'MemStatAuditor']))
# geometry service
services.append(GeoSvc("GeoSvc", detectors=["{}.xml".format(compact_path)], OutputLevel=WARNING))
# data service
services.append(EICDataSvc("EventDataSvc", inputs=input_sims, OutputLevel=WARNING))

# juggler components
from Configurables import PodioInput

from Configurables import Jug__Digi__SimTrackerHitsCollector as SimTrackerHitsCollector
from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

# branches needed from simulation root file
sim_coll = [
    'MCParticles',
    'B0TrackerHits',
    'EcalEndcapNHits',
    'EcalEndcapNHitsContributions',
    'EcalEndcapPHits',
    'EcalEndcapPHitsContributions',
    'EcalBarrelHits',
    'EcalBarrelHitsContributions',
    'EcalBarrelScFiHits',
    'EcalBarrelScFiHitsContributions',
    'HcalBarrelHits',
    'HcalBarrelHitsContributions',
    'HcalEndcapPHits',
    'HcalEndcapPHitsContributions',
    'HcalEndcapNHits',
    'HcalEndcapNHitsContributions',
    'DRICHHits',
]

forward_romanpot_collections = [
    'ForwardRomanPotHits1',
    'ForwardRomanPotHits2'
]
forward_offmtracker_collections = [
    'ForwardOffMTrackerHits1',
    'ForwardOffMTrackerHits2',
    'ForwardOffMTrackerHits3',
    'ForwardOffMTrackerHits4'
]
sim_coll += forward_romanpot_collections + forward_offmtracker_collections

tracker_endcap_collections = [
    'TrackerEndcapHits1',
    'TrackerEndcapHits2',
    'TrackerEndcapHits3',
    'TrackerEndcapHits4',
    'TrackerEndcapHits5',
    'TrackerEndcapHits6'
]
tracker_barrel_collections = [
    'TrackerBarrelHits'
]
vertex_barrel_collections = [
    'VertexBarrelHits'
]
gem_endcap_collections = [
    'GEMTrackerEndcapHits1',
    'GEMTrackerEndcapHits2',
    'GEMTrackerEndcapHits3'
]
sim_coll += tracker_endcap_collections + tracker_barrel_collections + vertex_barrel_collections + gem_endcap_collections


vertex_endcap_collections = [
    'VertexEndcapHits'
]
mpgd_barrel_collections = [
    'MPGDTrackerBarrelHits1',
    'MPGDTrackerBarrelHits2'
]

if 'acadia' in detector_version:
    sim_coll += vertex_endcap_collections
    sim_coll.append('MRICHHits')
else:
    sim_coll += mpgd_barrel_collections

# list of algorithms
algorithms = []

# input
podin = PodioInput("PodioReader", collections=sim_coll)
algorithms.append(podin)

## Roman pots
ffi_romanpot_coll = SimTrackerHitsCollector("ffi_romanpot_coll",
        inputSimTrackerHits = forward_romanpot_collections,
        outputSimTrackerHits = "ForwardRomanPotAllHits")
algorithms.append(ffi_romanpot_coll)
ffi_romanpot_digi = TrackerDigi("ffi_romanpot_digi",
        inputHitCollection = ffi_romanpot_coll.outputSimTrackerHits,
        outputHitCollection = "ForwardRomanPotRawHits",
        timeResolution = 8)
algorithms.append(ffi_romanpot_digi)

## Off momentum tracker
ffi_offmtracker_coll = SimTrackerHitsCollector("ffi_offmtracker_coll",
        inputSimTrackerHits = forward_offmtracker_collections,
        outputSimTrackerHits = "ForwardOffMTrackerAllHits")
algorithms.append(ffi_offmtracker_coll)
ffi_offmtracker_digi = TrackerDigi("ffi_offmtracker_digi",
        inputHitCollection = ffi_offmtracker_coll.outputSimTrackerHits,
        outputHitCollection = "ForwardOffMTrackerRawHits",
        timeResolution = 8)
algorithms.append(ffi_offmtracker_digi)

## B0 tracker
trk_b0_digi = TrackerDigi("trk_b0_digi",
        inputHitCollection="B0TrackerHits",
        outputHitCollection="B0TrackerRawHits",
        timeResolution=8)
algorithms.append(trk_b0_digi)

# Crystal Endcap Ecal
ce_ecal_daq = calo_daq['ecal_neg_endcap']

ce_ecal_digi = CalHitDigi("ce_ecal_digi",
        inputHitCollection="EcalEndcapNHits",
        outputHitCollection="EcalEndcapNRawHits",
        energyResolutions=[0., 0.02, 0.],
        **ce_ecal_daq)
algorithms.append(ce_ecal_digi)

# Endcap Sampling Ecal
ci_ecal_daq = calo_daq['ecal_pos_endcap']

ci_ecal_digi = CalHitDigi("ci_ecal_digi",
        inputHitCollection="EcalEndcapPHits",
        outputHitCollection="EcalEndcapPRawHits",
        **ci_ecal_daq)
algorithms.append(ci_ecal_digi)

# Central Barrel Ecal (Imaging Cal.)
img_barrel_daq = calo_daq['ecal_barrel_imaging']

img_barrel_digi = CalHitDigi("img_barrel_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelImagingRawHits",
        energyResolutions=[0., 0.02, 0.],   # 2% flat resolution
        **img_barrel_daq)
algorithms.append(img_barrel_digi)

# Central ECAL SciFi
scfi_barrel_daq = calo_daq['ecal_barrel_scfi']

scfi_barrel_digi = CalHitDigi("scfi_barrel_digi",
        inputHitCollection="EcalBarrelScFiHits",
        outputHitCollection="EcalBarrelScFiRawHits",
        **scfi_barrel_daq)
algorithms.append(scfi_barrel_digi)

# Central Barrel Hcal
cb_hcal_daq = calo_daq['hcal_barrel']

cb_hcal_digi = CalHitDigi("cb_hcal_digi",
         inputHitCollection="HcalBarrelHits",
         outputHitCollection="HcalBarrelRawHits",
         **cb_hcal_daq)
algorithms.append(cb_hcal_digi)

# Hcal Hadron Endcap
ci_hcal_daq = calo_daq['hcal_pos_endcap']

ci_hcal_digi = CalHitDigi("ci_hcal_digi",
         inputHitCollection="HcalEndcapPHits",
         outputHitCollection="HcalEndcapPRawHits",
         **ci_hcal_daq)
algorithms.append(ci_hcal_digi)

# Hcal Electron Endcap
ce_hcal_daq = calo_daq['hcal_neg_endcap']

ce_hcal_digi = CalHitDigi("ce_hcal_digi",
        inputHitCollection="HcalEndcapNHits",
        outputHitCollection="HcalEndcapNRawHits",
        **ce_hcal_daq)
algorithms.append(ce_hcal_digi)

# Tracking
trk_b_coll = SimTrackerHitsCollector("trk_b_coll",
        inputSimTrackerHits = tracker_barrel_collections,
        outputSimTrackerHits = "TrackerBarrelAllHits")
algorithms.append( trk_b_coll )

trk_b_digi = TrackerDigi("trk_b_digi",
        inputHitCollection = trk_b_coll.outputSimTrackerHits,
        outputHitCollection = "TrackerBarrelRawHits",
        timeResolution=8)
algorithms.append(trk_b_digi)

trk_ec_coll = SimTrackerHitsCollector("trk_ec_coll",
        inputSimTrackerHits = tracker_endcap_collections,
        outputSimTrackerHits = "TrackerEndcapAllHits")
algorithms.append( trk_ec_coll )

trk_ec_digi = TrackerDigi("trk_ec_digi",
        inputHitCollection = trk_ec_coll.outputSimTrackerHits,
        outputHitCollection = "TrackerEndcapRawHits",
        timeResolution=8)
algorithms.append(trk_ec_digi)

vtx_b_coll = SimTrackerHitsCollector("vtx_b_coll",
        inputSimTrackerHits = vertex_barrel_collections,
        outputSimTrackerHits = "VertexBarrelAllHits")
algorithms.append( vtx_b_coll )

vtx_b_digi = TrackerDigi("vtx_b_digi",
        inputHitCollection = vtx_b_coll.outputSimTrackerHits,
        outputHitCollection = "VertexBarrelRawHits",
        timeResolution=8)
algorithms.append(vtx_b_digi)

if 'acadia' in detector_version:
    vtx_ec_coll = SimTrackerHitsCollector("vtx_ec_coll",
            inputSimTrackerHits = vertex_endcap_collections,
            outputSimTrackerHits = "VertexEndcapAllHits")
    algorithms.append( vtx_ec_coll )

    vtx_ec_digi = TrackerDigi("vtx_ec_digi", 
            inputHitCollection = vtx_ec_coll.outputSimTrackerHits,
            outputHitCollection = "VertexEndcapRawHits",
            timeResolution=8)
    algorithms.append( vtx_ec_digi )
else:
    mm_b_coll = SimTrackerHitsCollector("mm_b_coll",
            inputSimTrackerHits = mpgd_barrel_collections,
            outputSimTrackerHits = "MPGDTrackerBarrelAllHits")
    algorithms.append( mm_b_coll )

    mm_b_digi = TrackerDigi("mm_b_digi", 
            inputHitCollection = mm_b_coll.outputSimTrackerHits,
            outputHitCollection = "MPGDTrackerBarrelRawHits",
            timeResolution=8)
    algorithms.append( mm_b_digi )

gem_ec_coll = SimTrackerHitsCollector("gem_ec_coll",
        inputSimTrackerHits = gem_endcap_collections,
        outputSimTrackerHits = "GEMTrackerEndcapAllHits")
algorithms.append( gem_ec_coll )

gem_ec_digi = TrackerDigi("gem_ec_digi",
        inputHitCollection = gem_ec_coll.outputSimTrackerHits,
        outputHitCollection = "GEMTrackerEndcapRawHits",
        timeResolution=10)
algorithms.append( gem_ec_digi )

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
