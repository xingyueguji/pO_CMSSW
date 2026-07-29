# Local smoke test for the OO data forest: imports the CRAB pset unchanged,
# then limits events and (optionally) overrides the input file — so the real
# config never needs test edits.
#
#   cmsRun test_OO_DATA_local.py
#   python3 checkForestOutput.py HiForestMiniAOD.root

import FWCore.ParameterSet.Config as cms

from forest_miniAOD_run3_OO_DATA import process

process.maxEvents.input = 10000

# A >=15 GeV lepton is rare enough that 10k events can yield zero stored
# events. For the smoke test, drop the lepton-count requirement (vertex and
# cluster-compatibility filters stay active) so the trees fill; the CRAB
# production uses forest_miniAOD_run3_OO_DATA.py directly and keeps the full
# W/Z pre-selection.
process.oneLepton.minNumber = cms.uint32(0)

# Electrons above 20 GeV are too rare in a short unselected run to exercise
# the pT calibration numerically, and the corrector skips electrons below its
# minPt (20 GeV, the production default). Lower it here so the plentiful soft
# electrons get corrected and checkForestOutput's low-pT fallback can verify
# the .dat numbers flow through. Local test only — production keeps 20.
process.correctedElectrons.minPt = 5.0

# uncomment to test on a locally copied file instead of the one in the config:
# process.source.fileNames = cms.untracked.vstring('file:/tmp/OO_test.root')
