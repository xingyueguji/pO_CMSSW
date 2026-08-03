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

# likely cause / recommended action per exit code (CMSSW 8xxx, grid 5xxxx/6xxxx)
KNOWN_CAUSES = {
    8001: 'CMSSW exception -- inspect stderr (crab getlog) before resubmitting',
    8002: 'std::exception in cmsRun -- inspect stderr before resubmitting',
    8004: 'cmsRun killed by signal -- bad node or corrupt read; resubmit is usually fine',
    8020: 'input file open failed -- transient storage/xrootd; resubmit',
    8021: 'input file read error -- transient xrootd; resubmit',
    8028: 'file open failed via AAA fallback -- transient storage; resubmit',
    8901: 'job terminated unexpectedly (node death/preemption) -- transient; resubmit',
    50513: 'worker-node environment/scram setup failure -- transient site issue; resubmit',
    50660: 'memory kill (RSS over request) -- resubmit with --maxmemory raised',
    50662: 'excessive disk usage on the worker node',
    50664: 'wall-time limit hit -- resubmit with --maxjobruntime raised',
    50665: 'killed by the site batch system -- often preemption; resubmit',
    60302: 'output missing at stageout -- job usually died earlier; check stderr',
    60303: 'output already exists at destination -- stale earlier transfer; may need cleanup',
    60307: 'stageout/transfer failed -- check destination quota/permissions; resubmit',
    60311: 'local stageout failure at the site -- transient; resubmit',
    60403: 'transfer timeout -- transient; resubmit',
}


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
            try:
                cause = KNOWN_CAUSES.get(int(code), '')
            except (TypeError, ValueError):
                cause = ''
            print('    [%s] x%d  %s' % (code, n, msg))
            print('          -> %s' % (cause or 'unknown cause: crab getlog -d %s --jobids <id>' % taskdir))
    if probe_failed:
        print('  PROBE failures (%s): not resubmittable; if the whole probe '
              'stage failed, submit a fresh task (bump TAG)' % ', '.join(probe_failed))
    if not failed:
        print('  no failed jobs')
    return len(regular_failed)


def resubmit(taskdir, options):
    kwargs = {k: v for k, v in options.items() if v}
    print('>>> crab resubmit %s %s' % (taskdir, kwargs or ''))
    try:
        crabCommand('resubmit', dir=taskdir, **kwargs)
    except Exception as exc:
        if 'no jobs to resubmit' in str(exc).lower():
            # Automatic splitting: failed MAIN-stage jobs are recovered by
            # the tail jobs on their own and are not resubmittable -- this
            # is fine, nothing is lost. Check again once the task is
            # COMPLETED; only then are leftover failures actionable.
            print('    nothing resubmittable: the failures are main-stage jobs')
            print('    already covered by automatic tail-job recovery -- OK')
        else:
            print('    resubmit failed: %s' % exc)


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
