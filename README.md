# cauj
Computer Architecture Project 1 Unofficial Judge

Usage:
`./cauj.py path/to/single_cycle`

or at the project directory:
`path/to/cauj.py single_cycle`

type `./cauj.py --help` for more options

The automatic diff may take a lot of time. Use `--limit-diff 0` to disable diff.

Typical output

```
...
...
...
================================= 103070038_01 ================================
Running /home/afg/projects/cauj/vendor/single_cycle
-> gold returned 0 in 0.001803 seconds
Running /home/afg/simulator/single_cycle
-> user returned 0 in 0.003964 seconds
-> snapshot.rpt   OK
-> error_dump.rpt OK
================================ fd03357293_01 ================================
Running /home/afg/projects/cauj/vendor/single_cycle
-> gold returned 1 in 0.004046 seconds
Running /home/afg/simulator/single_cycle
-> user returned 0 in 0.0043 seconds
=> snapshot.rpt   Differ
-> error_dump.rpt OK
=================================== SUMMARY ===================================
45/68 testcases passed
Total time of passed tests: 1.9783899784088135
Errored:
103062108_01 103062114_01 103062214_01 103062372_01
Failed:
multiply seq 102065512_01 102070021_01 102070028_01 102081005_01 103000099_01 103060007_01 103060011_01 103062143_01 103062173_01 103062224_01 103062310_01 103062318_01 103062327_01 103062331_01 103062391_01 103070021_01 fd03357293_01
```
