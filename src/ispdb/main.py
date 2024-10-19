"""
ISPDB is the Generic database of mail server configuration, maintained by the
Thunderbird project
See: https://github.com/thunderbird/autoconfig for details
"""

import argparse
import sys
from typing import Callable, Iterable, TextIO

from . import args, configure, lookups


def main(
    argv: list[str] | None = None,
    # for testing
    stdout: TextIO = sys.stdout,
    protocols: Callable[[argparse.Namespace], list[str]] = lookups.protocols,
    pipeline: Callable[[str, list[str]], Iterable[lookups.Lookup]] = lookups.pipeline,
) -> int:
    params = args.parse(argv)
    configure.logs(params)
    prot = protocols(params)
    try:
        for lookup in pipeline(params.email, prot):
            res = lookup.query()
            if res and not params.silent:
                print(res, file=stdout)
    except Exception as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    ret = main()
    exit(ret)
