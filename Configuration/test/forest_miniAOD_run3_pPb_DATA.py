### HiForest Configuration
# Input: miniAOD
# Type: data
# Target: pPb, W -> mu nu (muon channel)
#
# Adapted from forest_miniAOD_run3_pO_DATA.py (pO 2025).
# Everything marked "TODO(pPb)" is run-dependent and MUST be set to the
# values of the actual pPb production before submission:
#   1. Era        - 15_0_X has no pPb-specific era; using generic Run3_2025
#                   (pPb is reconstructed pp-style). Replace with the official
#                   era of the pPb prompt-reco release (check the pPb workflow
#                   in Configuration/Eras of that release).
#   2. Global tag - use the prompt GT of the pPb data-taking period.
#   3. Input file - point to the pPb muon primary dataset
#                   (2016 pPb: /PASingleMuon/PARun2016C-.../MINIAOD;
#                    naming for a new run will differ, e.g. IonPhysics* style).
#   4. Trigger list - replace with the single-muon paths of the pPb HLT menu.
#                   2016 pPb W->munu used HLT_PAL3Mu12_v. The 2025 pO run used
#                   HLT_OxyL1SingleMu* naming; a new pPb menu will have its own
#                   prefix. Verify against the actual menu before running.
#   5. Beam direction - pPb runs come in two configurations (p->Pb and Pb->p).
#                   Nothing here depends on it (lab-frame quantities are stored)
#                   but keep the two periods in separate CRAB tasks so the
#                   eta flip / CM boost (y_shift ~ 0.465) can be applied offline.

import FWCore.ParameterSet.Config as cms
# TODO(pPb): replace with the official pPb era of the production release
from Configuration.Eras.Era_Run3_2025_cff import Run3_2025
process = cms.Process('HiForest', Run3_2025)

###############################################################################

# HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 150X, data, pPb, WToMuNu")

###############################################################################

# input files
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        # TODO(pPb): replace with a file from the pPb muon primary dataset
        'root://xrootd-cms.infn.it//store/data/CHANGE_ME_pPb_MUON_PD.root'
    ),
)

# number of events to process, set to -1 to process all events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
    )

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

###############################################################################

# load Global Tag, geometry, etc.
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')


from Configuration.AlCa.GlobalTag import GlobalTag
# TODO(pPb): set the prompt GT of the pPb data-taking period
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_dataRun3_Prompt_v3', '')
process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

###############################################################################

# Define centrality binning
# NOTE(pPb): kept because hiMuons/hiElectrons (iso BDTs) consume
# centralityBin:HFtowers. Confirm that 'hiCentrality' exists in the pPb
# prompt-reco miniAOD (2016 pPb used 'pACentrality'); if absent, the
# centrality input of hiMuons/hiElectrons must be changed accordingly.
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("hiCentrality")
process.centralityBin.centralityVariable = cms.string("HFtowers")

###############################################################################

# root output
process.TFileService = cms.Service("TFileService",
    fileName = cms.string("HiForestMiniAOD.root"))

###############################################################################

# event analysis
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_data_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltobject_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.l1object_cfi')
process.metFilters = process.skimanalysis.clone(hltresults = "TriggerResults::RECO")
process.hiEvtAnalyzer.doHFfilters = False

# TODO(pPb): replace with the single-muon + minimum-bias paths of the actual
# pPb HLT menu. The names below are the 2016 pPb (8.16 TeV) reference paths;
# a new pPb menu will have different names (verify with `hltInfo` on one file
# or check the menu in ConfDB before submitting).
process.hltobject.triggerNames = cms.vstring(
    'HLT_PAL3Mu12_v',
    'HLT_PAL3Mu15_v',
    'HLT_PAL2Mu12_v',
    'HLT_PAL1DoubleMuOpen_v',
    'HLT_PAMinimumBiasHF_OR_SinglePixelTrack_v'
)

