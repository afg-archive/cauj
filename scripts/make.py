import os
import glob
import json
from cauj import sha1file, TestCase


def main():
    testcases = list(map(TestCase, glob.iglob('testcases/*/*')))

    assert len(testcases) == 75, 'There should be 75 testcases (iLMS #122210)'
    # http://lms.nthu.edu.tw/course.php?courseID=24831&f=forum&tid=122210

    data = {}

    for testcase in testcases:
        assert testcase.name not in data, 'duplicate testcase %r' % testcase.name
        data[testcase.name] = {
            'directory': testcase.directory,
            'sha1sums': testcase.get_sha1_checksums(),
        }

    with open('testcases.json', mode='w') as file:
        json.dump(data, file, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
