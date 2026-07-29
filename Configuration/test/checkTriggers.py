#!/usr/bin/env python3
"""Trigger-name check for the OO forest configs.

Lists the HLT paths present in a data file and verifies that every name in
hltobject.triggerNames (prefix-matched, '_v') exists in the menu.

Usage (after cmsenv; needs a voms proxy for root:// files):
  python3 checkTriggers.py <miniAOD file (local path or root://... LFN)>

Exit code 0 = all configured names match a path in the file.
"""
import sys

from DataFormats.FWLite import Events, Handle

# keep in sync with hltobject.triggerNames in forest_miniAOD_run3_OO_DATA.py
WANTED = [
    'HLT_OxyL1SingleMu0_v',
    'HLT_OxyL1SingleMuOpen_v',
    'HLT_OxyL1SingleEG10_v',
    'HLT_OxyL1SingleEG15_v',
    'HLT_MinimumBiasHF_OR_BptxAND_v',
]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    print('opening %s\n  (a remote open takes O(1 min); a silent hang beyond that '
          'usually means no valid voms proxy)' % sys.argv[1], flush=True)
    events = Events(sys.argv[1])
    print('file open, reading first event...', flush=True)
    handle = Handle('edm::TriggerResults')
    paths = None
    for ev in events:
        ev.getByLabel(('TriggerResults', '', 'HLT'), handle)
        names = ev.object().triggerNames(handle.product())
        # cppyy returns std::string objects; str() them for join/startswith
        paths = sorted(str(p) for p in names.triggerNames())
        break
    if paths is None:
        sys.exit('no events in file')

    print('=== %d HLT paths in file; muon/EG/MinBias-like ones: ===' % len(paths))
    for p in paths:
        if any(k in p for k in ('Mu', 'EG', 'Ele', 'MinimumBias')):
            print('   ', p)

    print('=== hltobject.triggerNames check (prefix match) ===')
    ok = True
    for w in WANTED:
        matches = [p for p in paths if p.startswith(w)]
        if matches:
            print('  %-35s OK -> %s' % (w, ', '.join(matches)))
        else:
            print('  %-35s MISSING from menu' % w)
            ok = False
    if not ok:
        print('some names missing: fix hltobject.triggerNames before submitting')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
