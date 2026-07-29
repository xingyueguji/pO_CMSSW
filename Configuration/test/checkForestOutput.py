#!/usr/bin/env python3
"""Sanity checks on a locally produced OO forest (HiForestMiniAOD.root).

Usage: python3 checkForestOutput.py [HiForestMiniAOD.root]

Checks: expected trees exist and are filled; stored runs are OO runs;
the HLT_Oxy* bits fire; the pO Z->ee electron pT calibration was applied
(data: elePt/eleRawPt ~ 1.021 in EB, ~ 1.087 in EE; on MC expect ~0.997 EB
/ ~0.993 EE with visible smearing spread instead).
"""
import sys

import ROOT

# Expected structure, cross-checked against the pO production output
# (pO_2025.root). Intentionally absent vs a naive reading of the config:
# muonAnalyzer/MuonTree (loaded, never scheduled — muons are in
# ggHiNtuplizer/EventTree via hiMuons), jet trees (only the rho analyzer is
# scheduled), track trees (unpackedTracksAndVertices is a producer only).
# metFilters/HltTree can have far fewer entries than the event trees (also
# true in the pO reference file).
TREES = [
    'HiForestInfo/HiForest',
    'hiEvtAnalyzer/HiTree',
    'hltanalysis/HltTree',
    'l1object/L1UpgradeFlatTree',
    'skimanalysis/HltTree',
    'metFilters/HltTree',
    'particleFlowAnalyser/pftree',
    'hiFJRhoAnalyzerFinerBins/t',
    'ggHiNtuplizer/EventTree',
]

TRIG_PREFIXES = [
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
    'HLT_MinimumBiasHF_OR_BptxAND_v',
]


def main():
    fname = sys.argv[1] if len(sys.argv) > 1 else 'HiForestMiniAOD.root'
    f = ROOT.TFile.Open(fname)
    if not f or f.IsZombie():
        sys.exit('cannot open ' + fname)

    print('=== trees ===')
    for name in TREES:
        t = f.Get(name)
        print('  %-32s %s' % (name, 'MISSING' if not t else '%d entries' % t.GetEntries()))

    evt = f.Get('hiEvtAnalyzer/HiTree')
    if evt and evt.GetEntries():
        evt.GetEntry(0)
        run = int(evt.run)
        # the OORun2025 dataset also contains earlier, uncertified runs
        # (e.g. 394075); CRAB's golden-JSON lumimask drops those
        tag = ('in golden-JSON range' if 394153 <= run <= 394217 else
               'OUTSIDE golden range — OK for a smoke test, excluded in production')
        print('=== first stored run: %d — %s ===' % (run, tag))

    print('=== hltobject trees (one per configured path) ===')
    for pre in TRIG_PREFIXES:
        t = f.Get('hltobject/' + pre)
        print('  hltobject/%-33s %s' % (pre, 'MISSING' if not t else '%d entries' % t.GetEntries()))

    hlt = f.Get('hltanalysis/HltTree')
    if hlt:
        print('=== trigger bits (accepted / stored events) ===')
        branches = [b.GetName() for b in hlt.GetListOfBranches()]
        for pre in TRIG_PREFIXES:
            hits = [b for b in branches if b.startswith(pre) and 'Prescale' not in b]
            if not hits:
                print('  %-35s no branch found' % pre)
            for b in hits:
                n = hlt.Draw(b, '%s==1' % b, 'goff')
                print('  %-35s %d / %d' % (b, n, hlt.GetEntries()))

    gg = f.Get('ggHiNtuplizer/EventTree')
    if gg and gg.GetEntries():
        print('=== lepton content (ggHiNtuplizer) ===')
        print('  events with >=1 electron: %d / %d' % (gg.Draw('nEle', 'nEle>=1', 'goff'), gg.GetEntries()))
        print('  events with >=1 muon:     %d / %d' % (gg.Draw('nMu', 'nMu>=1', 'goff'), gg.GetEntries()))
    if gg:
        print('=== electron pT calibration (corrected/raw, rawPt>20) ===')
        for region, cut, expect in [('EB', 'abs(eleSCEta)<1.4442', '~1.021 data / ~0.997 MC'),
                                    ('EE', 'abs(eleSCEta)>=1.4442', '~1.087 data / ~0.993 MC')]:
            n = gg.Draw('elePt/eleRawPt', 'eleRawPt>20 && ' + cut, 'goff')
            if n > 0:
                mean = sum(gg.GetV1()[i] for i in range(n)) / n
                print('  %s: n=%d  mean=%.4f  (expect %s)' % (region, n, mean, expect))
                continue
            # low-pT fallback: only meaningful for the local test wrapper,
            # which lowers correctedElectrons.minPt to 5. Qualitative check:
            # at low pT the E-p combination dilutes the pure ECAL scale, so
            # expect a ratio between 1 and the nominal scale; != 1 proves
            # the .dat numbers are applied.
            n = gg.Draw('elePt/eleRawPt', 'eleRawPt>5 && eleRawPt<20 && ' + cut, 'goff')
            if n > 0:
                mean = sum(gg.GetV1()[i] for i in range(n)) / n
                print('  %s: no electrons with rawPt>20; low-pT fallback (5-20): '
                      'n=%d  mean=%.4f  (qualitative — expect between 1 and %s)'
                      % (region, n, mean, expect))
            else:
                print('  %s: no electrons above 5 GeV either — raise maxEvents' % region)


if __name__ == '__main__':
    main()
