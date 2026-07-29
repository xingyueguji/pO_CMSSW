#!/usr/bin/env python3
# Submit the OO 2025 data HiForest over all IonPhysics streams.
#
# The IonPhysics streams are event-split (round-robin), so W/Z events are
# spread across all of them — every stream must be processed.
#
# Usage (lxplus, after cmsenv + voms-proxy-init -voms cms
#        + source /cvmfs/cms.cern.ch/common/crab-setup.sh):
#   python3 multicrab_OO_DATA.py            # submit all streams
#   python3 multicrab_OO_DATA.py status     # crab status of all submitted tasks
#
# Edit N_STREAMS after checking DAS:
#   dasgoclient -query="dataset dataset=/IonPhysics*/OORun2025*/MINIAOD"

import os
import sys
from multiprocessing import Process

from CRABAPI.RawCommand import crabCommand

N_STREAMS = 8   # TODO(OO): set to the actual number of IonPhysics streams
RECO_TAG = 'OORun2025-PromptReco-v1'


def submit(stream):
    import crabConfig_forest_OO_DATA as base
    cfg = base.config
    dataset = '/IonPhysics%d/%s/MINIAOD' % (stream, RECO_TAG)
    cfg.Data.inputDataset = dataset
    cfg.General.requestName = base.TAG + '_' + dataset.split('/')[1]
    print('>>> submitting', dataset)
    crabCommand('submit', config=cfg)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        work_area = 'crab_projects_OO'
        for d in sorted(os.listdir(work_area)):
            crabCommand('status', dir=os.path.join(work_area, d))
        return

    # each submission in its own process: CRABClient keeps global state and
    # misbehaves when submitting several configs from one interpreter
    for stream in range(N_STREAMS):
        p = Process(target=submit, args=(stream,))
        p.start()
        p.join()


if __name__ == '__main__':
    main()
