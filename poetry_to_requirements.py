import argparse
import subprocess
from typing import Optional
from typing import Sequence
import os

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        'Convert Poetry to requirements.txt',
    )

    check_cmd = ['poetry', 'export', '--dev', '--without-hashes']
    build_cmd = ['poetry', 'export', '--dev', '--output', 'atlas/requirements.txt', '--without-hashes']

    # check current file
    proc = subprocess.run(check_cmd, capture_output=True)

    stdout = proc.stdout.decode()

    retcode = 0

    if not os.path.isfile("atlas/requirements.txt") or (os.path.isfile("atlas/requirements.txt") and open("atlas/requirements.txt", "r").read() != stdout):
        subprocess.run(build_cmd, capture_output=True)
        print('created new requirements.txt file')
        retcode = 1
    return retcode


if __name__ == '__main__':
    exit(main())