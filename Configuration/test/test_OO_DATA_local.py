# Local smoke test for the OO data forest: imports the CRAB pset unchanged,
# then limits events and (optionally) overrides the input file — so the real
# config never needs test edits.
#
#   cmsRun test_OO_DATA_local.py
#   python3 checkForestOutput.py HiForestMiniAOD.root

import FWCore.ParameterSet.Config as cms

from forest_miniAOD_run3_OO_DATA import process

# enough events that a few pass the >=1 lepton superfilter and populate the
# electron calibration check; raise if checkForestOutput reports no electrons
process.maxEvents.input = 10000

# uncomment to test on a locally copied file instead of the one in the config:
# process.source.fileNames = cms.untracked.vstring('file:/tmp/OO_test.root')
