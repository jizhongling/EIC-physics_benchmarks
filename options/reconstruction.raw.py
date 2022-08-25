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
if "athena" in detector_name:
    has_ecal_barrel_scfi = True
if "ecce" in detector_name and "imaging" in detector_config:
    has_ecal_barrel_scfi = True
if "epic" in detector_name and "imaging" in detector_config:
    has_ecal_barrel_scfi = True

# RICH reconstruction
qe_data = [
    (1.0, 0.25),
    (7.5, 0.25),
]

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
# auditor service
services.append(AuditorSvc("AuditorSvc", Auditors=["ChronoAuditor", "MemStatAuditor"]))
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

from Configurables import Jug__Digi__SimTrackerHitsCollector as SimTrackerHitsCollector
from Configurables import Jug__Digi__PhotoMultiplierDigi as PhotoMultiplierDigi
from Configurables import Jug__Digi__CalorimeterHitDigi as CalHitDigi
from Configurables import Jug__Digi__SiliconTrackerDigi as TrackerDigi

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

## B0 tracker
trk_b0_digi = TrackerDigi(
    "trk_b0_digi",
    inputHitCollection="B0TrackerHits",
    outputHitCollection="B0TrackerRawHits",
    timeResolution=8,
)
algorithms.append(trk_b0_digi)

# Crystal Endcap Ecal
ce_ecal_daq = calo_daq["ecal_neg_endcap"]

ce_ecal_digi = CalHitDigi(
    "ce_ecal_digi",
    inputHitCollection="EcalEndcapNHits",
    outputHitCollection="EcalEndcapNRawHits",
    energyResolutions=[0.0, 0.02, 0.0],
    **ce_ecal_daq
)
algorithms.append(ce_ecal_digi)

# Endcap Sampling Ecal
ci_ecal_daq = calo_daq["ecal_pos_endcap"]

ci_ecal_digi = CalHitDigi(
    "ci_ecal_digi",
    inputHitCollection="EcalEndcapPHits",
    outputHitCollection="EcalEndcapPRawHits",
    **ci_ecal_daq
)
algorithms.append(ci_ecal_digi)

# Central Barrel Ecal
if has_ecal_barrel_scfi:
    # Central ECAL Imaging Calorimeter
    img_barrel_daq = calo_daq["ecal_barrel_imaging"]

    img_barrel_digi = CalHitDigi(
        "img_barrel_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelImagingRawHits",
        energyResolutions=[0.0, 0.02, 0.0],  # 2% flat resolution
        **img_barrel_daq
    )
    algorithms.append(img_barrel_digi)

    # Central ECAL SciFi
    scfi_barrel_daq = calo_daq["ecal_barrel_scfi"]

    scfi_barrel_digi = CalHitDigi(
        "scfi_barrel_digi",
        inputHitCollection="EcalBarrelScFiHits",
        outputHitCollection="EcalBarrelScFiRawHits",
        **scfi_barrel_daq
    )
    algorithms.append(scfi_barrel_digi)
else:
    # SciGlass calorimeter
    sciglass_ecal_daq = calo_daq["ecal_barrel_sciglass"]

    sciglass_ecal_digi = CalHitDigi(
        "sciglass_ecal_digi",
        inputHitCollection="EcalBarrelHits",
        outputHitCollection="EcalBarrelRawHits",
        energyResolutions=[0.0, 0.02, 0.0],  # 2% flat resolution
        **sciglass_ecal_daq
    )
    algorithms.append(sciglass_ecal_digi)

# Central Barrel Hcal
cb_hcal_daq = calo_daq["hcal_barrel"]

cb_hcal_digi = CalHitDigi(
    "cb_hcal_digi",
    inputHitCollection="HcalBarrelHits",
    outputHitCollection="HcalBarrelRawHits",
    **cb_hcal_daq
)
algorithms.append(cb_hcal_digi)

# Hcal Hadron Endcap
ci_hcal_daq = calo_daq["hcal_pos_endcap"]

ci_hcal_digi = CalHitDigi(
    "ci_hcal_digi",
    inputHitCollection="HcalEndcapPHits",
    outputHitCollection="HcalEndcapPRawHits",
    **ci_hcal_daq
)
algorithms.append(ci_hcal_digi)

# Hcal Electron Endcap
ce_hcal_daq = calo_daq["hcal_neg_endcap"]

ce_hcal_digi = CalHitDigi(
    "ce_hcal_digi",
    inputHitCollection="HcalEndcapNHits",
    outputHitCollection="HcalEndcapNRawHits",
    **ce_hcal_daq
)
algorithms.append(ce_hcal_digi)

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

# DRICH
drich_digi = PhotoMultiplierDigi(
    "drich_digi",
    inputHitCollection="DRICHHits",
    outputHitCollection="DRICHRawHits",
    quantumEfficiency=[(a * eV, b) for a, b in qe_data],
)
algorithms.append(drich_digi)

# MRICH
if "acadia" in detector_version:
    mrich_digi = PhotoMultiplierDigi(
        "mrich_digi",
        inputHitCollection="MRICHHits",
        outputHitCollection="MRICHRawHits",
        quantumEfficiency=[(a * eV, b) for a, b in qe_data],
    )
    algorithms.append(mrich_digi)

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
    + ["keep *RawHits"]
)
algorithms.append(podout)

ApplicationMgr(
    TopAlg=algorithms,
    EvtSel="NONE",
    EvtMax=n_events,
    ExtSvc=services,
    OutputLevel=WARNING,
    AuditAlgorithms=True,
)
