#!/usr/bin/env python3

import argparse
import difflib
import filecmp
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
import time
import statistics
import json
import hashlib


basedir = os.path.abspath(os.path.dirname(__file__))


class TestCaseError(Exception):
    pass

class ExecutionError(Exception):
    pass


class TestCase:

    def __init__(self, directory):
        self.directory = directory
        self.iimage = os.path.abspath(os.path.join(self.directory, 'iimage.bin'))
        self.dimage = os.path.abspath(os.path.join(self.directory, 'dimage.bin'))
        self.errordump = os.path.abspath(os.path.join(self.directory, 'error_dump.rpt.gold'))
        self.snapshot = os.path.abspath(os.path.join(self.directory, 'snapshot.rpt.gold'))
        self.name = os.path.basename(directory.rstrip('/'))
        self.check()

    @staticmethod
    def _check(path):
        if not os.path.exists(path):
            raise TestCaseError('{!r} does not exist'.format(path))

    def check(self):
        self._check(self.iimage)
        self._check(self.dimage)
        self._check(self.errordump)
        self._check(self.snapshot)

    def get_sha1_checksums(self):
        return {
            'iimage.bin': sha1file(self.iimage),
            'dimage.bin': sha1file(self.dimage),
            'snapshot.rpt.gold': sha1file(self.snapshot),
            'error_dump.rpt.gold': sha1file(self.errordump),
        }

    @classmethod
    def from_metadata(cls, metadata):
        self = cls(os.path.join(basedir, metadata['directory']))
        checksums = self.get_sha1_checksums()
        for name, value in metadata['sha1sums'].items():
            if checksums[name] != value:
                raise TestCaseError("TestCase {!s}'s {!s} is corrupted".format(
                    self.name,
                    name
                ))
        return self

    def __repr__(self):
        return '<TestCase {!r}>'.format(self.directory)


class Simulator:

    def __init__(self, executable, name):
        self.executable = os.path.abspath(executable)
        self.name = name

    def __repr__(self):
        return '<Simulator {} at {!r}>'.format(self.name, self.executable)


class Execution:

    def __init__(self, simulator, testcase, timeout=5, mute=False):
        self.simulator = simulator
        self.testcase = testcase
        self.timeout = timeout
        self.snapshot = None
        self.error_dump = None
        self.execution_time = None
        self.exitcode = None
        self.mute = mute

    @staticmethod
    def writeback(srcdir, dstdir, name, rename):
        try:
            shutil.copy(os.path.join(srcdir, name), os.path.join(dstdir, rename))
        except FileNotFoundError:
            raise ExecutionError('The simulator did not generate {!r}'.format(name))

    def run(self):
        print('Running {}'.format(self.simulator.executable))
        with tempfile.TemporaryDirectory() as tempdir:
            shutil.copy(self.testcase.dimage, tempdir)
            shutil.copy(self.testcase.iimage, tempdir)
            start_time = time.time()
            sys.stdout.flush()
            try:
                self.exitcode = subprocess.call(
                    [self.simulator.executable],
                    cwd=tempdir,
                    timeout=self.timeout,
                    stdout=subprocess.DEVNULL if self.mute else None,
                    stderr=subprocess.DEVNULL if self.mute else None,
                )
            except subprocess.TimeoutExpired:
                raise ExecutionError('Timed out ({} seconds)'.format(self.timeout))
            sys.stdout.flush()
            end_time = time.time()
            self.execution_time = end_time - start_time
            self.writeback(
                tempdir,
                self.testcase.directory,
                'snapshot.rpt',
                'snapshot.rpt.{}'.format(self.simulator.name),
            )
            self.writeback(
                tempdir,
                self.testcase.directory,
                'error_dump.rpt',
                'error_dump.rpt.{}'.format(self.simulator.name)
            )
            print('-> {} returned {} in {:.4g} seconds'.format(
                self.simulator.name,
                self.exitcode,
                self.execution_time,
                )
            )


def diffprint(line):
    if line.startswith('+'):
        print(end='\033[0;32m')
    elif line.startswith('-'):
        print(end='\033[0;31m')
    elif line.startswith('@@'):
        print(end='\033[0;36m')
    try:
        print(end=line)
    finally:
        print(end='\033[0;0m')


