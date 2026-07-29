### HiForest Configuration
# Input: miniAOD
# Type: mc
# System: OO 2025 (5.36 TeV NN), W/Z lepton channels
# Adapted from forest_miniAOD_run3_pO_MC.py (master) — same forest content,
# pO -> OO campaign, electron scale/smear from the 2025 pO Z->ee calibration.

import FWCore.ParameterSet.Config as cms
# Run3_2025_OXY is the oxygen-run era of the 2025 light-ion program and is the
# correct era for OO as well as pO (NeNe will need Run3_2025_NEON instead).
from Configuration.Eras.Era_Run3_2025_OXY_cff import Run3_2025_OXY
process = cms.Process('HiForest', Run3_2025_OXY)

###############################################################################

# HiForest info
process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 150X, mc, OO")

###############################################################################

# input files
# TODO(OO): point at an OO-campaign signal miniAOD (W->munu / W->enu / DY at
# 5.36 TeV with the OO beam configuration). Find campaigns with e.g.
#   dasgoclient -query="dataset dataset=/*OO*5p36*/*/MINIAODSIM"
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        'root://xrootd-cms.infn.it//store/CHANGE_ME_OO_MC_MINIAODSIM.root'
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
# TODO(OO): set the GT of the OO MC campaign you run on (the value below is
# the pO campaign GT, kept so the config stays runnable for smoke tests).
# Check candidates with:  conddb search mcRun3_2025_forOO
# or take it from the DAS config of the OO MC dataset itself.
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_mcRun3_2025_forpO_realistic_v9', '')
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

# All names verified against the OO data menu in run 394153; still confirm
# the OO MC campaign runs the same menu. First five = the pO list; Mu3/5/7,
# DoubleMu*, EG21 are W/Z additions.
process.hltobject.triggerNames = cms.vstring(
    'HLT_OxyL1SingleMu0_v',
    'HLT_OxyL1SingleMuOpen_v',
    'HLT_OxyL1SingleMu3_v',
    'HLT_OxyL1SingleMu5_v',
    'HLT_OxyL1SingleMu7_v',
    'HLT_OxyL1DoubleMu0_v',
    'HLT_OxyL1DoubleMuOpen_v',
    'HLT_OxyL1SingleEG10_v',
    'HLT_OxyL1SingleEG15_v',
    'HLT_OxyL1SingleEG21_v',
    'HLT_MinimumBiasHF_OR_BptxAND_v'
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
# 2025 pO Z->ee scale + smearing (MC): replaces the PbPb-2024 placeholder used
# in the pO production. See EGMAnalysis/data/Run3_2025_pO/README.md;
# eleRawPt in the output tree stays uncorrected regardless.
process.correctedElectrons.correctionFile = "HeavyIonsAnalysis/EGMAnalysis/data/Run3_2025_pO/SSpO2025MC.dat"
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
process.particleFlowAnalyser.ptMin = 0.0
process.ggHiNtuplizer.muonPtMin = 0.0

#########################
# Event Selection -> add the needed filters here
#########################

process.load('HeavyIonsAnalysis.EventAnalysis.collisionEventSelection_cff')
process.pclusterCompatibilityFilter = cms.Path(process.clusterCompatibilityFilter)
process.pprimaryVertexFilter = cms.Path(process.primaryVertexFilter)
process.pAna = cms.EndPath(process.skimanalysis)
