### HiForest Configuration
# Input: miniAOD
# Type: data
# System: OO 2025 (5.36 TeV NN), W/Z lepton channels
# Adapted from forest_miniAOD_run3_pO_DATA.py (master) — same forest content,
# pO -> OO datasets/runs, electron scale from the 2025 pO Z->ee calibration.

import FWCore.ParameterSet.Config as cms
# Run3_2025_OXY is the oxygen-run era of the 2025 light-ion program and is the
# correct era for OO as well as pO (NeNe will need Run3_2025_NEON instead).
from Configuration.Eras.Era_Run3_2025_OXY_cff import Run3_2025_OXY
process = cms.Process('HiForest', Run3_2025_OXY)

###############################################################################

# HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 150X, data, OO")

###############################################################################

# input files
# TODO(OO): put a real OO file here for local tests, e.g. from
#   dasgoclient -query="file dataset=/IonPhysics0/OORun2025-PromptReco-v1/MINIAOD" | head
# (CRAB overrides this with the input dataset.)
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        'root://xrootd-cms.infn.it//store/data/OORun2025/IonPhysics0/MINIAOD/PromptReco-v1/CHANGE_ME.root'
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
# GT of the OO PromptReco, confirmed from the DAS config of
# /IonPhysics*/OORun2025-PromptReco-v1/MINIAOD (reco release CMSSW_15_0_9_patch3).
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_dataRun3_Prompt_v1', '')
process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

###############################################################################

# Define centrality binning
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

# Same Oxy HLT menu as the pO run; verify the exact version suffixes on an OO
# file with e.g. hltInfo <file.root> before large-scale submission.
process.hltobject.triggerNames = cms.vstring(
    'HLT_OxyL1SingleMu0_v',
    'HLT_OxyL1SingleMuOpen_v',
    'HLT_OxyL1SingleEG10_v',
    'HLT_OxyL1SingleEG15_v',
    'HLT_MinimumBiasHF_OR_BptxAND_v'
)

process.load('HeavyIonsAnalysis.EventAnalysis.particleFlowAnalyser_cfi')
################################
# electrons, photons, muons
process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
process.load('HeavyIonsAnalysis.EGMAnalysis.hiElectrons_cfi')
process.load('HeavyIonsAnalysis.EGMAnalysis.correctedPatElectronProducer_cfi')
process.correctedElectrons = process.correctedPatElectronProducer.clone(src = "slimmedElectrons", centrality = "centralityBin:HFtowers")
# 2025 pO Z->ee scale (data): replaces the PbPb-2024 placeholder used in the
# pO production. See EGMAnalysis/data/Run3_2025_pO/README.md for provenance;
# eleRawPt in the output tree stays uncorrected regardless.
process.correctedElectrons.correctionFile = "HeavyIonsAnalysis/EGMAnalysis/data/Run3_2025_pO/SSpORun2025.dat"
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
process.load('HeavyIonsAnalysis.JetAnalysis.akCs4PFJetSequence_pponPbPb_data_cff')
################################
# tracks
process.load("HeavyIonsAnalysis.TrackAnalysis.TrackAnalyzers_cff")
# muons
process.load('HeavyIonsAnalysis.JetAnalysis.hiFJRhoAnalyzer_cff')
process.load('HeavyIonsAnalysis.MuonAnalysis.hiMuons_cfi')
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
