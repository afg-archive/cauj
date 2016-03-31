# cauj
Computer Architecture Project 1 Unofficial Judge (& Time Measurement Tool)

## Requirements

* python 3.4 or later

## Usage

Clone this repo and then:
`./cauj.py path/to/single_cycle`

or at the project directory:
`path/to/cauj.py single_cycle`

type `./cauj.py --help` for more options, or see below

## Options

`--mute` disables executable's stdout and stderr.

`--diff` show diff when the output is incorrect.

`--diff N` show diff when the output is incorrect, but limit diff's output to N lines.

`--timeout SECONDS` time limit on each testcase, defaults to 5.

`--repeat` repeat each testcase N times. defaults to 1.

`--avg` use average execution time for a testcase when a testcase is run multiple times.

`--min` use minimum execution time for a testcase when a testcase is run multiple times.

`--max` use maximum execution time for a testcase when a testcase is run multiple times.

## Typical output

```
75 testcases found
...
...
=== (74/75) 103070038_01 ======================================================
Running /home/afg/simulator/single_cycle
-> user returned 0 in 0.003964 seconds
-> snapshot.rpt   OK
-> error_dump.rpt OK
=== (75/75) fd03357293_01 =====================================================
Running /home/afg/simulator/single_cycle
-> user returned 0 in 0.0043 seconds
=> snapshot.rpt   Differ
-> error_dump.rpt OK
=== SUMMARY ===================================================================
45/75 testcases passed
Total time of passed tests: 1.9783899784088135
Errored:
103062108_01 103062114_01 103062214_01 103062372_01
Failed:
multiply seq 102065512_01 102070021_01 102070028_01 102081005_01 103000099_01 (... ommitted)
```
