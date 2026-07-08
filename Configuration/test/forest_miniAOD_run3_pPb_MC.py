### HiForest Configuration
# Input: miniAOD
# Type: mc
# Target: pPb, W -> mu nu (muon channel)
#
# Adapted from forest_miniAOD_run3_pO_MC.py (pO 2025).
# See the TODO(pPb) notes in forest_miniAOD_run3_pPb_DATA.py — the same
# run-dependent items apply here:
#   Era, MC global tag, input file (W->munu pPb signal, produced with the
#   correct CM boost / beam direction and an nPDF set), trigger list.

import FWCore.ParameterSet.Config as cms
# TODO(pPb): replace with the official pPb era of the production release
from Configuration.Eras.Era_Run3_2025_cff import Run3_2025
process = cms.Process('HiForest', Run3_2025)

###############################################################################

# HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 150X, mc, pPb, WToMuNu")

###############################################################################

# input files
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        # TODO(pPb): replace with a W->munu pPb signal miniAOD
        # (e.g. POWHEG WToMuNu with the pPb beam setup; check with the MC
        # contacts of the HIN EW group for the official request)
        'root://xrootd-cms.infn.it//store/CHANGE_ME_pPb_WToMuNu_MC.root'
    ),
)

# number of events to process, set to -1 to process all events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
    )

###############################################################################

# load Global Tag, geometry, etc.
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')


from Configuration.AlCa.GlobalTag import GlobalTag
# TODO(pPb): set the realistic MC GT of the pPb campaign
# (the value below is the pO 2025 one, kept only as a syntactic placeholder)
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_mcRun3_2025_forpO_realistic_v9', '')
process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

###############################################################################

# Define centrality binning
# NOTE(pPb): kept because hiMuons/hiElectrons (iso BDTs) consume
# centralityBin:HFtowers — see the note in forest_miniAOD_run3_pPb_DATA.py.
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("hiCentrality")
process.centralityBin.centralityVariable = cms.string("HFtowers")

###############################################################################

# root output
process.TFileService = cms.Service("TFileService",
    fileName = cms.string("HiForestMiniAOD.root"))

###############################################################################

#############################
# Gen Analyzer
#############################
process.load('HeavyIonsAnalysis.EventAnalysis.HiGenAnalyzer_cfi')

# event analysis
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_mc_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltobject_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.l1object_cfi')
process.metFilters = process.skimanalysis.clone(hltresults = "TriggerResults::RECO")
process.hiEvtAnalyzer.doHFfilters = False

# TODO(pPb): keep in sync with the data config trigger list
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
process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
process.ggHiNtuplizer.doGenParticles = cms.bool(True)
process.ggHiNtuplizer.genParticleSrc = "prunedGenParticles"
process.ggHiNtuplizer.doPackedGenParticle = False
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
process.load('HeavyIonsAnalysis.JetAnalysis.akCs4PFJetSequence_pponPbPb_mc_cff')
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
process.muonAnalyzer.doGen = cms.bool(True)

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
    process.HiGenParticleAna +
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
