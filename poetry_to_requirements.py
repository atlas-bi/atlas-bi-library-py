import argparse
import subprocess
from typing import Optional
from typing import Sequence
import os

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        'Convert Poetry to requirements.txt',
    )

    check_cmd = ('poetry', 'export', '--without-hashes')
    build_cmd = ('poetry', 'export', '--output', 'atlas/requirements.txt', '--without-hashes')

    # check current file
    proc = subprocess.Popen(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()

    stdout = stdout.decode()

    retcode = 0

    if not os.path.isfile("atlas/requirements.txt") or (os.path.isfile("atlas/requirements.txt") and open("atlas/requirements.txt", "r").read() != stdout):
        subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('created new requirements.txt file')
        retcode = 1
    return retcode


if __name__ == '__main__':
    exit(main())