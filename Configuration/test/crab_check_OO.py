#!/usr/bin/env python3
"""Sweep all CRAB tasks in a work area: list failed jobs per PD with their
failure reasons, and optionally resubmit them.

Usage (after cmsenv + source /cvmfs/cms.cern.ch/common/crab-setup.sh + proxy):
  python3 crab_check_OO.py                      # report every task
  python3 crab_check_OO.py --resubmit           # ... and resubmit failed jobs
  python3 crab_check_OO.py --resubmit --maxmemory 3000
  python3 crab_check_OO.py --only IonPhysics7   # single stream
  python3 crab_check_OO.py --workarea crab_projects_OO

Notes:
  - Probe jobs (ids 0-*) cannot be resubmitted: if the whole probe stage
    failed, the task is dead -- submit a fresh task (bump TAG) instead.
  - With Automatic splitting, failed processing jobs are usually recovered
    by the tail jobs on their own; resubmitting mainly matters for jobs
    still 'failed' once the task is otherwise COMPLETED.
"""

import argparse
import os
from collections import Counter
from multiprocessing import Process

from CRABAPI.RawCommand import crabCommand


def task_dirs(workarea, only):
    for name in sorted(os.listdir(workarea)):
        d = os.path.join(workarea, name)
        if os.path.isdir(d) and (not only or only in name):
            yield d


def pd_of(taskdir):
    return os.path.basename(taskdir).split('_')[-1]


def report(taskdir):
    """Print a summary for one task; return the number of failed non-probe jobs."""
    try:
        res = crabCommand('status', dir=taskdir)
    except Exception as exc:
        print('  could not fetch status: %s' % exc)
        return 0

    print('  scheduler status: %s' % res.get('status', 'unknown'))
    per = res.get('jobsPerStatus', {})
    if per:
        print('  jobs: ' + ', '.join('%s %d' % (k, v) for k, v in sorted(per.items())))

    jobs = res.get('jobs', {})
    failed = {jid: info for jid, info in jobs.items() if info.get('State') == 'failed'}
    probe_failed = sorted(j for j in failed if j.startswith('0-'))
    regular_failed = sorted(j for j in failed if not j.startswith('0-'))

    if regular_failed:
        print('  failed jobs: %s' % ', '.join(regular_failed))
        reasons = Counter()
        for jid in regular_failed:
            err = failed[jid].get('Error') or ('?', 'no error info recorded')
            code, msg = err[0], str(err[1]).splitlines()[0]
            reasons[(code, msg)] += 1
        for (code, msg), n in reasons.most_common():
            print('    [%s] x%d  %s' % (code, n, msg))
    if probe_failed:
        print('  PROBE failures (%s): not resubmittable; if the whole probe '
              'stage failed, submit a fresh task (bump TAG)' % ', '.join(probe_failed))
    if not failed:
        print('  no failed jobs')
    return len(regular_failed)


def resubmit(taskdir, options):
    kwargs = {k: v for k, v in options.items() if v}
    print('>>> crab resubmit %s %s' % (taskdir, kwargs or ''))
    crabCommand('resubmit', dir=taskdir, **kwargs)


def main():
    ap = argparse.ArgumentParser(
        description='Report (and optionally resubmit) failed jobs of every CRAB task in a work area.')
    ap.add_argument('--workarea', default='crab_projects_OO')
    ap.add_argument('--only', default='',
                    help='substring filter on the task dir name (e.g. IonPhysics7)')
    ap.add_argument('--resubmit', action='store_true',
                    help='resubmit every task that has failed non-probe jobs')
    ap.add_argument('--maxmemory', default='',
                    help='override the memory request (MB) on resubmit')
    ap.add_argument('--maxjobruntime', default='',
                    help='override the wall-time request (min) on resubmit')
    args = ap.parse_args()

    to_resubmit = []
    for d in task_dirs(args.workarea, args.only):
        print('=== %s  (%s) ===' % (pd_of(d), os.path.basename(d)))
        if report(d):
            to_resubmit.append(d)

    if not to_resubmit:
        print('\nnothing to resubmit')
        return
    print('\ntasks with failed (non-probe) jobs: %s' % ', '.join(pd_of(d) for d in to_resubmit))
    if not args.resubmit:
        print('run again with --resubmit to resubmit them')
        return

    opts = {'maxmemory': args.maxmemory, 'maxjobruntime': args.maxjobruntime}
    # one process per resubmission: CRABClient keeps global state and
    # misbehaves when several state-changing commands share an interpreter
    for d in to_resubmit:
        p = Process(target=resubmit, args=(d, opts))
        p.start()
        p.join()


if __name__ == '__main__':
    main()