def udiff(fromfile, tofile, limit_lines):
    with open(fromfile) as ff, open(tofile) as tf:
        diff = difflib.unified_diff(
            list(ff),
            list(tf),
            fromfile=fromfile,
            tofile=tofile
        )
        for line in itertools.islice(diff, None, limit_lines):
            diffprint(line)


def sha1file(filename):
    with open(filename, mode='rb') as file:
        return hashlib.sha1(file.read()).hexdigest()


def compare_and_diff(prefix, limit_lines):
    fromfile = prefix + '.gold'
    tofile = prefix + '.user'
    same = filecmp.cmp(fromfile, tofile, shallow=False)
    if same:
        print('-> {:14} OK'.format(os.path.basename(prefix)))
        return True
    else:
        print('=> {:14} Differ'.format(os.path.basename(prefix)))
        if limit_lines != 0:
            udiff(fromfile, tofile, limit_lines)
        return False


def main(executable, limit_diff, mute, repeat, reduce, timeout, these):
    with open(os.path.join(basedir, 'testcases.json')) as file:
        testcase_dict = json.load(file)
    if these:
        try:
            tcproducer = [testcase_dict[name] for name in these]
        except KeyError as e:
            raise SystemExit('Error: unknown testcase {!r}'.format(e.args[0]))
    else:
        tcproducer = testcase_dict.values()
    testcases = [TestCase.from_metadata(md) for md in tcproducer]
    print(len(testcases), 'testcases found')
    total_time = 0
    passed_count = 0
    failed = []
    errored = []
    for testcase in testcases:
        print(' {} '.format(testcase.name).center(79, '='))
        user = Simulator(executable, 'user')
        times = []
        for i in range(repeat):
            execution = Execution(user, testcase, mute=mute, timeout=timeout)
            try:
                execution.run()
            except ExecutionError as e:
                print('=>', e.args[0])
                errored.append(testcase.name)
                break
            snapshot_eq = compare_and_diff(
                os.path.join(testcase.directory, 'snapshot.rpt'),
                limit_diff
            )
            error_eq = compare_and_diff(
                os.path.join(testcase.directory, 'error_dump.rpt'),
                limit_diff
            )
            if not snapshot_eq or not error_eq:
                failed.append(testcase.name)
                break
            times.append(execution.execution_time)
        else:
            passed_count += 1
            total_time += reduce(times)
    print(' SUMMARY '.center(79, '='))
    print('{}/{} testcases passed'.format(passed_count, len(testcases)))
    print('Total time of passed tests:', total_time)
    if errored:
        print('Errored:')
        print(*errored)
    if failed:
        print('Failed:')
        print(*failed)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(
        description='Computer Architecture Project 1 Unofficial Judge'
    )
    parser.add_argument('executable', help='path to single_cycle executable')
    parser.add_argument(
        'testcases',
        metavar='TESTCASE',
        nargs='*',
        help='testcases to run. defaults to all testcases if not specified',
    )
    parser.add_argument(
        '--mute',
        action='store_true',
        help="don't show executable's stdout and stderr.",
    )
    parser.add_argument(
        '--diff',
        metavar='N',
        nargs='?',
        help=(
            'show diff output when the output is incorrect. '
            'optional: limit diff output to N lines, '
            'if N is not provided, the output is unlimited.'
        ),
        type=int,
        default=0,
        const=None,
    )
    parser.add_argument(
        '--timeout',
        metavar='SECONDS',
        help='time limit on each test case',
        type=float,
        default=5,
    )
    parser.add_argument(
        '--repeat',
        metavar='N',
        type=int,
        default=1,
        help='repeat the same testcase N times, defaults to 1.'
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--avg',
        action='store_const',
        dest='reduce',
        const=statistics.mean,
        default=statistics.mean,
        help='use average execution time for the same testcase '
            'when a testcase is run multiple times. '
            'this is the default.',
    )
    group.add_argument(
        '--min',
        action='store_const',
        dest='reduce',
        const=min,
        help='use minimum execution time for the same testcase.',
    )
    group.add_argument(
        '--max',
        action='store_const',
        dest='reduce',
        const=max,
        help='use maximum execution time for the same testcase.',
    )

    args = parser.parse_args()
    main(
        args.executable,
        args.diff,
        args.mute,
        args.repeat,
        args.reduce,
        args.timeout,
        args.testcases
    )
