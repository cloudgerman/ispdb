import argparse
import re

from .version import __version__


def email(txt: str) -> str:
    # thanks to the Django team!
    # Taken from: https://github.com/django/django/blob/main/django/core/validators.py
    if not txt or "@" not in txt or len(txt) > 320:
        raise ValueError

    user_part, domain_part = txt.rsplit("@", 1)

    user_regex = re.compile(
        # dot-atom
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])'
        r'*"\Z)',
        re.IGNORECASE,
    )
    if not user_regex.match(user_part):
        raise ValueError

    domain_regex = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r"((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z",
        re.IGNORECASE,
    )
    if not domain_regex.match(domain_part):
        raise ValueError
    return txt


def parse(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ispdb",
        description="query the ISPDB",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s version {__version__}",
        help="shows the version and exit",
    )
    parser.add_argument("email", type=email, help="email to query")

    action = parser.add_mutually_exclusive_group(required=False)
    action.add_argument("-d", "--debug", action="store_true")
    action.add_argument("-s", "--silent", action="store_true")

    parser.add_argument("--no-https", action="store_true")
    parser.add_argument("--no-http", action="store_true")
    parser.add_argument("--no-dns", action="store_true")
    args = parser.parse_args(argv)
    return args