process.load('HeavyIonsAnalysis.EventAnalysis.particleFlowAnalyser_cfi')
################################
# electrons, photons, muons
# NOTE: electron chain kept (useful for lepton vetoes / cross-checks in the
# W analysis). Drop the egammaSequence below to slim the forest if only the
# muon channel is needed.
process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
process.load('HeavyIonsAnalysis.EGMAnalysis.hiElectrons_cfi')
process.load('HeavyIonsAnalysis.EGMAnalysis.correctedPatElectronProducer_cfi')
process.correctedElectrons = process.correctedPatElectronProducer.clone(src = "slimmedElectrons", centrality = "centralityBin:HFtowers")
process.correctedElectrons.correctionFile = "HeavyIonsAnalysis/EGMAnalysis/data/Run3_2024_PbPb/SSHIRun2024A.dat"
process.hiElectrons.electrons = "correctedElectrons"
process.hiElectrons.file_idModel = "HeavyIonsAnalysis/EGMAnalysis/data/Run3_2024_PbPb/eleid_BDT.ubj"
process.hiElectrons.file_isoModel = "HeavyIonsAnalysis/EGMAnalysis/data/Run3_2024_PbPb/eleiso_BDT.ubj"
process.hiElectrons.file_corr = "HeavyIonsAnalysis/Configuration/data/lepton_spectra_train_weights_Run3_2024_PbPb.json.gz"
process.hiElectrons.era = "Run3_2024_PbPb"
process.ggHiNtuplizer.electronSrc = "hiElectrons"
process.egammaSequence = cms.Sequence(process.correctedElectrons * process.hiElectrons * process.ggHiNtuplizer)
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
process.ggHiNtuplizer.doPhotons = False
################################
# jet reco sequence
# NOTE(pPb): kept identical to the pO setup (constituent-subtracted CS jets).
# For a small system the pp-style ak4PFJetSequence_ppref_data_cff is an
# alternative; rhoSequence below is needed by the muon iso BDT either way.
process.load('HeavyIonsAnalysis.JetAnalysis.akCs4PFJetSequence_pponPbPb_data_cff')
################################
# tracks
process.load("HeavyIonsAnalysis.TrackAnalysis.TrackAnalyzers_cff")
# muons
process.load('HeavyIonsAnalysis.JetAnalysis.hiFJRhoAnalyzer_cff')
process.load('HeavyIonsAnalysis.MuonAnalysis.hiMuons_cfi')
# NOTE(pPb): iso BDT trained on PbPb 2024 (same re-use as the pO setup).
# 'era' must be Run3_2023_PbPb or Run3_2024_PbPb (HIMuonMVAProducer throws
# otherwise). Validate / retrain for the pPb multiplicity environment.
process.hiMuons.file_isoModel = "HeavyIonsAnalysis/MuonAnalysis/data/Run3_2024_PbPb/muiso_BDT.ubj"
process.hiMuons.file_isoCorr = "HeavyIonsAnalysis/Configuration/data/lepton_spectra_train_weights_Run3_2024_PbPb.json.gz"
process.hiMuons.era = "Run3_2024_PbPb"
process.ggHiNtuplizer.muonSrc = "hiMuons"
process.muonSequence = cms.Sequence(process.rhoSequence * process.hiMuons)
process.load("HeavyIonsAnalysis.MuonAnalysis.muonAnalyzer_cfi")

###############################################################################
# main forest sequence
process.forest = cms.Path(
    process.HiForestInfo +
    process.centralityBin +
    process.hiEvtAnalyzer +
    process.hltanalysis +
    process.hltobject +
    process.l1object +
    process.unpackedTracksAndVertices +
    process.particleFlowAnalyser +
    process.muonSequence +
    process.egammaSequence +
    process.ggHiNtuplizer +
    process.metFilters
    )

#customisation
# PF candidates stored down to pT = 0 over |eta| < 5 so that PF MET / W mT
# can be rebuilt offline (no MET collection is stored by this forest).
process.particleFlowAnalyser.ptMin = 0.0
process.ggHiNtuplizer.muonPtMin = 0.0

#########################
# Event Selection -> add the needed filters here
#########################

process.load('HeavyIonsAnalysis.EventAnalysis.collisionEventSelection_cff')
process.pclusterCompatibilityFilter = cms.Path(process.clusterCompatibilityFilter)
process.pprimaryVertexFilter = cms.Path(process.primaryVertexFilter)
process.pAna = cms.EndPath(process.skimanalysis)

process.goodMuons = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("slimmedMuons"),
    cut = cms.string("pt >= 15.0 && passed('CutBasedIdLoose')")
)
process.goodElectrons = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("slimmedElectrons"),
    cut = cms.string("pt >= 15.0")
)
process.oneLepton = cms.EDFilter("PATLeptonCountFilter",
    electronSource = cms.InputTag("goodElectrons"),
    muonSource     = cms.InputTag("goodMuons"),
    tauSource      = cms.InputTag(""),
    countElectrons = cms.bool(True),
    countMuons     = cms.bool(True),
    countTaus      = cms.bool(False),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1000000),
)
process.leptonSelection = cms.Sequence(process.goodElectrons * process.goodMuons * process.oneLepton)
process.filterSequence = cms.Sequence(
    process.clusterCompatibilityFilter *
    process.primaryVertexFilter *
    process.leptonSelection
)

process.superFilterPath = cms.Path(process.filterSequence)
process.skimanalysis.superFilters = cms.vstring("superFilterPath")

for path in process.paths:
    if path != "superFilterPath":
        getattr(process, path)._seq = process.filterSequence * getattr(process,path)._seq
