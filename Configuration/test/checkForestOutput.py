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

TREES = [
    'HiForestInfo/HiForest',
    'hiEvtAnalyzer/HiTree',
    'hltanalysis/HltTree',
    'skimanalysis/HltTree',
    'particleFlowAnalyser/pftree',
    'muonAnalyzer/MuonTree',
    'ggHiNtuplizer/EventTree',
]

TRIG_PREFIXES = [
    'HLT_OxyL1SingleMu0_v',
    'HLT_OxyL1SingleMuOpen_v',
    'HLT_OxyL1SingleEG10_v',
    'HLT_OxyL1SingleEG15_v',
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
        tag = 'OK' if 394153 <= run <= 394217 else 'NOT an OO run?!'
        print('=== first stored run: %d (OO: 394153-394217) %s ===' % (run, tag))

    hlt = f.Get('hltanalysis/HltTree')
    if hlt:
        print('=== trigger bits (accepted / stored events) ===')
        branches = [b.GetName() for b in hlt.GetListOfBranches()]
        for pre in TRIG_PREFIXES:
            hits = [b for b in branches if b.startswith(pre) and not b.endswith('Prescl')]
            if not hits:
                print('  %-35s no branch found' % pre)
            for b in hits:
                n = hlt.Draw(b, '%s==1' % b, 'goff')
                print('  %-35s %d / %d' % (b, n, hlt.GetEntries()))

    gg = f.Get('ggHiNtuplizer/EventTree')
    if gg:
        print('=== electron pT calibration (corrected/raw, rawPt>20) ===')
        for region, cut, expect in [('EB', 'abs(eleSCEta)<1.4442', '~1.021 data / ~0.997 MC'),
                                    ('EE', 'abs(eleSCEta)>=1.4442', '~1.087 data / ~0.993 MC')]:
            n = gg.Draw('elePt/eleRawPt', 'eleRawPt>20 && ' + cut, 'goff')
            if n > 0:
                mean = sum(gg.GetV1()[i] for i in range(n)) / n
                print('  %s: n=%d  mean=%.4f  (expect %s)' % (region, n, mean, expect))
            else:
                print('  %s: no electrons with rawPt>20 — raise maxEvents in the test config' % region)


if __name__ == '__main__':
    main()
